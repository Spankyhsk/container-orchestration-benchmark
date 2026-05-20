import { execSync } from "node:child_process";

export function cleanup(envType) {

    const sshUser = process.env.SSH_USER;
    const sshHost = process.env.SSH_HOST;

    const script = `/opt/scripts/cleanup-${envType}.sh`;

    const cmd = `ssh ${sshUser}@${sshHost} "sudo ${script}"`;

    execSync(cmd, {
        stdio: "inherit",
        shell: "cmd.exe"
    });
}
