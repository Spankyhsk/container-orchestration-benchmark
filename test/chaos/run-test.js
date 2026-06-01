import path from "path";
import fs from "fs";
import { spawn } from "child_process";
import { fileURLToPath } from "url";

import { waitForIdle } from "../load/shared/helpers/waitForIdle.js";
import { cleanup } from "./shared/lifecycle/cleanup.js";
import { cleanupChaos} from "./core/cleanup.js";

import { runScenario } from "./core/scenario-runner.js";
import {createUsers} from "./shared/lifecycle/create-users.js";
import {API} from "./shared/api/node-api.js";
import { setSSHConfig } from "./core/remote-executer.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, "..", "..");

// =====================================================
async function run() {

    const scenarioName = process.argv[2]; //api-instance-down, ...
    const envType = process.argv[3]; // docker || k3s
    const failureClass = process.argv[4]; // instance-failure, network-degradation
    const runId = process.argv[5] || "0";

    if (!failureClass || !envType || !scenarioName) {
        throw new Error("Usage: node run-test.js <test> <env> <scenario> <runId>");
    }

    console.log(`CHAOS RUN: ${scenarioName}`);

    let api;

    try {

        // ENV LOAD
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

        const sshHost = process.env.SSH_HOST;
        const sshUser = process.env.SSH_USER;

        setSSHConfig({
            host: sshHost,
            user: sshUser
        });

        const testFile = path.join(
            ROOT,
            "test/chaos/k6/load-test.js"
        );

        const scenarioPath = path.join(
            ROOT,
            "test/chaos/scenarios",
            `${failureClass}`,
            `${scenarioName}.json`
        );

        const scenario = JSON.parse(
            fs.readFileSync(scenarioPath, "utf8")
        );

        const resultDir = path.join(
            ROOT,
            "results",
            envType,
            "chaos",
            scenarioName,
            failureClass
        );

        fs.mkdirSync(resultDir, { recursive: true });

        const resultFile = path.join(
            resultDir,
            `${failureClass}_${runId}`
        );

        const userFile = path.join(ROOT, "test/chaos/k6/users.json")

        let users;

        users = await createUsers({
            api,
            count: 50
        });

        fs.writeFileSync(userFile, JSON.stringify(users, null, 2));

        let k6Env = {
            ...process.env,

            TEST_NAME: scenarioName,
            USER_PATH: userFile,
            RUNNUMBER: runId,
            TEST_TYPE: failureClass
        }

        await waitForIdle({ api });

        console.log("Starting k6...");

        const k6Process = spawn("k6", [
            "run",
            testFile,
            `--out=json=${resultFile}_raw.json`,
            `--summary-export=${resultFile}_summary.json`
        ], {
            stdio: "inherit",
            env: k6Env
        });

        await sleep(30000);

        console.log("Triggering chaos...");

        await runScenario(envType, scenario);

        await waitForProcess(k6Process);

        await waitForIdle({api});

    } catch (e) {

        console.error(e);

    } finally {

        // --------------------
        // CLEANUP
        // --------------------
        try {
            console.log(`Running remote cleanup for env: ${envType}`);

            cleanup(envType);
            cleanupChaos(envType);

        } catch (cleanupErr) {
            console.error("CLEANUP FAILED:", cleanupErr);
        }

        console.log("PIPELINE FINISHED");
    }
}

// helpers
function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

function waitForProcess(p) {
    return new Promise((res, rej) => {
        p.on("close", c => c === 0 ? res() : rej(c));
    });
}

run();