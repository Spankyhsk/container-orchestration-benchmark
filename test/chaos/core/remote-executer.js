import { execSync } from "child_process";

// =====================================================
// INTERNAL STATE
// =====================================================
let sshConfig = {
    host: null,
    user: null
};

// =====================================================
// SET SSH CONFIG
// =====================================================
export function setSSHConfig({ host, user }) {

    if (!host || !user) {
        throw new Error("SSH config requires host + user");
    }

    sshConfig = {
        host,
        user
    };
}

// =====================================================
// BUILD TARGET
// =====================================================
function getTarget() {

    if (!sshConfig.host || !sshConfig.user) {
        throw new Error(
            "SSH config not initialized. Call setSSHConfig() first."
        );
    }

    return `${sshConfig.user}@${sshConfig.host}`;
}

// =====================================================
// BASE SSH EXEC
// =====================================================
function ssh(cmd) {

    const target = getTarget();

    execSync(
        `ssh -T ${target} "${cmd}"`,
        {
            stdio: "inherit"
        }
    );
}

// =====================================================
// KUBERNETES YAML APPLY
// =====================================================
//
// YAML wird lokal erzeugt und direkt über STDIN
// an kubectl auf der VM übertragen.
//
// Externer Rechner
//      ↓
// ssh vm "kubectl apply -f -"
//      ↓
// kubectl erhält YAML über stdin
//
// =====================================================
export function applyKubernetesYaml(yamlContent) {

    const target = getTarget();

    execSync(
        `ssh ${target} "kubectl apply -f -"`,
        {
            input: yamlContent,
            stdio: [
                "pipe",
                "inherit",
                "inherit"
            ],
            maxBuffer: 10 * 1024 * 1024
        }
    );
}

// =====================================================
// DOCKER COMMAND
// =====================================================
export function runDockerCommand(cmd) {

    ssh(cmd);
}

// =====================================================
// GENERIC REMOTE COMMAND
// =====================================================
export function runRemote(cmd) {

    ssh(cmd);
}