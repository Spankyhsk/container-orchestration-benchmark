import path from "path";
import { spawn, execSync } from "child_process";

async function triggerChaos(ROOT, envType, chaosScenario) {

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