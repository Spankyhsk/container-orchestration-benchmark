import path from "path";
import fs from "fs";
import { execSync } from "child_process";

import { createUsers } from "./shared/lifecycle/create-users.js";
import { setupUsers } from "./shared/lifecycle/setup-users.js";
import { cleanupUsers} from "./shared/lifecycle/cleanup-users.js";
import { waitForIdle } from "./shared/helpers/waitForIdle.js";
import { loginAdmin } from "./shared/helpers/auth.js";
import { API } from "./shared/api/node-api.js";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, "..", "..");

async function run() {

    const testName = process.argv[2];   // login, klausur
    const envType = process.argv[3];    // docker, k3s
    const testType = process.argv[4];   // smoke, spike, averageLoad
    const runId = process.argv[5] || "0"; // fallback Nummer
    const withAnnotate = process.argv[6] || "0";

    if (!testName || !envType || !testType) {
        throw new Error("Usage: node run-test.js <testName> <env> <testType>");
    }

    console.log(`Running ${testName} (${testType}) on ${envType}`);

    let preparedUsers = [];
    let adminToken;
    let api;


    try {
        const isAuthTest = testName === "login";


        // --------------------
        // ENV LOAD
        // --------------------
        const envFile = path.join(
            ROOT,
            envType === "k3s" ? ".env.k3s" : ".env.docker"
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

        console.log("BASE_URL RAW:", JSON.stringify(process.env.BASE_URL));

        api = API(process.env.BASE_URL);

        // --------------------
        // CONFIG PATHS
        // --------------------
        const configPath = path.join(ROOT, "test/load", testName, "config");

        const scenarioPath = path.join(configPath, "scenario.json");
        const loadProfilesPath = path.join(configPath, "load-profiles.json");
        const thresholdsPath = path.join(configPath, "thresholds.json");

        const scenario = JSON.parse(fs.readFileSync(scenarioPath, "utf8"));
        const loadProfiles = JSON.parse(fs.readFileSync(loadProfilesPath, "utf8"));
        const thresholds = JSON.parse(fs.readFileSync(thresholdsPath, "utf8"));

        const profile = loadProfiles[testType];

        if (!profile) {
            throw new Error(`Unknown testType: ${testType}`);
        }

        const isSmoke = testType === "smoke";

        // --------------------
        // FILE PATHS
        // --------------------
        const testFile = path.join(
            ROOT,
            "test/load/tests",
            `${testType}.js`
        );

        const resultDir = path.join(ROOT, "results", envType, "load", testName, testType);
        fs.mkdirSync(resultDir, { recursive: true });

        const resultFile = path.join(resultDir, `${testType}_${runId}`);

        const usersFile = path.join(ROOT, "test/load", testName, "users.json");

        // --------------------
        // PIPELINE START
        // --------------------
        let users;   // <- WICHTIG

        console.log("Admin login...");

        adminToken = await loginAdmin(api)

        console.log("Creating users...");

        users = await createUsers({
            api,
            count: profile.users
        });


        console.log("Setting up users...");
        preparedUsers = await setupUsers({
            users,
            scenario,
            api,
            adminToken,
            mode: testType,
            forcedRole: isSmoke ? profile.smokeRole : null,
            isAuthTest: isAuthTest
        });

        // --------------------
        // WRITE USERS FOR K6
        // --------------------
        fs.writeFileSync(usersFile, JSON.stringify(preparedUsers, null, 2));

        console.log("Waiting for system stabilization...");
        await waitForIdle({ api });

        // --------------------
        // RUN K6
        // --------------------
        console.log("Running k6...");

        let k6Env = {
            ...process.env,

            // k6 INPUTS
            SCENARIO_PATH: scenarioPath,
            LOADPROFILES_PATH: loadProfilesPath,
            THRESHOLDS_PATH: thresholdsPath,

            TEST_NAME: testName,
            USERS_PATH: usersFile,
            RUNNUMBER: runId
        };

        const useSetupTeardown = withAnnotate === "1";

        const cmd = useSetupTeardown
            ? `k6 run "${testFile}" --out json="${resultFile}_raw.json" --summary-export="${resultFile}_summary.json"`
            : `k6 run "${testFile}" --no-setup --no-teardown --out json="${resultFile}_raw.json" --summary-export="${resultFile}_summary.json"`;

        console.log("Lifecycle mode:", useSetupTeardown ? "FULL (setup+teardown)" : "MINIMAL (no setup/teardown)");

        execSync(cmd, {
            stdio: "inherit",
            env: k6Env
        });

        console.log("Load test finished");

    } catch (err) {

        console.error("PIPELINE FAILED:", err);

    } finally {

        // --------------------
        // CLEANUP
        // --------------------
        if (preparedUsers.length > 0 && adminToken) {

            console.log("Cleaning up users...");

            try {
                    await cleanupUsers({
                        api,
                        users: preparedUsers,
                        adminToken
                    });

            } catch (cleanupErr) {
                console.error("CLEANUP FAILED:", cleanupErr);
            }
        }

        console.log("PIPELINE FINISHED");
    }
}

run();