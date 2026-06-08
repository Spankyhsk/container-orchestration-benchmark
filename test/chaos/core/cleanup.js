import { runRemote } from "./remote-executer.js";

export async function cleanupChaos(envType) {

    if (envType === "k3s") {
        await cleanupKubernetes();
    }

    if (envType === "docker") {
        await cleanupDocker();
    }
}

export async function cleanupKubernetes() {

    console.log("Cleaning Kubernetes chaos resources...");

    runRemote(
        "kubectl delete podchaos --all -A --ignore-not-found; " +
        "kubectl delete networkchaos --all -A --ignore-not-found; " +
        "kubectl delete stresschaos --all -A --ignore-not-found"
    );
}

export async function cleanupDocker() {

    console.log("Cleaning Docker chaos resources...");

    runRemote(`cd ~/teamprojekt && docker compose down && docker compose up -d`);
}