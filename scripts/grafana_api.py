import requests

from config import load_environment


def get_annotations(env):

    cfg = load_environment(env)

    headers = {
        "Authorization": f"Bearer {cfg['GRAFANA_TOKEN']}"
    }

    url = f"{cfg['GRAFANA_URL']}/api/annotations"

    res = requests.get(url, headers=headers)

    return res.json()


def get_test_window(scenario, env, testType, run_id):

    annotations = get_annotations(env)

    start = None
    end = None

    for ann in annotations:

        tags = ann.get("tags", [])

        required_tags = [
            f"scenario:{scenario}",
            f"env:{env}",
            f"type:{testType}",
            f"run:{run_id}"
        ]

        if all(tag in tags for tag in required_tags):

            if ann["text"] == "START":
                start = ann["time"]

            if ann["text"] == "END":
                end = ann["time"]

    if start is None or end is None:
        raise Exception("Missing START or END annotation")

    return start / 1000, end / 1000