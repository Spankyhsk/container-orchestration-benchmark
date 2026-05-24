import path from "path";
import fs from "fs";
import { spawn, execSync } from "child_process";
import { fileURLToPath } from "url";

import { waitForIdle } from "../load/shared/helpers/waitForIdle.js";
import { cleanup } from "../load/shared/lifecycle/cleanup.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, "..", "..");

async function run() {

    // --------------------
    // CLI PARAMS
    // --------------------
    const testName = process.argv[2];        // klausur, login
    const envType = process.argv[3];         // docker, k3s
    const chaosScenario = process.argv[4];   // pod-kill, service-failure
    const runId = process.argv[5] || "0";

    if (!testName || !envType || !chaosScenario) {
        throw new Error(
            "Usage: node run-test.js <testName> <envType> <chaosScenario> <runId>"
        );
    }

    console.log(`Running chaos test:
    Test: ${testName}
    Env: ${envType}
    Scenario: ${chaosScenario}
    Run: ${runId}`);

    try {

        // --------------------
        // ENV LOAD
        // --------------------
        const envFile = path.join(
            ROOT,
            envType === "k3s"
                ? ".env.k3s"
                : ".env.docker"
        );

        fs.readFileSync(envFile, "utf8")
            .split("\n")
            .forEach(line => {

                const trimmed = line.trim();

                if (!trimmed || trimmed.startsWith("#")) return;

                const index = trimmed.indexOf("=");

                if (index === -1) return;

                const key = trimmed.slice(0, index).trim();
                const value = trimmed.slice(index + 1).trim();

                process.env[key] = value;
            });

        console.log("BASE_URL:", process.env.BASE_URL);

        // --------------------
        // FIXED LOAD PROFILE
        // --------------------
        const testFile = path.join(
            ROOT,
            "test/load/tests",
            "averageLoad.js"
        );

        // --------------------
        // RESULT PATHS
        // --------------------
        const resultDir = path.join(
            ROOT,
            "results",
            envType,
            "chaos",
            testName,
            chaosScenario
        );

        fs.mkdirSync(resultDir, { recursive: true });

        const resultFile = path.join(
            resultDir,
            `${chaosScenario}_${runId}`
        );

        // --------------------
        // K6 ENV
        // --------------------
        const k6Env = {
            ...process.env,

            TEST_NAME: testName,
            CHAOS_SCENARIO: chaosScenario,
            RUNNUMBER: runId
        };

        // --------------------
        // WAIT BEFORE START
        // --------------------
        console.log("Waiting for idle system...");
        await waitForIdle({});

        // --------------------
        // START K6
        // --------------------
        console.log("Starting k6 averageLoad test...");

        const k6Process = spawn(
            "k6",
            [
                "run",
                testFile,

                "--no-setup",
                "--no-teardown",

                `--out=json=${resultFile}_raw.json`,

                `--summary-export=${resultFile}_summary.json`
            ],
            {
                stdio: "inherit",
                env: k6Env
            }
        );

        // --------------------
        // WAIT BEFORE CHAOS
        // --------------------
        console.log("Waiting 30s before chaos injection...");

        await sleep(30000);

        // --------------------
        // TRIGGER CHAOS
        // --------------------
        console.log(`Triggering chaos scenario: ${chaosScenario}`);

        await triggerChaos(envType, chaosScenario);

        // --------------------
        // WAIT FOR K6 END
        // --------------------
        await waitForProcess(k6Process);

        console.log("Chaos test finished");

        // --------------------
        // WAIT AFTER TEST
        // --------------------
        console.log("Waiting for stabilization...");
        await waitForIdle({});

    } catch (err) {

        console.error("CHAOS PIPELINE FAILED:", err);

    } finally {

        // --------------------
        // CLEANUP
        // --------------------
        try {

            console.log(`Running cleanup for env: ${envType}`);

            cleanup(envType);

        } catch (cleanupErr) {

            console.error("CLEANUP FAILED:", cleanupErr);
        }

        console.log("CHAOS PIPELINE FINISHED");
    }
}

// --------------------
// CHAOS EXECUTION
// --------------------
async function triggerChaos(envType, chaosScenario) {

    if (envType === "k3s") {

        const chaosFile = path.join(
            ROOT,
            "test/chaos/scenarios/k3s",
            `${chaosScenario}.yaml`
        );

        execSync(
            `kubectl apply -f "${chaosFile}"`,
            {
                stdio: "inherit"
            }
        );

    } else {

        const scriptFile = path.join(
            ROOT,
            "test/chaos/scenarios/docker",
            `${chaosScenario}.sh`
        );

        execSync(
            `bash "${scriptFile}"`,
            {
                stdio: "inherit"
            }
        );
    }
}

// --------------------
// WAIT HELPERS
// --------------------
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function waitForProcess(process) {

    return new Promise((resolve, reject) => {

        process.on("close", code => {

            if (code === 0) {
                resolve();
            } else {
                reject(new Error(`Process exited with code ${code}`));
            }
        });

        process.on("error", reject);
    });
}

run();