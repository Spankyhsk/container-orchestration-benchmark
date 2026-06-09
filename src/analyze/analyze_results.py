import json
import pandas as pd
import os

from src.evaluation.scoring import calculate_score_by_type
from src.evaluation.recommendations import generate_recommendations


# =================================================
# METRIC SEMANTIC LAYER
# =================================================
METRIC_TYPE = {

    # Cluster Utilization (0–1)
    "cpu": "cluster_utilization",
    "memory": "cluster_utilization",

    # Node Utilization (0–1)
    "node_cpu": "node_utilization",
    "node_memory": "node_utilization",
    "node_load": "node_utilization",

    # Throughput
    "network_rx": "throughput",
    "network_tx": "throughput",
    "disk_read": "throughput",
    "disk_write": "throughput",

    # Counter
    "restarts": "counter"
}


# =================================================
# LOAD TIMESERIES
# =================================================
def load_timeseries(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    if df.empty:
        return None

    return df


# =================================================
# K6 SUMMARY (SAFE NONE)
# =================================================
def load_k6_summary(path):

    if not os.path.exists(path):
        return {
            "latency_avg": None,
            "latency_p95": None,
            "latency_p99": None,
            "error_rate": None,
            "requests_total": None,
            "requests_rate": None
        }

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics = data.get("metrics", {})

    http_duration = metrics.get("http_req_duration", {})
    http_failed = metrics.get("http_req_failed", {})
    http_reqs = metrics.get("http_reqs", {})

    return {
        "latency_avg": http_duration.get("avg"),
        "latency_p95": http_duration.get("p(95)"),
        "latency_p99": http_duration.get("p(99)"),
        "error_rate": http_failed.get("value"),
        "requests_total": http_reqs.get("count"),
        "requests_rate": http_reqs.get("rate")
    }


# =================================================
# PROMETHEUS LOADER (SAFE)
# =================================================
def load_prometheus_metric(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    if df.empty:
        return None

    values = df["value"].tolist()

    return {
        "avg": float(sum(values) / len(values)),
        "max": float(max(values)),
        "min": float(min(values))
    }


# =================================================
# RAW K6
# =================================================
def load_k6_raw(path):

    if not os.path.exists(path):
        return []

    data = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))

    return data


# =================================================
# SCORE ROUTER
# =================================================

# =================================================
# TREND ANALYSIS (IMPROVED)
# =================================================
def calculate_trend_percent(df):

    if df is None or df.empty or len(df) < 3:
        return 0

    df = df.sort_values("timestamp").dropna(subset=["value"])

    values = df["value"].rolling(window=5, min_periods=1).mean()

    start = values.iloc[:5].mean()
    end = values.iloc[-5:].mean()

    if start == 0:
        return 0

    return ((end - start) / start) * 100


# =================================================
# SOAK TREND EXTRACTION (IMPROVED)
# =================================================
def extract_soak_trends(base, testType, run_id):

    trends = {}

    for name in [
        "memory",
        "cpu",
        "node_load",
        "k6_latency",
        "requests_rate"
    ]:

        df = load_timeseries(
            f"{base}/{testType}_{run_id}_{name}.csv"
        )

        if df is not None:
            trends[f"{name}_growth_percent"] = calculate_trend_percent(df)

    return trends

def process_chaos_metrics(summary_path, recovery_path):
    """
    CHAOS POST PROCESSOR

    Diese Funktion ist bewusst getrennt vom normalen
    Analyseprozess, weil Chaos-spezifische Metriken:

    - recovery time
    - availability
    - post-failure stability

    NICHT Teil von Load/Soak sind.
    """

    import json

    result = {}

    # =====================================================
    # 1. LOAD K6 SUMMARY
    # =====================================================

    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
    else:
        summary = {}

    # =====================================================
    # 2. LOAD RECOVERY RESULT
    # =====================================================

    if os.path.exists(recovery_path):
        with open(recovery_path, "r", encoding="utf-8") as f:
            recovery = json.load(f)
    else:
        recovery = {}

    # =====================================================
    # 3. RECOVERY TIME (CORE CHAOS METRIC)
    # =====================================================

    result["recoveryTimeMs"] = recovery.get("recoveryTimeMs")
    result["recovered"] = recovery.get("recovered")

    # =====================================================
    # 4. AVAILABILITY RATE (aus k6 Summary)
    # =====================================================

    metrics = summary.get("metrics", {})
    http_failed = metrics.get("http_req_failed", {})

    error_rate = http_failed.get("value", 0)

    if error_rate > 0:
        result["availability"] = 1 - error_rate
    else:
        result["availability"] = None

    return result

