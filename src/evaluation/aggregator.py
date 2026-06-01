import os
import json
from glob import glob


# =================================================
# SAFE LOAD
# =================================================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =================================================
# SAFE OPS
# =================================================
def safe_list(values):
    return [v for v in values if v is not None]


def avg(values):
    values = safe_list(values)
    return sum(values) / len(values) if values else None


def maxv(values):
    values = safe_list(values)
    return max(values) if values else None


def minv(values):
    values = safe_list(values)
    return min(values) if values else None


def sumv(values):
    values = safe_list(values)
    return sum(values) if values else 0


# =================================================
# AGGREGATE RUNS (UNCHANGED LOGIC - CLEANED)
# =================================================
def aggregate_runs(files):

    data = [load_json(f) for f in files if os.path.exists(f)]

    if not data:
        return None

    base = data[0]

    def collect(key):
        return [d.get(key) for d in data]

    aggregated = {

        # =========================
        # IDENTIFIERS
        # =========================
        "environment": base.get("environment"),
        "testClass": base.get("testClass"),
        "scenario": base.get("scenario"),
        "testType": base.get("testType"),

        "runs": len(data),

        # =========================
        # TIME (FAIR ACROSS RUNS)
        # =========================
        "startTime": minv(collect("startTime")),
        "endTime": maxv(collect("endTime")),

        # =========================
        # K6 PERFORMANCE
        # =========================
        "latency_avg": avg(collect("latency_avg")),
        "latency_p95": avg(collect("latency_p95")),
        "latency_p99": avg(collect("latency_p99")),

        "error_rate": avg(collect("error_rate")),

        "requests_total": sumv(collect("requests_total")),
        "requests_rate": avg(collect("requests_rate")),

        # =========================
        # CPU
        # =========================
        "cpu_avg": avg(collect("cpu_avg")),
        "cpu_max": maxv(collect("cpu_max")),
        "cpu_min": minv(collect("cpu_min")),

        # =========================
        # MEMORY
        # =========================
        "memory_avg": avg(collect("memory_avg")),
        "memory_max": maxv(collect("memory_max")),
        "memory_min": minv(collect("memory_min")),

        # =========================
        # NETWORK
        # =========================
        "network_rx_avg": avg(collect("network_rx_avg")),
        "network_tx_avg": avg(collect("network_tx_avg")),

        # =========================
        # DISK
        # =========================
        "disk_read_avg": avg(collect("disk_read_avg")),
        "disk_write_avg": avg(collect("disk_write_avg")),

        # =========================
        # NODE
        # =========================
        "node_cpu_max": maxv(collect("node_cpu_max")),
        "node_memory_max": maxv(collect("node_memory_max")),
        "node_load_max": maxv(collect("node_load_max")),

        # =========================
        # INFRA ADDITIONS
        # =========================
        "restarts": sumv(collect("restarts")),

        # =========================
        # SCORE (MEAN ACROSS RUNS)
        # =========================
        "reliability_score": avg(collect("reliability_score")),

        # =========================
        # RECOMMENDATIONS (DEDUP)
        # =========================
        "recommendations": list({
            r
            for d in data
            for r in d.get("recommendations", [])
            if r
        })
    }

    return aggregated


# =================================================
# RUN AGGREGATION (FIXED PATH STRUCTURE)
# =================================================
def run_aggregation(env, testClass, scenario, testType):


    #if anweisung einbauen
    base_path = f"results/{env}/{testClass}/{scenario}/{testType}"

    pattern = os.path.join(base_path, "summary_*_final.json")
    files = glob(pattern)

    if not files:
        print(f"No summaries found in {base_path}")
        return None

    aggregated = aggregate_runs(files)

    if not aggregated:
        return None

    out_path = os.path.join(base_path, "aggregate.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2)

    print(f"Saved: {out_path}")

    return out_path