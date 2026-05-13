import os
from dotenv import load_dotenv

def load_environment(env):

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    env_file = os.path.join(base_dir, f".env.{env}")

    load_dotenv(env_file)

    return {
        "PROM_URL": os.getenv("PROM_URL"),      # SSH Tunnel
        "GRAFANA_URL": os.getenv("GRAFANA_URL"), # SSH Tunnel
        "GRAFANA_TOKEN": os.getenv("GRAFANA_TOKEN")
    }