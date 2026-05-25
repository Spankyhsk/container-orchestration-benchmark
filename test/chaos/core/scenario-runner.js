import fs from "fs";
import path from "path";

import { render } from "./template-engine.js";
import {
    applyKubernetesYaml,
    runDockerCommand
} from "./remote-executer.js";

const ROOT = process.cwd();

// =====================================================
// MAIN
// =====================================================
export async function runScenario(envType, scenario) {

    console.log(`[SCENARIO] ${scenario.failureClass}`);

    if (envType === "k3s") {
        return runK8s(scenario);
    }

    if (envType === "docker") {
        return runDocker(scenario);
    }

    throw new Error("unknown env");
}

// =====================================================
// KUBERNETES
// =====================================================
function runK8s(scenario) {

    const templates = {
        INSTANCE_FAILURE: "instance-failure.yaml",
        SERVICE_OUTAGE: "service-outage.yaml",
        NETWORK_DEGRADATION: "network-chaos.yaml"
    };

    const file = templates[scenario.failureClass];

    if (!file) throw new Error("No template for " + scenario.failureClass);

    const templatePath = path.join(
        ROOT,
        "test/chaos/templates/k3s",
        file
    );

    const yaml = fs.readFileSync(templatePath, "utf8");

    const rendered = render(yaml, {
        NAME: scenario.name,
        MODE: scenario.mode,
        K8S_LABEL: scenario.target.k8sLabel,
        DURATION: scenario.chaos.duration,
        LATENCY: scenario.network?.latencyMs || 0,
        LOSS: scenario.network?.lossPercent || 0
    });

    applyKubernetesYaml(rendered);
}

// =====================================================
// DOCKER
// =====================================================
export function runDocker(scenario) {


    const templateMap = {
        INSTANCE_FAILURE: "instance-failure.sh",
        SERVICE_OUTAGE: "service-outage.sh",
        NETWORK_DEGRADATION: "network-chaos.sh"
    };

    const templateFile = templateMap[scenario.failureClass];

    if (!templateFile) {
        throw new Error("No template for " + scenario.failureClass);
    }

    const filePath = path.join(
        ROOT,
        "test/chaos/templates/docker",
        templateFile
    );

    const template = fs.readFileSync(filePath, "utf8");

    const rendered = render(template, {
        CONTAINER: scenario.target.container,
        LATENCY: scenario.network?.latencyMs || 0,
        LOSS: scenario.network?.lossPercent || 0,
        DURATION: scenario.chaos?.duration || 30
    });

    runDockerCommand(rendered);
}