import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import ast


# =================================================
# INFRA METRICS LOADER (CSV)
# =================================================

def load_metric(csv_path):

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    if df.empty:
        return None

    # -------------------------------------------------
    # Metric Label Parsing (Prometheus style)
    # -------------------------------------------------
    # CSV enthält stringified dicts aus Prometheus labels
    # -> wird hier wieder in dict zurück konvertiert
    # -------------------------------------------------

    def safe_parse(x):
        try:
            return ast.literal_eval(x) if isinstance(x, str) else {}
        except Exception:
            return {}

    df["metric"] = df["metric"].apply(safe_parse)

    # -------------------------------------------------
    # Label Extraction (Grafana-like grouping)
    # -------------------------------------------------

    def extract_label(metric):

        if not isinstance(metric, dict):
            return "all"

        # -------------------------------------------------
        # NODE METRICS (SPECIAL CASE)
        # -------------------------------------------------
        # node_memory / node_load sollen echte Node Namen zeigen
        # -------------------------------------------------

        if "instance" in metric:

            instance = metric.get("instance", "")

            # node-exporter-xxxxx → nur cleaner node name
            if "node-exporter" in instance:
                return instance.split("-node-exporter")[0]

            # fallback: IP cleanup
            if ":" in instance:
                return instance.split(":")[0]

            return instance

        # stabile Priorität (wichtig für Kubernetes/Docker Mix)
        return (
                metric.get("pod")
                or metric.get("container")
                or metric.get("name")
                or metric.get("instance")
                or "all"
        )

    df["label"] = df["metric"].apply(extract_label)

    # -------------------------------------------------
    # Timestamp Conversion
    # -------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        pd.to_numeric(df["timestamp"], errors="coerce"),
        unit="s",
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Berlin")

    # -------------------------------------------------
    # Value Conversion
    # -------------------------------------------------

    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # remove invalid rows
    df = df.dropna(subset=["timestamp", "value"])

    # sort globally (important for line plotting)
    df = df.sort_values("timestamp")

    return df


# =================================================
# K6 RAW LOADER
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


# =================================================
# K6 TIMESERIES EXTRACTION
# =================================================

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

    # k6 timestamps are usually ISO strings OR epoch → safe parse
    metric_df["timestamp"] = pd.to_datetime(
        metric_df["timestamp"],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Europe/Berlin")

    metric_df = metric_df.dropna(subset=["timestamp", "value"])

    return metric_df.sort_values("timestamp")


# =================================================
# INFRA PLOT (Grafana-like multi-series)
# =================================================

def plot_metric(df, title, ylabel, output):

    plt.figure(figsize=(14, 6))

    # -------------------------------------------------
    # One line per label (Grafana behavior)
    # -------------------------------------------------
    for label, group in df.groupby("label"):

        group = group.sort_values("timestamp")

        plt.plot(
            group["timestamp"],
            group["value"],
            label=label
        )

    # -------------------------------------------------
    # Legend outside (important for many containers)
    # -------------------------------------------------
    plt.legend(
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=7
    )

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()


# =================================================
# K6 PLOT (single series)
# =================================================

def plot_k6_metric(df, title, ylabel, output):

    plt.figure(figsize=(14, 6))

    plt.plot(
        df["timestamp"],
        df["value"]
    )

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()


# =================================================
# MAIN ENTRY
# =================================================

def generate_plots(scenario, env, testType, run_id, testClass):

    base = f"results/{env}/{testClass}/{scenario}/{testType}"

    # =================================================
    # INFRASTRUCTURE METRICS
    # =================================================

    metrics = {

        # Container metrics
        "cpu": "Container CPU Usage",
        "memory": "Container Memory Usage",
        "network_rx": "Container Network RX",
        "network_tx": "Container Network TX",
        "disk_read": "Container Disk Read",
        "disk_write": "Container Disk Write",

        # Node metrics
        "node_cpu": "Node CPU Usage",
        "node_memory": "Node Memory Usage",
        "node_load": "Node Load"
    }

    for metric, label in metrics.items():

        csv_path = f"{base}/{testType}_{run_id}_{metric}.csv"

        df = load_metric(csv_path)

        if df is None:
            continue

        output = f"{base}/{testType}_{run_id}_{metric}.png"

        plot_metric(
            df=df,
            title=f"{label} - {env} - {scenario} - {testType}",
            ylabel=label,
            output=output
        )

        print(f"Generated plot: {output}")

    # =================================================
    # K6 METRICS
    # =================================================

    raw_path = f"{base}/{testType}_{run_id}_raw.json"

    k6_df = load_k6_raw(raw_path)

    if k6_df is None:
        print("No k6 raw data found")
        return

    # LATENCY
    latency = extract_k6_timeseries(k6_df, "http_req_duration")

    if latency is not None:
        plot_k6_metric(
            latency,
            f"k6 Latency - {env} - {scenario} - {testType}",
            "ms",
            f"{base}/k6_latency_{run_id}.png"
        )

    # REQUESTS
    reqs = extract_k6_timeseries(k6_df, "http_reqs")

    if reqs is not None:
        plot_k6_metric(
            reqs,
            f"k6 Requests - {env} - {scenario} - {testType}",
            "count",
            f"{base}/k6_requests_{run_id}.png"
        )

    # ERRORS
    errors = extract_k6_timeseries(k6_df, "http_req_failed")

    if errors is not None:
        plot_k6_metric(
            errors,
            f"k6 Errors - {env} - {scenario} - {testType}",
            "rate",
            f"{base}/k6_errors_{run_id}.png"
        )