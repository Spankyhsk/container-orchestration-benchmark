import time
import requests


# =========================================================
# BASIC HTTP CHECK
# =========================================================
def wait_for_http(name: str, url: str, timeout: int = 60):
    """
    HTTP endpoint must answer with 200
    """

    start = time.time()

    while time.time() - start < timeout:

        try:
            r = requests.get(url, timeout=3)

            if r.status_code == 200:
                print(f"[OK] {name} ready -> {url}")
                return True

        except requests.exceptions.ConnectionError:
            # klarer Hinweis: Service/Portforward noch nicht da
            pass

        except Exception as e:
            print(f"[WARN] {name} check error: {e}")

        time.sleep(1)

    raise TimeoutError(f"{name} not ready (timeout): {url}")


# =========================================================
# PROMETHEUS METRICS CHECK (IMPROVED)
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

                # ---- URL valid but no response?
                if r.status_code != 200:
                    continue

                data = r.json()

                # safety checks (Prometheus can return partial/empty)
                if "data" not in data:
                    continue

                result = data["data"].get("result", [])

                # IMPORTANT:
                # Prometheus is only ready if at least 1 time series exists
                if len(result) > 0:
                    print("[OK] Prometheus metrics ready")
                    return True

            except requests.exceptions.ConnectionError as e:
                last_error = f"connection error: {e}"

            except Exception as e:
                last_error = str(e)

        time.sleep(2)

    raise TimeoutError(
        f"Prometheus metrics not ready: {prom_url} | last_error={last_error}"
    )


# =========================================================
# FULL STACK CHECK
# =========================================================
def wait_for_stack(grafana_url: str, prom_url: str):
    """
    Combined readiness check for Grafana + Prometheus
    """

    # -----------------------------------------------------
    # GRAFANA (IMPORTANT: real health endpoint)
    # -----------------------------------------------------
    print("Waiting for Grafana...")

    wait_for_http(
        "Grafana",
        f"{grafana_url}/api/health"
    )

    # -----------------------------------------------------
    # PROMETHEUS API (basic reachability)
    # -----------------------------------------------------
    print("Waiting for Prometheus API...")

    # FIXED: better endpoint for readiness
    wait_for_http(
        "Prometheus API",
        f"{prom_url}/-/ready"
    )

    # fallback check (some setups only expose runtimeinfo)
    try:
        wait_for_http(
            "Prometheus runtime",
            f"{prom_url}/api/v1/status/runtimeinfo",
            timeout=20
        )
    except Exception:
        print("[WARN] runtimeinfo not available, continuing...")

    # -----------------------------------------------------
    # REAL METRICS CHECK
    # -----------------------------------------------------
    #wait_for_prometheus_metrics(prom_url)

    print("Monitoring stack fully ready")