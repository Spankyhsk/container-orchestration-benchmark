import sys
import os

# =========================================================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import json
import subprocess
import queue
import time

from nicegui import ui
from dotenv import dotenv_values

from infra.environments import DockerEnvironment, K3sEnvironment
from infra.healthchecks import wait_for_stack
from infra.registry import ConnectionState
from infra.ui_logger import UILogger


# =========================================================
# CONFIGS
# =========================================================
CONFIG_DIR = "configs"
configs = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]

STATE = ConnectionState()
LOGGER = UILogger()

terminal_queue = queue.Queue()

# =========================================================
# HELPERS
# =========================================================
def add_log(msg: str):

    timestamp = time.strftime("%H:%M:%S")
    full = f"[{timestamp}] {msg}"

    print(full)

    LOGGER.push(full)

    try:
        log_box.push(full)
    except:
        pass


def load_env(env_name: str):
    return dotenv_values(f".env.{env_name}")


def vpn_alive():

    try:
        result = subprocess.run(
            ["ping", "-n", "1", "8.8.8.8"],
            capture_output=True
        )

        return result.returncode == 0

    except:
        return False


# =========================================================
# BUTTON STATE
# =========================================================
def set_button_state(btn, ok: bool):

    color = "#16a34a" if ok else "#dc2626"

    btn.style(
        f"""
        background-color: {color};
        color: white;
        border: 2px solid {color};
        """
    )

    btn.update()


# =========================================================
# LIVE TERMINAL CAPTURE
# =========================================================
class StreamCapture:

    def __init__(self):
        self.original_stdout = sys.stdout

    def write(self, text):

        self.original_stdout.write(text)

        if text.strip():
            terminal_queue.put(text.strip())

    def flush(self):
        self.original_stdout.flush()

    def isatty(self):
        return self.original_stdout.isatty()

    def fileno(self):
        return self.original_stdout.fileno()


sys.stdout = StreamCapture()


# =========================================================
# PAGE
# =========================================================
ui.dark_mode()

with ui.column().classes("w-full items-center p-4 gap-4"):

    # =====================================================
    # HEADER
    # =====================================================
    with ui.card().classes("w-full max-w-7xl p-6"):

        ui.label(
            "Container Benchmark Automation"
        ).classes(
            "text-4xl font-bold"
        )

        status_label = ui.label(
            "Idle"
        ).classes(
            "text-lg text-blue-300 mt-2"
        )

    # =====================================================
    # CONTROL PANEL
    # =====================================================
    with ui.card().classes("w-full max-w-7xl p-6"):

        ui.label(
            "Benchmark Configuration"
        ).classes(
            "text-2xl font-bold mb-4"
        )

        with ui.row().classes(
                "w-full items-center gap-4"
        ):

            config_select = ui.select(
                configs,
                label="Config"
            ).classes("w-72")

            mode_select = ui.select(
                ["collect", "analyze", "full"],
                value="collect",
                label="Mode"
            ).classes("w-48")

            start_button = ui.button(
                "Start Benchmark"
            ).classes(
                "text-white text-lg px-6 py-2"
            )

            start_button.style(
                """
                background-color: #2563eb;
                """
            )

    # =====================================================
    # CONNECTION STATES
    # =====================================================
    with ui.card().classes("w-full max-w-7xl p-6"):

        ui.label(
            "Live Connection State"
        ).classes(
            "text-2xl font-bold mb-6"
        )

        # =================================================
        # VPN
        # =================================================
        ui.label("VPN").classes("text-xl mb-2")

        with ui.row().classes("gap-2 mb-6"):

            vpn_button = ui.button(
                "VPN"
            ).props("disable")

        # =================================================
        # SSH
        # =================================================
        ui.label("SSH Tunnels").classes("text-xl mb-2")

        with ui.grid(columns=2).classes(
                "w-full gap-3 mb-6"
        ):

            ssh_docker_grafana = ui.button(
                "SSH Docker Grafana"
            ).props("disable")

            ssh_docker_prom = ui.button(
                "SSH Docker Prometheus"
            ).props("disable")

            ssh_k3s_grafana = ui.button(
                "SSH K3s Grafana"
            ).props("disable")

            ssh_k3s_prom = ui.button(
                "SSH K3s Prometheus"
            ).props("disable")

        # =================================================
        # PORT FORWARD
        # =================================================
        ui.label("Port Forwards").classes("text-xl mb-2")

        with ui.grid(columns=2).classes(
                "w-full gap-3"
        ):

            pf_k3s_grafana = ui.button(
                "PF K3s Grafana"
            ).props("disable")

            pf_k3s_prom = ui.button(
                "PF K3s Prometheus"
            ).props("disable")

    # =====================================================
    # LOG + CONFIG
    # =====================================================
    with ui.row().classes(
            "w-full max-w-7xl gap-4"
    ):

        # =================================================
        # APP LOGS
        # =================================================
        with ui.card().classes(
                "w-1/2 p-4"
        ):

            ui.label(
                "Application Logs"
            ).classes(
                "text-2xl font-bold mb-2"
            )

            log_box = ui.log(
                max_lines=2000
            ).classes(
                "w-full h-[600px] border"
            )

        # =================================================
        # CONFIG VIEW
        # =================================================
        with ui.card().classes(
                "w-1/2 p-4"
        ):

            ui.label(
                "Current Config"
            ).classes(
                "text-2xl font-bold mb-2"
            )

            config_view = ui.code(
                "",
                language="json"
            ).classes(
                "w-full h-[600px]"
            )

    # =====================================================
    # TERMINAL WINDOW
    # =====================================================
    with ui.card().classes(
            "w-full max-w-7xl p-4"
    ):

        ui.label(
            "Terminal Output"
        ).classes(
            "text-2xl font-bold mb-2"
        )

        terminal_box = ui.log(
            max_lines=4000
        ).classes(
            "w-full h-[500px] border"
        )


