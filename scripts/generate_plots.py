import pandas as pd
import matplotlib.pyplot as plt
import os
import json


# -------------------------------------------------
# LOAD INFRA METRICS (CSV)
# -------------------------------------------------

def load_metric(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


# -------------------------------------------------
# LOAD K6 RAW (NDJSON)
# -------------------------------------------------

def load_k6_raw(raw_path):

    if not os.path.exists(raw_path):
        return None

    data = []

    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))

    if not data:
        return None

    return pd.DataFrame(data)


# -------------------------------------------------
# EXTRACT K6 TIMESERIES
# -------------------------------------------------

def extract_k6_timeseries(df, metric_name):

    metric_df = df[df["metric"] == metric_name].copy()

    if metric_df.empty:
        return None

    metric_df["value"] = pd.to_numeric(metric_df["value"], errors="coerce")

    metric_df["timestamp"] = pd.to_datetime(metric_df["time"], errors="coerce")

    return metric_df


# -------------------------------------------------
# PLOT GENERIC METRIC (CSV)
# -------------------------------------------------

def plot_metric(df, title, ylabel, output):

    plt.figure(figsize=(12, 5))

    plt.plot(df["timestamp"], df["value"])

    plt.title(title)
    plt.xlabel("Timestamp")
    plt.ylabel(ylabel)

    plt.tight_layout()

    plt.savefig(output)
    plt.close()


# -------------------------------------------------
# PLOT K6 METRIC (RAW)
# -------------------------------------------------

def plot_k6_metric(df, title, ylabel, output):

    plt.figure(figsize=(12, 5))

    plt.plot(df["timestamp"], df["value"])

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)

    plt.tight_layout()

    plt.savefig(output)
    plt.close()


# -------------------------------------------------
# MAIN ENTRY
# -------------------------------------------------

def generate_plots(scenario, env, testType, run_id):

    base = f"results/{env}/load/{scenario}/{testType}"

    # =================================================
    # 1. INFRASTRUCTURE METRICS
    # =================================================

    metrics = {
        "cpu": "CPU Usage",
        "memory": "Memory Usage",
        "network_rx": "Network RX",
        "network_tx": "Network TX",
        "disk_read": "Disk Read",
        "disk_write": "Disk Write"
    }

    for metric, label in metrics.items():

        csv_path = f"{base}/{testType}_{run_id}_{metric}.csv"

        df = load_metric(csv_path)

        if df is None:
            continue

        output = f"{base}/{testType}_{run_id}_{metric}.png"

        plot_metric(
            df=df,
            title=f"{label} - {env} - {scenario} - {testType} - {run_id}",
            ylabel=label,
            output=output
        )

        print(f"Generated plot: {output}")

    # =================================================
    # 2. K6 RAW METRICS
    # =================================================

    raw_path = f"{base}/{testType}_{run_id}_raw.json"

    k6_df = load_k6_raw(raw_path)

    if k6_df is None:
        print("No k6 raw data found")
        return

    # -------------------------------------------------
    # LATENCY
    # -------------------------------------------------

    latency = extract_k6_timeseries(k6_df, "http_req_duration")

    if latency is not None:
        plot_k6_metric(
            latency,
            f"k6 Latency - {env} - {scenario} - {testType} - {run_id}",
            "ms",
            f"{base}/k6_latency_{run_id}.png"
        )
        print("Generated k6 latency plot")

    # -------------------------------------------------
    # REQUESTS
    # -------------------------------------------------

    reqs = extract_k6_timeseries(k6_df, "http_reqs")

    if reqs is not None:
        plot_k6_metric(
            reqs,
            f"k6 Requests - {env} - {scenario} - {testType} - {run_id}",
            "count",
            f"{base}/k6_requests_{run_id}.png"
        )
        print("Generated k6 requests plot")

    # -------------------------------------------------
    # ERRORS
    # -------------------------------------------------

    errors = extract_k6_timeseries(k6_df, "http_req_failed")

    if errors is not None:
        plot_k6_metric(
            errors,
            f"k6 Errors - {env} - {scenario} - {testType} - {run_id}",
            "rate",
            f"{base}/k6_errors_{run_id}.png"
        )
        print("Generated k6 error plot")