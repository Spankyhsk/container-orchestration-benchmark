METRIC_TYPES = {

    # =================================================
    # CPU
    # =================================================
    "cpu_avg": "cpu",
    "cpu_max": "cpu",
    "cpu_min": "cpu",

    "node_cpu_avg": "cpu",
    "node_cpu_max": "cpu",
    "node_cpu_min": "cpu",

    # =================================================
    # ERRORS
    # =================================================
    "error_rate": "percent",

    # =================================================
    # MEMORY
    # =================================================
    "memory_avg": "bytes",
    "memory_max": "bytes",
    "memory_min": "bytes",

    "node_memory_avg": "bytes",
    "node_memory_max": "bytes",
    "node_memory_min": "bytes",

    # =================================================
    # NETWORK / DISK
    # =================================================
    "network_rx_avg": "rate",
    "network_rx_max": "rate",
    "network_rx_min": "rate",

    "network_tx_avg": "rate",
    "network_tx_max": "rate",
    "network_tx_min": "rate",

    "disk_read_avg": "rate",
    "disk_read_max": "rate",
    "disk_read_min": "rate",

    "disk_write_avg": "rate",
    "disk_write_max": "rate",
    "disk_write_min": "rate",

    # =================================================
    # LOAD
    # =================================================
    "node_load_avg": "raw",
    "node_load_max": "raw",
    "node_load_min": "raw",

    # =================================================
    # LATENCY
    # =================================================
    "latency_avg": "number",
    "latency_p95": "number",
    "latency_p99": "number",

    # =================================================
    # REQUESTS
    # =================================================
    "requests_total": "number",
    "requests_rate": "number",

    # =================================================
    # RESTARTS
    # =================================================
    "restart_count": "number",
}


def format_value(key, value):

    if value is None:
        return "N/A"

    metric_type = METRIC_TYPES.get(key, "number")

    # =================================================
    # CPU / PERCENT
    # =================================================
    if metric_type == "cpu":
        return f"{value * 100:.1f}%"

    if metric_type == "percent":
        return f"{value * 100:.1f}%"

    # =================================================
    # MEMORY
    # =================================================
    if metric_type == "bytes":

        gb = value / (1024 ** 3)
        mb = value / (1024 ** 2)

        if gb >= 1:
            return f"{gb:.2f} GB"

        return f"{mb:.2f} MB"

    # =================================================
    # NETWORK / DISK
    # =================================================
    if metric_type == "rate":

        if value >= 1024 * 1024:
            return f"{value / (1024 * 1024):.2f} MB/s"

        if value >= 1024:
            return f"{value / 1024:.2f} KB/s"

        return f"{value:.2f} B/s"

    # =================================================
    # RAW VALUES
    # =================================================
    if metric_type == "raw":
        return f"{value:.2f}"

    # =================================================
    # DEFAULT
    # =================================================
    return f"{value:.2f}"