# =========================================================
# BUTTON REGISTRY
# =========================================================
connection_buttons = {

    "vpn": vpn_button,

    # SSH
    "ssh-docker-grafana": ssh_docker_grafana,
    "ssh-docker-prom": ssh_docker_prom,

    "ssh-k3s-grafana": ssh_k3s_grafana,
    "ssh-k3s-prom": ssh_k3s_prom,

    # PF
    "pf-k3s-grafana": pf_k3s_grafana,
    "pf-k3s-prom": pf_k3s_prom,
}


# =========================================================
# INITIAL STATES
# =========================================================
for btn in connection_buttons.values():
    set_button_state(btn, False)


# =========================================================
# TERMINAL REFRESH
# =========================================================
def refresh_terminal():

    while not terminal_queue.empty():

        try:

            msg = terminal_queue.get_nowait()

            terminal_box.push(msg)

        except:
            pass


ui.timer(0.5, refresh_terminal)


# =========================================================
# UI REFRESH LOOP
# =========================================================
def refresh_ui():

    try:

        # VPN
        set_button_state(
            connection_buttons["vpn"],
            vpn_alive()
        )

        # reset all except vpn
        for key, btn in connection_buttons.items():

            if key == "vpn":
                continue

            set_button_state(btn, False)

        connections = STATE.all()

        # DEBUG
        # print(connections)

        for name, obj in connections.items():

            if not obj:
                continue

            try:
                status = obj.is_alive()

            except Exception as e:

                add_log(
                    f"is_alive failed for {name}: {e}"
                )

                continue

            # dict mode
            if isinstance(status, dict):

                for service_name, ok in status.items():

                    ui_key = f"{name}-{service_name}"

                    btn = connection_buttons.get(ui_key)

                    if btn:
                        set_button_state(btn, ok)

            # bool mode
            elif isinstance(status, bool):

                btn = connection_buttons.get(name)

                if btn:
                    set_button_state(btn, status)

    except Exception as e:

        print("refresh_ui failed:", e)


# refresh every 0.5 seconds
ui.timer(0.5, refresh_ui)


# =========================================================
# MAIN
# =========================================================
async def run_benchmark():

    selected = config_select.value

    if not selected:

        status_label.set_text(
            "No config selected"
        )

        return

    config_path = os.path.join(
        CONFIG_DIR,
        selected
    )

    with open(config_path, "r") as f:
        config = json.load(f)

    # =====================================================
    # SHOW CONFIG LIVE
    # =====================================================
    config_view.content = json.dumps(
        config,
        indent=2
    )

    envs = config.get("envs", [])
    mode = mode_select.value

    docker_env = None
    k3s_env = None

    try:

        add_log("Starting infrastructure...")

        status_label.set_text(
            "Starting infrastructure..."
        )

        docker_vars = (
            load_env("docker")
            if "docker" in envs
            else None
        )

        k3s_vars = (
            load_env("k3s")
            if "k3s" in envs
            else None
        )

        # =================================================
        # START ENVIRONMENTS
        # =================================================
        if docker_vars:

            add_log(
                "Starting Docker environment"
            )

            docker_env = DockerEnvironment(
                docker_vars
            )

            docker_env.start(
                registry=STATE
            )

        if k3s_vars:

            add_log(
                "Starting K3s environment"
            )

            k3s_env = K3sEnvironment(
                k3s_vars
            )

            k3s_env.start(
                registry=STATE
            )

        add_log(
            f"Registry state: {STATE.all()}"
        )

        # =================================================
        # HEALTHCHECKS
        # =================================================
        add_log("Waiting for stacks...")

        status_label.set_text(
            "Waiting for stacks..."
        )

        targets = []

        if docker_vars:

            targets.append((
                "docker",
                docker_vars["GRAFANA_URL"],
                docker_vars["PROM_URL"]
            ))

        if k3s_vars:

            targets.append((
                "k3s",
                k3s_vars["GRAFANA_URL"],
                k3s_vars["PROM_URL"]
            ))

        for name, g, p in targets:

            add_log(
                f"Healthcheck: {name}"
            )

            wait_for_stack(g, p)

            add_log(
                f"{name} ready"
            )

        # =================================================
        # RUN BENCHMARK
        # =================================================
        add_log(
            f"Running benchmark ({mode})"
        )

        status_label.set_text(
            f"Running benchmark ({mode})"
        )

        process = subprocess.run(
            [
                "powershell",
                "-File",
                "run_benchmarks.ps1",
                config_path,
                mode
            ],
            cwd=ROOT
        )

        if process.returncode == 0:

            add_log(
                "Benchmark finished successfully"
            )

            status_label.set_text(
                "Done"
            )

        else:

            add_log(
                f"Benchmark failed ({process.returncode})"
            )

            status_label.set_text(
                "Failed"
            )

    except Exception as e:

        add_log(f"ERROR: {e}")

        status_label.set_text(
            f"Error: {e}"
        )

    finally:

        add_log("Cleaning up...")

        status_label.set_text(
            "Cleaning up..."
        )

        if k3s_env:
            k3s_env.stop()

        if docker_env:
            docker_env.stop()

        add_log("Cleanup finished")

        status_label.set_text("Idle")


# =========================================================
# BUTTON ACTION
# =========================================================
start_button.on_click(run_benchmark)

# =========================================================
ui.run(
    title="Benchmark Orchestrator",
    reload=False
)