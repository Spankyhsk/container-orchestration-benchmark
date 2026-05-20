import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.reports.format_summary import format_value


GERMANY_TZ = ZoneInfo("Europe/Berlin")


def format_time_de(timestamp):

    if timestamp is None:
        return "N/A"

    try:
        dt = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        dt_de = dt.astimezone(GERMANY_TZ)

        return dt_de.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return str(timestamp)


def build_summary_text(path, run_id=None):

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []

    # =================================================
    # HEADER
    # =================================================
    header = "RUN SUMMARY"

    if run_id is not None:
        header += f" (Run {run_id})"

    lines.append(header)

    lines.append(
        f"({data.get('environment')} | {data.get('scenario')} | {data.get('testType')})"
    )

    lines.append("")

    # =================================================
    # TEST WINDOW
    # =================================================
    start = data.get("startTime")
    end = data.get("endTime")

    duration = None

    if start is not None and end is not None:
        try:
            duration = float(end) - float(start)
        except Exception:
            duration = None

    lines.append("⏱ Test Window")

    lines.append(f"Start (DE): {format_time_de(start)}")
    lines.append(f"End (DE):   {format_time_de(end)}")

    if duration is not None:
        lines.append(f"Duration:   {int(duration)}s")

    lines.append("")

    # =================================================
    # LATENCY
    # =================================================
    lines.append("⚡ Latency")

    lines.append(
        f"p95: {format_value('latency_p95', data.get('latency_p95'))} ms"
    )

    lines.append(
        f"avg: {format_value('latency_avg', data.get('latency_avg'))} ms"
    )

    lines.append("")



    # =================================================
    # THROUGHPUT
    # =================================================
    lines.append("🚀 Throughput")

    lines.append(
        f"Requests/sec: {format_value('requests_rate', data.get('requests_rate'))}"
    )

    lines.append(
        f"Total Requests: {format_value('requests_total', data.get('requests_total'))}"
    )

    lines.append("")

    # =================================================
    # ERRORS
    # =================================================
    lines.append("❌ Errors")

    lines.append(
        f"rate: {format_value('error_rate', data.get('error_rate'))}"
    )

    lines.append("")

    # =================================================
    # CPU
    # =================================================
    lines.append("🧠 CPU")

    lines.append(
        f"avg: {format_value('cpu_avg', data.get('cpu_avg'))}"
    )

    lines.append(
        f"max: {format_value('cpu_max', data.get('cpu_max'))}"
    )

    lines.append("")

    # =================================================
    # MEMORY
    # =================================================
    lines.append("💾 Memory")

    lines.append(
        f"avg: {format_value('memory_avg', data.get('memory_avg'))}"
    )

    lines.append(
        f"max: {format_value('memory_max', data.get('memory_max'))}"
    )

    lines.append("")

    # =================================================
    # NETWORK
    # =================================================
    lines.append("🌐 Network")

    lines.append(
        f"RX avg: {format_value('network_rx_avg', data.get('network_rx_avg'))}"
    )

    lines.append(
        f"TX avg: {format_value('network_tx_avg', data.get('network_tx_avg'))}"
    )

    lines.append("")

    # =================================================
    # DISK
    # =================================================
    lines.append("💽 Disk")

    lines.append(
        f"read avg:  {format_value('disk_read_avg', data.get('disk_read_avg'))}"
    )

    lines.append(
        f"write avg: {format_value('disk_write_avg', data.get('disk_write_avg'))}"
    )

    lines.append("")

    # =================================================
    # NODE
    # =================================================
    lines.append("📡 Node")

    lines.append(
        f"CPU max:  {format_value('node_cpu_max', data.get('node_cpu_max'))}"
    )

    lines.append(
        f"Load max: {format_value('node_load_max', data.get('node_load_max'))}"
    )

    lines.append("")

    # =================================================
    # RESTARTS
    # =================================================
    restart_count = data.get("restarts")

    lines.append("🔄 Container Restarts")

    if restart_count is not None:
        lines.append(f"Restarts: {restart_count}")
    else:
        lines.append("Restarts: N/A")

    lines.append("")

    # =================================================
    # RECOMMENDATIONS
    # =================================================
    recommendations = data.get("recommendations", [])

    if recommendations:

        lines.append("💡 Recommendations")

        for recommendation in recommendations:
            lines.append(f"- {recommendation}")

        lines.append("")

    # =================================================
    # RELIABILITY SCORE
    # =================================================
    score = data.get("reliability_score")

    lines.append("🏆 Reliability Score")

    if score is not None:
        lines.append(f"{score}/100")
    else:
        lines.append("N/A")

    return "\n".join(lines)