# =================================================
# MAIN ANALYSIS
# =================================================
def analyze_results(scenario, env, testType, run_id, testClass, startTime, endTime):

    #if einbauen
    base = f"results/{env}/{testClass}/{scenario}/{testType}"

    result = {
        "environment": env,
        "scenario": scenario,
        "testType": testType,
        "testClass": testClass,
        "run": run_id,
        "startTime": startTime,
        "endTime": endTime
    }

    # -------------------------------------------------
    # K6
    # -------------------------------------------------
    summary_path = f"{base}/{testType}_{run_id}_summary.json"
    raw_path = f"{base}/{testType}_{run_id}_raw.json"

    result.update(load_k6_summary(summary_path))
    result["raw_events"] = len(load_k6_raw(raw_path))

    # -------------------------------------------------
    # PROMETHEUS
    # -------------------------------------------------
    prometheus_metrics = [
        "cpu",
        "memory",
        "network_rx",
        "network_tx",
        "disk_read",
        "disk_write",
        "node_cpu",
        "node_memory",
        "node_load",
        "restarts"
    ]

    for metric in prometheus_metrics:

        metric_data = load_prometheus_metric(
            f"{base}/{testType}_{run_id}_{metric}.csv"
        )

        metric_type = METRIC_TYPE.get(metric)

        if metric_data is None:

            result[f"{metric}_avg"] = None
            result[f"{metric}_max"] = None
            result[f"{metric}_min"] = None
            continue

        if metric_type in ["cluster_utilization", "node_utilization"]:

            result[f"{metric}_avg"] = metric_data["avg"]
            result[f"{metric}_max"] = metric_data["max"]
            result[f"{metric}_min"] = metric_data["min"]

        elif metric_type == "throughput":

            result[f"{metric}_avg"] = metric_data["avg"]
            result[f"{metric}_max"] = metric_data["max"]

        elif metric_type == "counter":

            result[metric] = metric_data["max"]

        else:
            result[f"{metric}_max"] = metric_data["max"]

    # -------------------------------------------------
    # SOAK
    # -------------------------------------------------
    if testType == "soak":
        result.update(extract_soak_trends(base, testType, run_id))

    # -------------------------------------------------
    # CHAOS EXTENSION (nur wenn chaos test)
    # -------------------------------------------------

    if testClass == "chaos":

        recovery_path = f"{base}/{testType}_{run_id}_recovery.json"

        chaos_metrics = process_chaos_metrics(
            summary_path,
            recovery_path
        )

        result.update(chaos_metrics)

    # -------------------------------------------------
    # SCORE
    # -------------------------------------------------
    result["reliability_score"] = calculate_score_by_type(
        testClass,
        testType,
        result
    )

    # -------------------------------------------------
    # RECOMMENDATIONS
    # -------------------------------------------------
    result["recommendations"] = generate_recommendations(result)

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------
    output = f"{base}/summary_{run_id}_final.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Saved summary: {output}")

def analyze_update_results(
        scenario,
        env,
        testType,
        run_id,
        testClass
):
    """
    UPDATE TEST ANALYSIS (LEAN VERSION)

    - NO Prometheus / Grafana dependency
    - OPTIONAL chaos metrics (recovery + availability)
    - FULLY k6-driven
    """

    base = f"results/{env}/{testClass}/{scenario}/{testType}"

    result = {
        "environment": env,
        "scenario": scenario,
        "testType": testType,
        "testClass": testClass,
        "run": run_id
    }

    # =================================================
    # K6 SUMMARY (PRIMARY SOURCE)
    # =================================================
    summary_path = f"{base}/{testType}_{run_id}_summary.json"
    raw_path = f"{base}/{testType}_{run_id}_raw.json"

    result.update(load_k6_summary(summary_path))
    result["raw_events"] = len(load_k6_raw(raw_path))

    # =================================================
    # BASIC DERIVED METRICS
    # =================================================
    total = result.get("requests_total") or 0
    failed_rate = result.get("error_rate") or 0

    result["success_rate"] = (1 - failed_rate) if total > 0 else None

    latency_avg = result.get("latency_avg")
    latency_p95 = result.get("latency_p95")

    result["latency_spread"] = (
        (latency_p95 - latency_avg)
        if latency_avg and latency_p95
        else None
    )

    # =================================================
    # OPTIONAL CHAOS METRICS (SAFE)
    # =================================================
    recovery_path = f"{base}/{testType}_{run_id}_recovery.json"

    chaos_metrics = process_chaos_metrics(
        summary_path,
        recovery_path
    )

    # nur hinzufügen wenn wirklich etwas da ist
    if chaos_metrics:
        result.update(chaos_metrics)

    # =================================================
    # SCORE (UPDATE MODE)
    # =================================================
    result["reliability_score"] = calculate_score_by_type(
        testClass,
        testType,
        result
    )

    # =================================================
    # RECOMMENDATIONS
    # =================================================
    result["recommendations"] = generate_recommendations(result)

    # =================================================
    # SAVE
    # =================================================
    output = f"{base}/summary_{run_id}_final.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Saved summary: {output}")