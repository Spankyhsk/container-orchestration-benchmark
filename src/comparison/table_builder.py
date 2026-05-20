from src.reports.format_summary import format_value


def winner(a, b, reverse=False):

    if a is None and b is None:
        return "N/A"

    if a is None:
        return "K3s"

    if b is None:
        return "Docker"

    if a == b:
        return "Equal"

    if reverse:
        return "Docker" if a > b else "K3s"

    return "Docker" if a < b else "K3s"


# =================================================
# STRUCTURED TABLE (FOR PDF)
# =================================================
def build_table_data(a, b):

    def row(name, key, reverse=False):

        av = a.get(key)
        bv = b.get(key)

        w = winner(av, bv, reverse)

        return [
            name,
            format_value(key, av),
            format_value(key, bv),
            w
        ]

    table = []

    # HEADER
    table.append(["Metric", "Docker", "K3s", "Winner"])

    # K6
    table.append(row("Latency P95", "latency_p95"))
    table.append(row("Latency Avg", "latency_avg"))
    table.append(row("Error Rate", "error_rate"))

    table.append(row("Requests/sec", "requests_rate", True))
    table.append(row("Total Requests", "requests_total", True))

    # CPU / MEMORY
    table.append(row("CPU Avg", "cpu_avg"))
    table.append(row("CPU Max", "cpu_max"))
    table.append(row("Memory Avg", "memory_avg"))
    table.append(row("Memory Max", "memory_max"))

    # NETWORK
    table.append(row("Network RX Avg", "network_rx_avg"))
    table.append(row("Network TX Avg", "network_tx_avg"))

    # DISK
    table.append(row("Disk Read Avg", "disk_read_avg"))
    table.append(row("Disk Write Avg", "disk_write_avg"))

    # NODE
    table.append(row("Node CPU Max", "node_cpu_max"))
    table.append(row("Node Memory Max", "node_memory_max"))
    table.append(row("Node Load Max", "node_load_max"))

    # SCORE
    table.append(row("Reliability Score", "reliability_score", True))

    return table


# =================================================
# STRING VERSION (DISCORD / LOGS)
# =================================================
def build_table(a, b):

    data = build_table_data(a, b)

    lines = ["=== BENCHMARK COMPARISON ===\n"]

    for r in data[1:]:
        lines.append(f"{r[0]:<22} | Docker: {r[1]} | K3s: {r[2]} | Winner: {r[3]}")

    # overall
    score_a = a.get("reliability_score") or 0
    score_b = b.get("reliability_score") or 0

    overall = "Docker" if score_a > score_b else "K3s"

    lines.append("\n====================")
    lines.append(f"OVERALL WINNER: {overall}")

    return "\n".join(lines)