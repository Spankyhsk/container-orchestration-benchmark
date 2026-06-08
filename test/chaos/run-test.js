import path from "path";
import fs from "fs";
import { spawn } from "child_process";
import { fileURLToPath } from "url";

import { waitForIdle } from "../load/shared/helpers/waitForIdle.js";
import { cleanup } from "./shared/lifecycle/cleanup.js";
import { cleanupChaos } from "./core/cleanup.js";

import { runScenario } from "./core/scenario-runner.js";
import { createUsers } from "./shared/lifecycle/create-users.js";
import { API } from "./shared/api/node-api.js";
import { setSSHConfig } from "./core/remote-executer.js";
import { waitForStableRecovery } from "./shared/lifecycle/waitForRecovery.js";
import { sleep } from "./shared/helpers/sleep.js";
import { waitForProcess } from "./shared/helpers/waitForProcess.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, "..", "..");

// =========================
// TIMEOUT CONFIG
// =========================
const CHAOS_TIMEOUT_MS = 690000; // 11 min 30 sec

function timeout(ms) {
    return new Promise((_, reject) =>
        setTimeout(() => reject(new Error("CHAOS TIMEOUT REACHED")), ms)
    );
}

async function run() {
    const scenarioName = process.argv[2];
    const envType = process.argv[3];
    const failureClass = process.argv[4];
    const runId = process.argv[5] || "0";

    if (!failureClass || !envType || !scenarioName) {
        throw new Error("Usage: node run-test.js <test> <env> <scenario> <runId>");
    }

    console.log(`CHAOS RUN: ${scenarioName}`);

    let api;
    let k6Process;

    let startTime = null;
    let endTime = null;

    try {
        // -------------------------
        // ENV LOAD
        // -------------------------
        const envFile = path.join(
            ROOT,
            envType === "k3s" ? ".env.k3s" : ".env.docker"
        );

        fs.readFileSync(envFile, "utf8")
            .split("\n")
            .forEach(line => {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith("#")) return;

                const idx = trimmed.indexOf("=");
                if (idx === -1) return;

                process.env[trimmed.slice(0, idx)] =
                    trimmed.slice(idx + 1);
            });

        api = API(process.env.BASE_URL);

        setSSHConfig({
            host: process.env.SSH_HOST,
            user: process.env.SSH_USER
        });

        const testFile = path.join(ROOT, "test/chaos/k6/load-test.js");

        const scenarioPath = path.join(
            ROOT,
            "test/chaos/scenarios",
            `${failureClass}`,
            `${scenarioName}.json`
        );

        const scenario = JSON.parse(fs.readFileSync(scenarioPath, "utf8"));

        const resultDir = path.join(
            ROOT,
            "results",
            envType,
            "chaos",
            scenarioName,
            failureClass
        );

        fs.mkdirSync(resultDir, { recursive: true });

        const resultFile = path.join(resultDir, `${failureClass}_${runId}`);

        // -------------------------
        // USERS
        // -------------------------
        const users = await createUsers({ api, count: 50 });

        const userFile = path.join(ROOT, "test/chaos/k6/users.json");
        fs.writeFileSync(userFile, JSON.stringify(users, null, 2));

        // -------------------------
        // RECOVERY TARGETS
        // -------------------------
        const services = Array.isArray(scenario.target.service)
            ? scenario.target.service
            : [scenario.target.service];

        const targetMap = {
            "api": () => api.health(),
            "ai-api": () => api.ai?.health?.(),
            "check-api": () => ({ status: 200 })
        };

        const recoveryTargets = services.map(t => ({
            name: t,
            check: targetMap[t]
        }));

        await waitForIdle({ api });

        // =========================
        // PIPELINE
        // =========================
        const pipeline = (async () => {

            console.log("Starting k6...");

            k6Process = spawn("k6", [
                "run",
                testFile,
                `--out=json=${resultFile}_raw.json`,
                `--summary-export=${resultFile}_summary.json`
            ], {
                stdio: "inherit",
                env: {
                    ...process.env,
                    TEST_NAME: scenarioName,
                    USER_PATH: userFile,
                    RUNNUMBER: runId,
                    TEST_TYPE: failureClass
                }
            });

            await sleep(30000);

            console.log("Triggering chaos...");

            // START TIME kommt aus runScenario (WICHTIG)

            try {
                startTime = await runScenario(envType, scenario);
                const recoveryPromise = waitForStableRecovery(recoveryTargets, 5000);

                const timeoutPromise = timeout(CHAOS_TIMEOUT_MS);

                // END TIME = entweder Recovery oder Timeout
                endTime = await Promise.race([
                    recoveryPromise,
                    timeoutPromise
                ]);

            } catch (e) {
                console.error("Recovery not completed or timeout reached:", e);

                // FALLBACK: wenn NICHT fertig → aktueller Zeitpunkt
                endTime = Date.now();
            }

            const recoveryTimeMs = endTime - startTime;

            const recoveryResultFile = path.join(
                resultDir,
                `${failureClass}_${runId}_recovery.json`
            );

            fs.writeFileSync(
                recoveryResultFile,
                JSON.stringify({
                    recoveryStart: startTime,
                    recoveryEnd: endTime,
                    recoveryTimeMs,
                    recovered: recoveryTimeMs < CHAOS_TIMEOUT_MS
                }, null, 2)
            );

            console.log("Stopping k6...");
            await waitForProcess(k6Process);

            await waitForIdle({ api });
        })();

        await pipeline;

    } catch (e) {
        console.error("PIPELINE ERROR:", e);

        if (k6Process && !k6Process.killed) {
            try {
                k6Process.kill("SIGTERM");
            } catch {}
        }

    } finally {
        console.log("PIPELINE FINISHED - cleanup starting");

        try {
            await cleanup(envType);
        } catch (e) {
            console.error("ENV cleanup failed", e);
        }

        try {
            if (failureClass !== "update") {
                await cleanupChaos(envType);
            }
        } catch (e) {
            console.error("Chaos cleanup failed", e);
        }
    }
}

run();