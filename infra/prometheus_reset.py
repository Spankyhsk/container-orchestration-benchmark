import os
import subprocess
from pathlib import Path
import time
import requests


# ---------------------------------------------------
# Load .env.k3s
# ---------------------------------------------------
def load_env_k3s(env_file: str = ".env.k3s"):
    env_path = Path(env_file)

    if not env_path.exists():
        raise FileNotFoundError(f"{env_file} not found in project root")

    env_vars = {}

    with env_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

    return env_vars


# ---------------------------------------------------
# SSH helper (robust retry included)
# ---------------------------------------------------
def ssh_run(host, user, command, retries=3):
    ssh_cmd = ["ssh", f"{user}@{host}", command]

    for i in range(retries):
        print(f"[SSH] Attempt {i+1}: {command}")

        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout

        print("[SSH FAIL]")
        print(result.stderr)

        time.sleep(2)

    raise RuntimeError(f"SSH command failed after {retries} retries: {command}")


# ---------------------------------------------------
# Prometheus reset (hard clean state for each test)
# ---------------------------------------------------
def reset_prometheus(wait_seconds: int = 10):
    env = load_env_k3s()

    ssh_host = env.get("SSH_HOST")
    ssh_user = env.get("SSH_USER")

    if not ssh_host or not ssh_user:
        raise ValueError("SSH_HOST or SSH_USER missing in .env.k3s")

    namespace = "monitoring"
    sts = "prometheus-monitoring-kube-prometheus-prometheus"

    print("=== Restart Prometheus (clean TSDB state) ===")

    # restart statefulset
    ssh_run(
        ssh_host,
        ssh_user,
        f"kubectl rollout restart statefulset -n {namespace} {sts}"
    )

    # wait rollout
    ssh_run(
        ssh_host,
        ssh_user,
        f"kubectl rollout status statefulset -n {namespace} {sts} --timeout=180s"
    )

    # IMPORTANT: give Prometheus time to open API again
    print(f"Waiting {wait_seconds}s for Prometheus API stabilization...")
    time.sleep(wait_seconds)

    print("Prometheus reset complete")


def wait_for_prometheus_ready(timeout: int = 120):
    """
    Waits until Prometheus is fully ready after test execution.
    Uses URL from .env.k3s
    """

    env = load_env_k3s()
    prom_url = env.get("PROM_URL")

    if not prom_url:
        raise ValueError("PROM_URL missing in .env.k3s")

    print(f"Waiting for Prometheus readiness: {prom_url}")

    start = time.time()

    while time.time() - start < timeout:

        try:
            # 1. basic API ready
            r = requests.get(f"{prom_url}/-/ready", timeout=5)
            if r.status_code != 200:
                continue

            # 2. real query check
            r2 = requests.get(
                f"{prom_url}/api/v1/query",
                params={"query": "up"},
                timeout=5
            )

            if r2.status_code == 200:
                data = r2.json()
                if data.get("data", {}).get("result"):
                    print("[OK] Prometheus fully ready")
                    return True

        except Exception:
            pass

        time.sleep(2)

    raise TimeoutError(f"Prometheus not ready after timeout: {prom_url}")

def wait_for_tunnel(host="localhost", port=9091, timeout=60):
    import socket
    import time

    print("Waiting for SSH tunnel...")

    start = time.time()

    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("[OK] SSH tunnel ready")
                return True
        except OSError:
            time.sleep(1)

    raise TimeoutError("SSH tunnel not ready")