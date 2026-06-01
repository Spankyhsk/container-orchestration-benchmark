import requests
import csv
import os

from src.config.config import load_environment

QUERIES = {

    # =================================================
    # CPU (Cluster Utilization – Docker vs Kubernetes Vergleich)
    # =================================================
    "cpu": {

        # =================================================
        # Docker:
        # App CPU usage / Host CPU capacity
        # =================================================
        "docker":
            '''
            sum(rate(container_cpu_usage_seconds_total{name!=""}[1m]))
            /
            count(node_cpu_seconds_total{mode="system"})
            ''',

        # =================================================
        # Kubernetes:
        # App CPU usage / Cluster CPU capacity
        # =================================================
        "k3s":
            '''
            sum(rate(container_cpu_usage_seconds_total{
                namespace=~"codetask|mongodb",
                container!="",
                pod!=""
            }[1m]))
            /
            sum(machine_cpu_cores)
            '''
    },


    # =================================================
    # MEMORY (Cluster Utilization)
    # =================================================
    "memory": {

        "docker":
            '''
            sum(container_memory_working_set_bytes{name!=""})
            /
            sum(node_memory_MemTotal_bytes)
            ''',

        "k3s":
            '''
            sum(container_memory_working_set_bytes{
                namespace=~"codetask|mongodb",
                container!="",
                pod!=""
            })
            /
            sum(node_memory_MemTotal_bytes)
            '''
    },


    # =================================================
    # NETWORK (Throughput)
    # =================================================
    "network_rx": {

        "docker":
            'sum(rate(container_network_receive_bytes_total{name!=""}[1m]))',

        "k3s":
            'sum(rate(container_network_receive_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m]))'
    },

    "network_tx": {

        "docker":
            'sum(rate(container_network_transmit_bytes_total{name!=""}[1m]))',

        "k3s":
            'sum(rate(container_network_transmit_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m]))'
    },


    # =================================================
    # DISK (I/O throughput)
    # =================================================
    "disk_read": {

        "docker":
            'sum(rate(container_fs_reads_bytes_total{name!=""}[1m]))',

        "k3s":
            'sum(rate(container_fs_reads_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m]))'
    },

    "disk_write": {

        "docker":
            'sum(rate(container_fs_writes_bytes_total{name!=""}[1m]))',

        "k3s":
            'sum(rate(container_fs_writes_bytes_total{namespace=~"codetask|mongodb",pod!=""}[1m]))'
    },


    # =================================================
    # NODE CPU (WORST NODE – normalized per core)
    # =================================================
    "node_cpu": {

        "docker":
            '''
            (
                sum(rate(node_cpu_seconds_total{mode!="idle"}[1m]))
                /
                count(node_cpu_seconds_total{mode="system"})
            )
            ''',

        "k3s":
            '''
            max(
                (
                    sum by(instance)(
                        rate(node_cpu_seconds_total{mode!="idle"}[1m])
                    )
                    /
                    count by(instance)(
                        node_cpu_seconds_total{mode="system"}
                    )
                )
            )
            '''
    },


    # =================================================
    # NODE MEMORY (WORST NODE – utilization 0..1)
    # =================================================
    "node_memory": {

        "docker":
            '''
            1 - (
                node_memory_MemAvailable_bytes
                /
                node_memory_MemTotal_bytes
            )
            ''',

        "k3s":
            '''
            max(
                1 - (
                    node_memory_MemAvailable_bytes
                    /
                    node_memory_MemTotal_bytes
                )
            )
            '''
    },


    # =================================================
    # NODE LOAD (WORST NODE – normalized per core)
    # =================================================
    "node_load": {

        # =================================================
        # Docker (normalized per core)
        # =================================================
        "docker": '''
        node_load1
        /
        scalar(
            count(node_cpu_seconds_total{mode="system"})
        )
    ''',

        # =================================================
        # Kubernetes (worst node normalized)
        # =================================================
        "k3s": '''
        max(
            node_load1
        )
        /
        avg(
            count by(instance)(
                node_cpu_seconds_total{mode="system"}
            )
        )
    '''
    },


    # =================================================
    # RESTARTS (cluster instability signal)
    # =================================================
    "restarts": {

        "docker":
            'sum(changes(container_start_time_seconds{name!=""}[5m]))',

        "k3s":
            'sum(increase(kube_pod_container_status_restarts_total{namespace=~"codetask|mongodb"}[5m]))'
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

    #if einbauen
    result_dir = f"results/{env}/{testClass}/{scenario}/{testType}"

    os.makedirs(result_dir, exist_ok=True)

    for name in QUERIES.keys():

        print(f"Exporting {name}...")

        query = get_query(name, env)

        data = query_range(env, query, start, end)

        # -----------------------------
        # SAFETY CHECK
        # -----------------------------
        if (
            not data
            or data.get("status") != "success"
            or "data" not in data
            or "result" not in data["data"]
        ):
            print(f"[WARN] Invalid Prometheus response for {name}")
            continue

        save_csv(
        f"{result_dir}/{testType}_{run_id}_{name}.csv",
            data
        )

        print(f"Saved {name}")