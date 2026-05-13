import json
import pandas as pd
import os

from src.evaluation.scoring import (
    calculate_load_score,
    calculate_soak_score
)
from src.evaluation.recommendations import generate_recommendations


# -------------------------------------------------
# TIMESERIES LOADER
# -------------------------------------------------

def load_timeseries(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    return df


# -------------------------------------------------
# K6 SUMMARY
# -------------------------------------------------

def load_k6_summary(path):

    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = {
        "latency_avg": None,
        "latency_p95": None,
        "latency_p99": None,
        "error_rate": None,
        "requests_total": None,
        "requests_rate": None
    }

    metrics = data.get("metrics", {})

    if "http_req_duration" in metrics:
        values = metrics["http_req_duration"].get("values", {})
        summary["latency_avg"] = values.get("avg")
        summary["latency_p95"] = values.get("p(95)")
        summary["latency_p99"] = values.get("p(99)")

    if "http_req_failed" in metrics:
        summary["error_rate"] = metrics["http_req_failed"].get("values", {}).get("rate")

    if "http_reqs" in metrics:
        values = metrics["http_reqs"].get("values", {})
        summary["requests_total"] = values.get("count")
        summary["requests_rate"] = values.get("rate")

    return summary


# -------------------------------------------------
# PROMETHEUS LOADER
# -------------------------------------------------

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

    return {
        "avg": float(df["value"].mean()),
        "max": float(df["value"].max()),
        "min": float(df["value"].min())
    }


# -------------------------------------------------
# RAW K6
# -------------------------------------------------

def load_k6_raw(path):

    if not os.path.exists(path):
        return []

    data = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))

    return data


# -------------------------------------------------
# SCORE ROUTER
# -------------------------------------------------

def calculate_score_by_type(testClass, testType, result):

    # LOAD FAMILY
    if testClass == "load":

        # SOAK = special case of load
        if testType == "soak":
            return calculate_soak_score(result)

        return calculate_load_score(result)

    # CHAOS
    elif testClass == "chaos":
        return calculate_load_score(result)  # später ersetzen

    # UPDATE
    elif testClass == "update":
        return calculate_load_score(result)  # später ersetzen

    return calculate_load_score(result)

# -------------------------------------------------
# Calculate trend for soak
# -------------------------------------------------
def calculate_trend_percent(df):

    if df is None or df.empty:
        return 0

    df = df.sort_values("timestamp")

    df = df.dropna(subset=["value", "timestamp"])

    start = df["value"].iloc[0]
    end = df["value"].iloc[-1]

    if start == 0:
        return 0

    return ((end - start) / start) * 100

def extract_soak_trends(base, testType, run_id):
    """
    Berechnet echte Trends für Soak Tests aus Timeseries CSVs
    """

    trends = {}

    # ----------------------------
    # MEMORY TREND
    # ----------------------------
    memory_df = load_timeseries(
        f"{base}/{testType}_{run_id}_memory.csv"
    )

    if memory_df is not None:
        trends["memory_growth_percent"] = calculate_trend_percent(memory_df)

    # ----------------------------
    # CPU TREND
    # ----------------------------
    cpu_df = load_timeseries(
        f"{base}/{testType}_{run_id}_cpu.csv"
    )

    if cpu_df is not None:
        trends["cpu_growth_percent"] = calculate_trend_percent(cpu_df)

    # ----------------------------
    # LATENCY TREND (k6)
    # ----------------------------
    latency_df = load_timeseries(
        f"{base}/k6_latency_timeseries_{run_id}.csv"
    )

    if latency_df is not None:
        trends["latency_growth_percent"] = calculate_trend_percent(latency_df)

    return trends

# -------------------------------------------------
# ANALYZE RESULTS
# -------------------------------------------------

def analyze_results(scenario, env, testType, run_id, testClass):

    base = f"results/{env}/{testClass}/{scenario}/{testType}"

    result = {
        "environment": env,
        "scenario": scenario,
        "testType": testType,
        "testClass": testClass,
        "run": run_id
    }

    # -------------------------------------------------
    # K6 SUMMARY
    # -------------------------------------------------

    summary_path = f"{base}/{testType}_{run_id}_summary.json"
    raw_path = f"{base}/{testType}_{run_id}_raw.json"

    k6_summary = load_k6_summary(summary_path)
    k6_raw = load_k6_raw(raw_path)

    result.update(k6_summary)
    result["raw_events"] = len(k6_raw)

    # -------------------------------------------------
    # PROMETHEUS METRICS
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
        "node_load"
    ]

    for metric in prometheus_metrics:

        metric_data = load_prometheus_metric(
            f"{base}/{testType}_{run_id}_{metric}.csv"
        )

        if metric_data:
            result[f"{metric}_avg"] = metric_data["avg"]
            result[f"{metric}_max"] = metric_data["max"]
            result[f"{metric}_min"] = metric_data["min"]

    # -------------------------------------------------
    # SOAK FEATURES (nur wenn soak)
    # -------------------------------------------------

    if testType == "soak":

        # Platzhalter (später echte Trendanalyse)
        trends = extract_soak_trends(base, testType, run_id)
        result.update(trends)

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