import json
import os
from collections import defaultdict

BASE = "results"


def load_json(path):
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f)


def collect(env):
    data = defaultdict(list)

    path = os.path.join(BASE, env)

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith("_final.json"):
                full = os.path.join(root, file)
                content = load_json(full)

                if content:
                    key = f"{content['scenario']}:{content['testType']}"
                    data[key].append(content)

    return data


def avg(values, key):
    vals = [v.get(key) for v in values if v.get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def build_report():
    docker = collect("docker")
    k3s = collect("k3s")

    report = {}

    all_keys = set(docker.keys()) | set(k3s.keys())

    for key in all_keys:
        report[key] = {
            "docker_p95": avg(docker.get(key, []), "latency_p95"),
            "k3s_p95": avg(k3s.get(key, []), "latency_p95"),
        }

    out = "results/benchmark_report.json"

    with open(out, "w") as f:
        json.dump(report, f, indent=2)

    return out