import time
import requests
import socket


# =========================================================
# BASIC HTTP CHECK (ROBUST AGAINST SSH TUNNEL RACE)
# =========================================================
def wait_for_http(name: str, url: str, timeout: int = 120):
    """
    HTTP endpoint must answer with 200
    - handles SSH tunnel startup delays
    - handles port-forward race conditions
    """

    print(f"[WAIT] {name} -> {url}")

    start = time.time()
    last_error = None

    while time.time() - start < timeout:

        try:
            r = requests.get(url, timeout=5)

            if r.status_code == 200:
                print(f"[OK] {name} ready -> {url}")
                return True

        except requests.exceptions.ConnectionError as e:
            # THIS is expected during SSH tunnel startup
            last_error = str(e)

        except Exception as e:
            last_error = str(e)

        time.sleep(2)

    raise TimeoutError(
        f"{name} not ready (timeout): {url} | last_error={last_error}"
    )


# =========================================================
# PROMETHEUS METRICS CHECK (UNCHANGED LOGIC, SAFER LOOP)
# =========================================================
def wait_for_prometheus_metrics(prom_url: str, timeout: int = 120):
    """
    Wait until Prometheus returns real metric data
    """

    print("Waiting for Prometheus metrics...")

    start = time.time()

    query_urls = [
        f"{prom_url}/api/v1/query",
        f"{prom_url}/api/v1/query?query=up"
    ]

    last_error = None

    while time.time() - start < timeout:

        for url in query_urls:

            try:
                r = requests.get(
                    url,
                    params={"query": "up"} if "query?" not in url else None,
                    timeout=5
                )

                if r.status_code != 200:
                    continue

                data = r.json()

                if "data" not in data:
                    continue

                result = data["data"].get("result", [])

                if len(result) > 0:
                    print("[OK] Prometheus metrics ready")
                    return True

            except requests.exceptions.ConnectionError as e:
                last_error = str(e)

            except Exception as e:
                last_error = str(e)

        time.sleep(2)

    raise TimeoutError(
        f"Prometheus metrics not ready: {prom_url} | last_error={last_error}"
    )


# =========================================================
# FULL STACK CHECK (UI CALLS THIS - NO CHANGES REQUIRED)
# =========================================================
def wait_for_stack(grafana_url: str, prom_url: str):
    """
    Combined readiness check for Grafana + Prometheus
    SAFE AGAINST SSH TUNNEL RACE CONDITIONS
    """

    # -----------------------------------------------------
    # GRAFANA
    # -----------------------------------------------------
    print("Waiting for Grafana...")

    wait_for_http(
        "Grafana",
        f"{grafana_url}/api/health"
    )

    # -----------------------------------------------------
    # PROMETHEUS BASIC READY CHECK
    # -----------------------------------------------------
    print("Waiting for Prometheus API...")

    wait_for_http(
        "Prometheus API",
        f"{prom_url}/-/ready"
    )

    # -----------------------------------------------------
    # OPTIONAL runtimeinfo (non-blocking)
    # -----------------------------------------------------
    try:
        wait_for_http(
            "Prometheus runtime",
            f"{prom_url}/api/v1/status/runtimeinfo",
            timeout=20
        )
    except Exception:
        print("[WARN] runtimeinfo not available, continuing...")

    # -----------------------------------------------------
    # IMPORTANT: give SSH tunnel / kube-proxy a small buffer
    # -----------------------------------------------------
    time.sleep(3)

    # -----------------------------------------------------
    # METRICS (kept optional because heavy)
    # -----------------------------------------------------
    # wait_for_prometheus_metrics(prom_url)

    print("Monitoring stack fully ready")