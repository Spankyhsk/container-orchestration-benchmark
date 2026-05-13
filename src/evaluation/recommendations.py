def generate_recommendations(summary):

    recommendations = []

    # =================================================
    # LATENCY
    # =================================================

    latency_p95 = summary.get("latency_p95")

    if latency_p95 is not None:

        if latency_p95 > 1000:

            recommendations.append(
                "High p95 latency detected. "
                "Check API bottlenecks or scaling."
            )

    # =================================================
    # ERROR RATE
    # =================================================

    error_rate = summary.get("error_rate")

    if error_rate is not None:

        if error_rate > 0.05:

            recommendations.append(
                "High error rate detected. "
                "Investigate failing requests."
            )

    # =================================================
    # CPU
    # =================================================

    cpu_max = summary.get("cpu_max")

    if cpu_max is not None:

        if cpu_max > 0.95:

            recommendations.append(
                "Container CPU usage is very high."
            )

    # =================================================
    # MEMORY
    # =================================================

    memory_max = summary.get("memory_max")

    if memory_max is not None:

        if memory_max > 0.95:

            recommendations.append(
                "Container memory usage is very high."
            )

    # =================================================
    # NODE LOAD
    # =================================================

    node_load = summary.get("node_load_max")

    if node_load is not None:

        if node_load > 4:

            recommendations.append(
                "Node load is critically high."
            )

    # =================================================
    # NO ISSUES
    # =================================================

    if not recommendations:

        recommendations.append(
            "System behaved stable during the benchmark."
        )

    return recommendations