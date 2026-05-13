import requests
import csv
import os

from src.config.config import load_environment

QUERIES = {

    # =================================================
    # CPU USAGE
    # =================================================
    "cpu": {
        # Docker (cAdvisor nutzt meist "name")
        "docker":
            'sum(rate(container_cpu_usage_seconds_total[1m])) by (name)',

        # Kubernetes / k3s (nur codetask + mongodb)
        "k3s":
            'sum(rate(container_cpu_usage_seconds_total{namespace=~"codetask|mongodb",container!="",pod!=""}[1m])) by (pod, container)'
    },

    # =================================================
    # MEMORY USAGE
    # =================================================
    "memory": {
        "docker":
            'sum(container_memory_usage_bytes) by (name)',

        "k3s":
            'sum(container_memory_usage_bytes{namespace=~"codetask|mongodb",container!="",pod!=""}) by (pod, container)'
    },

    # =================================================
    # NETWORK RX
    # =================================================
    "network_rx": {
        "docker":
            'sum(rate(container_network_receive_bytes_total[1m])) by (name)',

        "k3s":
            'sum(rate(container_network_receive_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m])) by (pod, container)'
    },

    # =================================================
    # NETWORK TX
    # =================================================
    "network_tx": {
        "docker":
            'sum(rate(container_network_transmit_bytes_total[1m])) by (name)',

        "k3s":
            'sum(rate(container_network_transmit_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m])) by (pod, container)'
    },

    # =================================================
    # DISK READ
    # =================================================
    "disk_read": {
        "docker":
            'sum(rate(container_fs_reads_bytes_total[1m])) by (name)',

        "k3s":
            'sum(rate(container_fs_reads_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m])) by (pod, container)'
    },

    # =================================================
    # DISK WRITE
    # =================================================
    "disk_write": {
        "docker":
            'sum(rate(container_fs_writes_bytes_total[1m])) by (name)',

        "k3s":
            'sum(rate(container_fs_writes_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m])) by (pod, container)'
    },

    # =================================================
    # NODE CPU
    # =================================================
    "node_cpu": {
        "docker":
            'sum(rate(node_cpu_seconds_total{mode!="idle"}[1m])) by (instance)',

        "k3s":
            'sum(rate(node_cpu_seconds_total{mode!="idle"}[1m])) by (instance)'
    },

    # =================================================
    # NODE MEMORY
    # =================================================
    "node_memory": {
        "docker":
            '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)',

        "k3s":
            '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)'
    },

    # =================================================
    # NODE LOAD
    # =================================================
    "node_load": {
        "docker":
            'node_load1',

        "k3s":
            'node_load1'
    }
}


def query_range(env, query, start, end):

    cfg = load_environment(env)

    url = f"{cfg['PROM_URL']}/api/v1/query_range"

    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": "15"
    }

    return requests.get(url, params=params).json()


def save_csv(path, data):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "metric",
            "timestamp",
            "value"
        ])

        for series in data["data"]["result"]:

            metric = str(series["metric"])

            for point in series["values"]:

                writer.writerow([
                    metric,
                    point[0],
                    point[1]
                ])

def get_query(metric, env):

    if metric not in QUERIES:
        raise ValueError(f"Unknown metric: {metric}")

    if env not in QUERIES[metric]:
        raise ValueError(f"Unknown env '{env}' for metric '{metric}'")

    return QUERIES[metric][env]

def export_metrics(env, scenario, testType, run_id, testClass, start, end):

    result_dir = f"results/{env}/{testClass}/{scenario}/{testType}"

    os.makedirs(result_dir, exist_ok=True)

    for name in QUERIES.keys():

        print(f"Exporting {name}...")

        query = get_query(name, env)

        data = query_range(env, query, start, end)

        save_csv(
            f"{result_dir}/{testType}_{run_id}_{name}.csv",
            data
        )

        print(f"Saved {name}")