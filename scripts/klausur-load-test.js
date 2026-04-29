import path from "path";
import fs from "fs";
import { execSync } from "child_process";

// Projektroot automatisch berechnen
const ROOT = process.cwd();

const envType = process.argv[2];
const testType = process.argv[3];

if (!envType || !testType) {
    console.error("Usage: node scripts/load-tests/klausur-load-test.js <docker|k3s> <testType>");
    process.exit(1);
}

// env file
const envFile = path.join(
    ROOT,
    envType === "k3s" ? ".env.k3s" : ".env.docker"
);

const envContent = fs.readFileSync(envFile, "utf8");

envContent.split("\n").forEach(line => {
    const [key, value] = line.split("=");
    if (key && value) {
        process.env[key.trim()] = value.trim();
    }
});

// test file
const testFile = path.join(
    ROOT,
    "test",
    "load",
    "klausur",
    "tests",
    `${testType}.js`
);

const resultFile = path.join(
    ROOT,
    "results",
    envType,
    "load",
    `klausur-${testType}.json`
);

console.log(`🚀 Running ${testType} on ${envType}`);

execSync(`k6 run "${testFile}" --out json=${resultFile}`, {
    stdio: "inherit",
    env: process.env
});

