import requests

from src.config.config import load_environment


def get_annotations(env):

    cfg = load_environment(env)

    headers = {
        "Authorization": f"Bearer {cfg['GRAFANA_TOKEN']}"
    }

    url = f"{cfg['GRAFANA_URL']}/api/annotations"

    res = requests.get(url, headers=headers)

    return res.json()


def get_test_window(scenario, env, testType, run_id, testClass):

    annotations = get_annotations(env)

    start = None
    end = None

    for ann in annotations:

        tags = ann.get("tags", [])

        required_tags = [
            f"scenario:{scenario}",
            f"env:{env}",
            f"type:{testType}",
            f"class:{testClass}",
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

def cleanup_annotations(env, scenario, testType, run_id, testClass):

    cfg = load_environment(env)

    annotations = get_annotations(env)

    required_tags = [
        f"scenario:{scenario}",
        f"env:{env}",
        f"type:{testType}",
        f"class:{testClass}",
        f"run:{run_id}"
    ]

    headers = {
        "Authorization": f"Bearer {cfg['GRAFANA_TOKEN']}",
        "Content-Type": "application/json"
    }

    deleted = 0

    for ann in annotations:

        tags = ann.get("tags", [])

        if all(tag in tags for tag in required_tags):

            annotation_id = ann["id"]

            url = f"{cfg['GRAFANA_URL']}/api/annotations/{annotation_id}"

            response = requests.delete(url, headers=headers)

            if response.status_code == 200:
                deleted += 1
                print(f"Deleted annotation {annotation_id}")
            else:
                print(
                    f"Failed to delete {annotation_id}: "
                    f"{response.status_code} - {response.text}"
                )

    print(f"Cleanup finished. Deleted: {deleted}")