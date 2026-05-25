import { execSync } from "child_process";

// =====================================================
// INTERNAL STATE
// =====================================================
let sshConfig = {
    host: null,
    user: null
};

// =====================================================
// SET SSH CONFIG (IMPORTANT)
// =====================================================
export function setSSHConfig({ host, user }) {

    if (!host || !user) {
        throw new Error("SSH config requires host + user");
    }

    sshConfig = { host, user };
}

// =====================================================
// BUILD TARGET
// =====================================================
function getTarget() {

    if (!sshConfig.host || !sshConfig.user) {
        throw new Error("SSH config not initialized. Call setSSHConfig() first.");
    }

    return `${sshConfig.user}@${sshConfig.host}`;
}

// =====================================================
// BASE SSH EXEC
// =====================================================
function ssh(cmd) {

    const target = getTarget();

    execSync(`ssh ${target} "${cmd}"`, {
        stdio: "inherit"
    });
}

// =====================================================
// KUBERNETES APPLY (via cat)
// =====================================================
export function applyKubernetesYaml(yamlContent) {

    const cmd = `cat <<EOF | kubectl apply -f -
${yamlContent}
EOF`;

    ssh(cmd);
}

// =====================================================
// DOCKER COMMAND
// =====================================================
export function runDockerCommand(cmd) {

    ssh(cmd);
}

// =====================================================
// GENERIC
// =====================================================
export function runRemote(cmd) {
    ssh(cmd);
}