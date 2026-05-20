import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import ast
from collections import defaultdict


# =================================================
# METRIC META
# =================================================

METRIC_INFO = {
    "cpu": {"title": "CPU Usage", "ylabel": "%"},
    "memory": {"title": "Memory Usage", "ylabel": "Bytes"},
    "network_rx": {"title": "Network RX", "ylabel": "MB/s"},
    "network_tx": {"title": "Network TX", "ylabel": "MB/s"},
    "disk_read": {"title": "Disk Read", "ylabel": "MB/s"},
    "disk_write": {"title": "Disk Write", "ylabel": "MB/s"},
    "node_cpu": {"title": "Node CPU", "ylabel": "%"},
    "node_memory": {"title": "Node Memory", "ylabel": "Bytes"},
    "node_load": {"title": "Node Load", "ylabel": "Load"},
    "restarts": {"title": "Restarts", "ylabel": "count"},
}


# =================================================
# LOAD SINGLE CSV
# =================================================

def load_df(path):
    if not os.path.exists(path):
        print(f"Missing CSV: {path}")
        return None

    df = pd.read_csv(path)

    if df.empty:
        return None

    def extract_instance(x):
        try:
            d = ast.literal_eval(x)
            return d.get("instance", "unknown")
        except:
            return "unknown"

    df["instance"] = df["metric"].apply(extract_instance)

    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df = df.dropna(subset=["timestamp", "value"])

    return df


# =================================================
# RUN ID FIX (WICHTIG!)
# =================================================

def extract_run_id(filename):
    # smoke_0_node_load.csv -> 0
    match = re.search(r"_(\d+)_", filename)
    return match.group(1) if match else "0"


def attach_run_id(df, file_path):
    run_id = extract_run_id(os.path.basename(file_path))
    df = df.copy()
    df["run"] = run_id
    return df


# =================================================
# MULTI FILE LOADER (FIXED)
# =================================================

def load_multi(files):
    dfs = []

    for f in files:
        df = load_df(f)
        if df is not None:
            df = attach_run_id(df, f)
            dfs.append(df)

    if not dfs:
        return None

    return pd.concat(dfs, ignore_index=True)


# =================================================
# DURATION PER RUN (CRITICAL FIX)
# =================================================

def add_duration(df):
    df = df.copy()

    df["duration"] = df.groupby(["run", "instance"])["timestamp"].transform(
        lambda x: x - x.min()
    )

    return df


# =================================================
# NORMALIZATION
# =================================================

def normalize(metric, df):
    df = df.copy()

    if "cpu" in metric:
        df["value"] *= 100

    elif "memory" in metric:
        pass

    elif "network" in metric or "disk" in metric:
        df["value"] /= 1024 ** 2

    return df


# =================================================
# FIND FILES
# =================================================

def find_metric_files(base_path, metric):
    return [
        os.path.join(base_path, f)
        for f in os.listdir(base_path)
        if f.endswith(".csv") and metric in f
    ]


# =================================================
# PLOT FIXED (NO MORE VERTICAL LINES)
# =================================================

def plot_compare(metric, docker_files, k3s_files, output):

    docker_df = load_multi(docker_files)
    k3s_df = load_multi(k3s_files)

    if docker_df is None or k3s_df is None:
        print(f"Skipping plot for {metric}")
        return None

    docker_df = normalize(metric, docker_df)
    k3s_df = normalize(metric, k3s_df)

    docker_df = add_duration(docker_df)
    k3s_df = add_duration(k3s_df)

    info = METRIC_INFO.get(metric, {"title": metric, "ylabel": metric})

    plt.figure(figsize=(14, 6))

    # =================================================
    # DOCKER: run + instance separation
    # =================================================
    for (run, inst), g in docker_df.groupby(["run", "instance"]):
        g = g.sort_values("duration")
        plt.plot(
            g["duration"],
            g["value"],
            alpha=0.35,
            linewidth=1
        )

    # =================================================
    # K3S
    # =================================================
    for (run, inst), g in k3s_df.groupby(["run", "instance"]):
        g = g.sort_values("duration")
        plt.plot(
            g["duration"],
            g["value"],
            alpha=0.35,
            linewidth=1
        )

    plt.title(info["title"])
    plt.xlabel("Test Duration (s)")
    plt.ylabel(info["ylabel"])
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()

    print(f"Generated: {output}")

    return output


# =================================================
# MAIN
# =================================================

def generate_comparison_plots(docker_base_path, k3s_base_path, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    metrics = [
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

    files = []

    for metric in metrics:

        docker_files = find_metric_files(docker_base_path, metric)
        k3s_files = find_metric_files(k3s_base_path, metric)

        if not docker_files or not k3s_files:
            print(f"Missing CSV for metric: {metric}")
            continue

        output = os.path.join(output_dir, f"{metric}_compare.png")

        img = plot_compare(metric, docker_files, k3s_files, output)

        if img:
            files.append(img)

    return files