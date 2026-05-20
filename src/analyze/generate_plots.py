import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import ast


# =================================================
# METRIC SEMANTIC LAYER (MUSS ZU ANALYZE_RESULTS PASSEN)
# =================================================

METRIC_TYPE = {

    # Cluster Utilization (0–1)
    "cpu": "utilization_cluster",
    "memory": "utilization_cluster",

    # Node Utilization (0–1)
    "node_cpu": "utilization_node",
    "node_memory": "utilization_node",

    # Node Load (ABSOLUT)
    "node_load": "absolute",

    # Throughput
    "network_rx": "throughput",
    "network_tx": "throughput",
    "disk_read": "throughput",
    "disk_write": "throughput",

    # Counter
    "restarts": "counter"
}


# =================================================
# LOAD METRIC CSV
# =================================================

def load_metric(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    def safe_parse(x):
        try:
            return ast.literal_eval(x) if isinstance(x, str) else {}
        except Exception:
            return {}

    df["metric"] = df["metric"].apply(safe_parse)

    def extract_label(metric):

        if not isinstance(metric, dict):
            return "all"

        service = metric.get("app") or metric.get("service")

        if service:
            return f"SERVICE:{service}"

        if "instance" in metric:

            instance = metric.get("instance", "")

            if "node-exporter" in instance:
                return f"NODE:{instance.split('-node-exporter')[0]}"

            if ":" in instance:
                return f"NODE:{instance.split(':')[0]}"

            return f"NODE:{instance}"

        return (
            "POD:" + metric.get("pod")
            if metric.get("pod")
            else "CONT:" + metric.get("container")
            if metric.get("container")
            else metric.get("name")
                 or "all"
        )

    df["label"] = df["metric"].apply(extract_label)

    df["timestamp"] = pd.to_datetime(
        pd.to_numeric(df["timestamp"], errors="coerce"),
        unit="s",
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Berlin")

    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df = df.dropna(subset=["timestamp", "value"])
    df = df.sort_values("timestamp")

    return df


# =================================================
# PLOT METRIC (NORMALIZATION AWARE)
# =================================================

def plot_metric(df, title, ylabel, output, metric_type=None):

    plt.figure(figsize=(14, 6))

    for label, group in df.groupby("label"):

        group = group.sort_values("timestamp")

        plt.plot(group["timestamp"], group["value"], label=label)

    # -----------------------------
    # Y-SCALE LOGIC (IMPORTANT)
    # -----------------------------

    if metric_type in ["utilization_cluster", "utilization_node"]:
        plt.ylim(0, 1.05)

    plt.legend(
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=7
    )

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)

    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()


# =================================================
# K6 TIMESERIES
# =================================================

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


def extract_k6_timeseries(df, metric_name):

    metric_df = df[df["metric"] == metric_name].copy()

    if metric_df.empty:
        return None

    metric_df["value"] = metric_df["data"].apply(
        lambda x: x.get("value") if isinstance(x, dict) else None
    )

    metric_df["timestamp"] = metric_df["data"].apply(
        lambda x: x.get("time") if isinstance(x, dict) else None
    )

    metric_df["value"] = pd.to_numeric(metric_df["value"], errors="coerce")

    metric_df["timestamp"] = pd.to_datetime(
        metric_df["timestamp"],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Berlin")

    metric_df = metric_df.dropna(subset=["timestamp", "value"])

    return metric_df.sort_values("timestamp")


def plot_k6_metric(df, title, ylabel, output):

    plt.figure(figsize=(14, 6))

    plt.plot(df["timestamp"], df["value"])

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)

    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()


# =================================================
# MAIN
# =================================================

def generate_plots(scenario, env, testType, run_id, testClass):

    base = f"results/{env}/{testClass}/{scenario}/{testType}"

    metrics = {

        "cpu": ("Container CPU Usage", "ratio"),
        "memory": ("Container Memory Usage", "ratio"),

        "network_rx": ("Network RX", "bytes/s"),
        "network_tx": ("Network TX", "bytes/s"),
        "disk_read": ("Disk Read", "bytes/s"),
        "disk_write": ("Disk Write", "bytes/s"),

        "node_cpu": ("Node CPU Usage", "ratio"),
        "node_memory": ("Node Memory Usage", "ratio"),
        "node_load": ("Node Load", "load avg"),

        "restarts": ("Container Restarts", "count")
    }

    for metric, (label, unit) in metrics.items():

        csv_path = f"{base}/{testType}_{run_id}_{metric}.csv"

        df = load_metric(csv_path)

        if df is None:
            continue

        output = f"{base}/{testType}_{run_id}_{metric}.png"

        metric_type = METRIC_TYPE.get(metric)

        plot_metric(
            df=df,
            title=f"{label} - {env} - {scenario} - {testType}",
            ylabel=unit,
            output=output,
            metric_type=metric_type
        )

        print(f"Generated plot: {output}")

    # =================================================
    # K6
    # =================================================

    raw_path = f"{base}/{testType}_{run_id}_raw.json"

    k6_df = load_k6_raw(raw_path)

    if k6_df is None:
        return

    latency = extract_k6_timeseries(k6_df, "http_req_duration")

    if latency is not None:
        plot_k6_metric(
            latency,
            f"k6 Latency - {env}",
            "ms",
            f"{base}/k6_latency_{run_id}.png"
        )

    reqs = extract_k6_timeseries(k6_df, "http_reqs")

    if reqs is not None:
        plot_k6_metric(
            reqs,
            f"k6 Requests - {env}",
            "count",
            f"{base}/k6_requests_{run_id}.png"
        )

    errors = extract_k6_timeseries(k6_df, "http_req_failed")

    if errors is not None:
        plot_k6_metric(
            errors,
            f"k6 Errors - {env}",
            "rate",
            f"{base}/k6_errors_{run_id}.png"
        )