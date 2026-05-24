import time
import requests


def wait_for_http(name: str, url: str, timeout: int = 60):
    """
    Level 2 readiness check: HTTP must respond 200
    """

    start = time.time()

    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(f"[OK] {name} ready")
                return True
        except Exception:
            pass

        time.sleep(1)

    raise TimeoutError(f"{name} not ready: {url}")


def wait_for_stack(grafana_url: str, prom_url: str):
    """
    Combined check for full monitoring stack
    """

    print("Waiting for Grafana...")
    wait_for_http("Grafana", f"{grafana_url}/api/health")

    print("Waiting for Prometheus...")
    wait_for_http("Prometheus", f"{prom_url}/api/v1/status/runtimeinfo")

    print("Monitoring stack ready")