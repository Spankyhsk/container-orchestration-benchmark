import requests
import csv
import os

from config import load_environment

QUERIES = {

    # CPU
    "cpu":
        'sum(rate(container_cpu_usage_seconds_total[1m])) by (name)',

    # RAM
    "memory":
        'container_memory_usage_bytes',

    # Network RX
    "network_rx":
        'rate(container_network_receive_bytes_total[1m])',

    # Network TX
    "network_tx":
        'rate(container_network_transmit_bytes_total[1m])',

    # Disk Read
    "disk_read":
        'rate(container_fs_reads_bytes_total[1m])',

    # Disk Write
    "disk_write":
        'rate(container_fs_writes_bytes_total[1m])'
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


def export_metrics(env, scenario, testType, run_id, start, end):

    result_dir = f"results/{env}/load/{scenario}/{testType}"

    os.makedirs(result_dir, exist_ok=True)

    for name, query in QUERIES.items():

        print(f"Exporting {name}...")

        data = query_range(env, query, start, end)

        save_csv(
            f"{result_dir}/{testType}_{run_id}_{name}.csv",
            data
        )

        print(f"Saved {name}")