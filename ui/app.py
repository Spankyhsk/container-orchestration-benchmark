import sys
import os
import json
import subprocess
import queue
import time
import threading

from nicegui import ui
from dotenv import dotenv_values

# =========================================================
# ROOT
# =========================================================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from infra.environments import DockerEnvironment, K3sEnvironment
from infra.healthchecks import wait_for_stack
from infra.registry import ConnectionState
from infra.prometheus_reset import reset_prometheus

# =========================================================
# CONFIG
# =========================================================
CONFIG_DIR = "configs"
configs = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]

STATE = ConnectionState()

log_queue = queue.Queue()

benchmark_thread = None
benchmark_running = False
cancel_event = threading.Event()

docker_env = None
k3s_env = None


# =========================================================
# HELPERS
# =========================================================
def add_log(msg: str):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    log_queue.put(line)


def load_env(name: str):
    return dotenv_values(f".env.{name}")


# =========================================================
# UI
# =========================================================
ui.dark_mode()

with ui.column().classes("w-full items-center p-4 gap-4"):

    # =====================================================
    # HEADER
    # =====================================================
    with ui.card().classes("w-full max-w-6xl p-6"):
        ui.label("Benchmark Orchestrator").classes("text-3xl font-bold")
        status_label = ui.label("Idle").classes("text-blue-300")


    # =====================================================
    # MAIN
    # =====================================================
    with ui.row().classes("w-full max-w-6xl gap-4"):

        # -------------------------------------------------
        # CONTROL
        # -------------------------------------------------
        with ui.card().classes("w-1/2 p-4"):

            ui.label("Configuration").classes("font-bold")

            config_select = ui.select(configs, label="Config").classes("w-full")

            mode_select = ui.select(
                ["collect", "analyze", "full"],
                value="collect",
                label="Mode"
            ).classes("w-full")

            start_btn = ui.button("Start Benchmark")
            cancel_btn = ui.button("Cancel")

            start_btn.style("background:#2563eb;color:white;font-weight:bold")
            cancel_btn.style("background:#dc2626;color:white;font-weight:bold")


        # -------------------------------------------------
        # CONFIG PREVIEW
        # -------------------------------------------------
        with ui.card().classes("w-1/2 p-4"):

            ui.label("Config Preview").classes("font-bold")

            config_view = ui.code("", language="json").classes("w-full h-[400px]")


    # =====================================================
    # LOGS
    # =====================================================
    with ui.card().classes("w-full max-w-6xl p-4"):

        ui.label("Logs").classes("font-bold")

        log_box = ui.log(max_lines=3000).classes("w-full h-[400px]")


# =========================================================
# LOG LOOP
# =========================================================
def refresh_logs():
    while not log_queue.empty():
        log_box.push(log_queue.get_nowait())

ui.timer(0.3, refresh_logs)


# =========================================================
# CONFIG PREVIEW
# =========================================================
def refresh_config():
    selected = config_select.value
    if not selected:
        return

    try:
        path = os.path.join(CONFIG_DIR, selected)
        with open(path, "r") as f:
            data = json.load(f)

        config_view.content = json.dumps(data, indent=2)
        config_view.update()

    except Exception as e:
        config_view.content = str(e)
        config_view.update()

ui.timer(1.0, refresh_config)


# =========================================================
# WORKER
# =========================================================
def worker():

    global docker_env, k3s_env, benchmark_running

    try:
        cancel_event.clear()

        selected = config_select.value
        if not selected:
            add_log("No config selected")
            return

        config_path = os.path.join(CONFIG_DIR, selected)

        with open(config_path, "r") as f:
            config = json.load(f)

        mode = mode_select.value
        envs = config.get("envs", [])

        add_log(f"Mode: {mode}")

        # =====================================================
        # ANALYZE MODE
        # =====================================================
        if mode == "analyze":

            status_label.set_text("Analyzing results...")

            add_log("Analyze mode -> skipping infrastructure startup")
            add_log("No SSH tunnel required")
            add_log("No port forwarding required")
            add_log("No healthchecks required")

        else:

            status_label.set_text("Starting infrastructure...")

            docker_vars = load_env("docker") if "docker" in envs else None
            k3s_vars = load_env("k3s") if "k3s" in envs else None

            # =====================================================
            # START INFRA
            # =====================================================
            if docker_vars:
                add_log("Starting Docker environment")
                docker_env = DockerEnvironment(docker_vars)
                docker_env.start(registry=STATE)

            if k3s_vars:
                add_log("=== RESET PROMETHEUS (k3s) BEFORE TUNNEL ===")

                reset_prometheus()

                add_log("Prometheus reset complete")

                # kleine Stabilisierung (wichtig!)
                time.sleep(5)

                add_log("Starting K3s environment")
                k3s_env = K3sEnvironment(k3s_vars)
                k3s_env.start(registry=STATE)

            # =====================================================
            # HEALTHCHECKS
            # =====================================================
            status_label.set_text("Waiting for stacks...")

            targets = []

            if docker_vars:
                targets.append((
                    docker_vars["GRAFANA_URL"],
                    docker_vars["PROM_URL"]
                ))

            if k3s_vars:
                targets.append((
                    k3s_vars["GRAFANA_URL"],
                    k3s_vars["PROM_URL"]
                ))

            for g, p in targets:

                if cancel_event.is_set():
                    raise Exception("Cancelled")

                add_log(f"Healthcheck: {g} / {p}")

                wait_for_stack(g, p)

                add_log("Stack ready")

        # =====================================================
        # BENCHMARK / ANALYZE
        # =====================================================
        status_label.set_text(f"Running {mode}...")

        proc = subprocess.Popen(
            [
                "powershell",
                "-File",
                "run_benchmarks.ps1",
                config_path,
                mode
            ],
            cwd=ROOT
        )

        while proc.poll() is None:

            if cancel_event.is_set():

                add_log("Cancel requested -> killing benchmark")

                proc.terminate()
                proc.kill()

                raise Exception("Cancelled")

            time.sleep(0.5)

        add_log(f"{mode} finished")

    except Exception as e:

        add_log(f"ERROR: {e}")

    finally:

        # =====================================================
        # CLEANUP ONLY IF INFRA WAS STARTED
        # =====================================================
        status_label.set_text("Cleaning up...")

        try:

            if k3s_env:
                k3s_env.stop()

            if docker_env:
                docker_env.stop()

        except Exception as e:

            add_log(f"Cleanup error: {e}")

        docker_env = None
        k3s_env = None

        benchmark_running = False

        status_label.set_text("Idle")

        add_log("Cleanup finished")


# =========================================================
# START / CANCEL
# =========================================================
def start():
    global benchmark_running

    if benchmark_running:
        add_log("Already running")
        return

    benchmark_running = True
    threading.Thread(target=worker, daemon=True).start()


def cancel():
    add_log("Cancel triggered")
    cancel_event.set()


start_btn.on_click(start)
cancel_btn.on_click(cancel)

# =========================================================
ui.run(title="Benchmark Orchestrator", reload=False)