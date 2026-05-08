import path from "path";
import fs from "fs";
import { execSync } from "child_process";

import { createUsers } from "./shared/lifecycle/create-users.js";
import { setupUsers } from "./shared/lifecycle/setup-users.js";
import {cleanupCreatedUsers, cleanupUsers} from "./shared/lifecycle/cleanup-users.js";
import { waitForIdle } from "./shared/helpers/helpers.js";
import { loginAdmin } from "./shared/helpers/auth.js";
import { API } from "./shared/api/node-api.js";
import {buildUsers} from "./shared/helpers/buildUsers.js";

const ROOT = path.resolve(process.cwd(), "..", "..");

async function run() {

    const testName = process.argv[2];   // login, klausur
    const envType = process.argv[3];    // docker, k3s
    const testType = process.argv[4];   // smoke, spike, averageLoad

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
                const [k, v] = line.split("=");
                if (k && v) process.env[k.trim()] = v.trim();
            });

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

        const resultDir = path.join(ROOT, "results", envType, "load", testName);
        fs.mkdirSync(resultDir, { recursive: true });

        const resultFile = path.join(resultDir, `${testType}.json`);

        const usersFile = path.join(ROOT, "test/load", testName, "users.json");

        // --------------------
        // PIPELINE START
        // --------------------
        let users;   // <- WICHTIG

        if (isAuthTest) {
            console.log("Auth Load Test Mode");

            users = await buildUsers({
                count: profile.users
            });

        } else {
            console.log("Admin login...");
            adminToken = loginAdmin({ api });

            console.log("Creating users...");
            users = await createUsers({
                api,
                count: profile.users
            });
        }

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

        execSync(
            `k6 run "${testFile}" --out json="${resultFile}"`,
            {
                stdio: "inherit",
                env: {
                    ...process.env,

                    // k6 INPUTS
                    SCENARIO_PATH: scenarioPath,
                    LOADPROFILES_PATH: loadProfilesPath,
                    THRESHOLDS_PATH: thresholdsPath,

                    TEST_NAME: testName,
                    USERS_PATH: usersFile
                }
            }
        );

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
                if(isAuthTest){
                    await cleanupCreatedUsers({
                        api,
                        users: preparedUsers,
                        adminToken
                    });
                }else{
                    await cleanupUsers({
                        api,
                        users: preparedUsers,
                        adminToken
                    });
                }

            } catch (cleanupErr) {
                console.error("CLEANUP FAILED:", cleanupErr);
            }
        }

        console.log("PIPELINE FINISHED");
    }
}

run();