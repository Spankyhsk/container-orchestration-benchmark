import fs from "fs";
import path from "path";

import {
    applyKubernetesYaml,
    runDockerCommand, runRemote
} from "./remote-executer.js";

const ROOT = process.cwd();

// =====================================================
// MAIN
// =====================================================
export async function runScenario(envType, scenario) {

    if (envType === "k3s") {
        return runK8s(scenario);
    }

    if (envType === "docker") {
        return runDocker();
    }

    throw new Error("unknown env");
}

function runK8s(scenario){
    runRemote(`kubectl rollout restart deployment ${scenario}`)
}

function runDocker(){
    runRemote('bash teamprojekt/webhook.sh')
}

