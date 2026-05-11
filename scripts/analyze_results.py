import json
import pandas as pd
import os


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

    # LATENCY
    if "http_req_duration" in metrics:
        values = metrics["http_req_duration"].get("values", {})
        summary["latency_avg"] = values.get("avg")
        summary["latency_p95"] = values.get("p(95)")
        summary["latency_p99"] = values.get("p(99)")

    # ERROR RATE
    if "http_req_failed" in metrics:
        summary["error_rate"] = metrics["http_req_failed"].get("values", {}).get("rate")

    # REQUESTS
    if "http_reqs" in metrics:
        values = metrics["http_reqs"].get("values", {})
        summary["requests_total"] = values.get("count")
        summary["requests_rate"] = values.get("rate")

    return summary


def load_prometheus_metric(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    df["value"] = pd.to_numeric(df["value"])

    return {
        "avg": float(df["value"].mean()),
        "max": float(df["value"].max()),
        "min": float(df["value"].min())
    }


def calculate_reliability_score(summary):

    score = 100

    # -------------------------------------------------
    # LATENCY
    # -------------------------------------------------

    if summary.get("latency_p95"):

        if summary["latency_p95"] > 1200:
            score -= 30

        elif summary["latency_p95"] > 800:
            score -= 15

    # -------------------------------------------------
    # ERROR RATE
    # -------------------------------------------------

    if summary.get("error_rate"):

        if summary["error_rate"] > 0.05:
            score -= 40

        elif summary["error_rate"] > 0.01:
            score -= 20

    # -------------------------------------------------
    # CPU
    # -------------------------------------------------

    if summary.get("cpu_max"):

        if summary["cpu_max"] > 0.95:
            score -= 10

    # -------------------------------------------------
    # MEMORY
    # -------------------------------------------------

    if summary.get("memory_max"):

        if summary["memory_max"] > 0.95:
            score -= 10

    return max(score, 0)

def load_k6_raw(path):

    if not os.path.exists(path):
        return []

    data = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))

    return data

def analyze_results(scenario, env, testType, run_id):

    base = f"results/{env}/load/{scenario}/{testType}"

    result = {
        "environment": env,
        "scenario": scenario,
        "testType": testType,
        "run": run_id
    }

    # -------------------------------------------------
    # K6 SUMMARY (FIXED PATH)
    # -------------------------------------------------

    summary_path = f"{base}/summary_{run_id}.json"
    raw_path = f"{base}/raw_{run_id}.json"

    k6_summary = load_k6_summary(summary_path)
    k6_raw = load_k6_raw(raw_path)

    result.update(k6_summary)

    # optional: raw size debug metric
    result["raw_events"] = len(k6_raw)

    # -------------------------------------------------
    # CPU
    # -------------------------------------------------

    cpu = load_prometheus_metric(f"{base}/{testType}_{run_id}_cpu.csv")
    if cpu:
        result["cpu_avg"] = cpu["avg"]
        result["cpu_max"] = cpu["max"]

    # -------------------------------------------------
    # MEMORY
    # -------------------------------------------------

    memory = load_prometheus_metric(f"{base}/{testType}_{run_id}_memory.csv")
    if memory:
        result["memory_avg"] = memory["avg"]
        result["memory_max"] = memory["max"]

    # -------------------------------------------------
    # NETWORK RX
    # -------------------------------------------------

    network_rx = load_prometheus_metric(f"{base}/{testType}_{run_id}_network_rx.csv")
    if network_rx:
        result["network_rx_avg"] = network_rx["avg"]
        result["network_rx_max"] = network_rx["max"]

    # -------------------------------------------------
    # NETWORK TX
    # -------------------------------------------------

    network_tx = load_prometheus_metric(f"{base}/{testType}_{run_id}_network_tx.csv")
    if network_tx:
        result["network_tx_avg"] = network_tx["avg"]
        result["network_tx_max"] = network_tx["max"]

    # -------------------------------------------------
    # RELIABILITY SCORE
    # -------------------------------------------------

    result["reliability_score"] = calculate_reliability_score(result)

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    output = f"{base}/summary_{run_id}_final.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Saved summary: {output}")