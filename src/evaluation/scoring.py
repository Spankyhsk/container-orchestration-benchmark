# =================================================
# SCORE ROUTER
# =================================================
from ftplib import error_reply


def calculate_score_by_type(testClass, testType, result):

    if testClass == "load":

        if testType == "soak":
            return calculate_soak_score(result)

        return calculate_load_score(result)

    if testClass == "chaos":
        return calculate_chaos_reliability_score(result)

    return calculate_load_score(result)

def calculate_load_score(summary):

    # =================================================
    # RELIABILITY-FIRST SCORING MODEL
    #
    # Fokus:
    # 1. Fehler & Instabilität (wichtigste Ebene)
    # 2. System-/Node-Stabilität
    # 3. Container-Stabilität
    # 4. Ressourcenstress
    # 5. Performance (nur indirekt!)
    # =================================================

    score = 100

    # =================================================
    # 1. ERROR RATE (HIGHEST IMPACT)
    # =================================================
    error_rate = summary.get("error_rate")

    if error_rate is not None:

        if error_rate > 0.05:
            score -= 45
        elif error_rate > 0.01:
            score -= 25
        elif error_rate > 0:
            score -= 10

    # =================================================
    # 2. CONTAINER RESTARTS (STABILITY FAILURE)
    # =================================================
    restarts = summary.get("restarts")

    if restarts is not None:

        if restarts >= 5:
            score -= 35
        elif restarts >= 3:
            score -= 20
        elif restarts >= 1:
            score -= 10

    # =================================================
    # 3. NODE MEMORY (CRITICAL INFRASTRUCTURE SIGNAL)
    # =================================================
    node_memory_max = summary.get("node_memory_max")

    if node_memory_max is not None:

        if node_memory_max > 0.95:
            score -= 20
        elif node_memory_max > 0.85:
            score -= 10
        elif node_memory_max > 0.75:
            score -= 5

    # =================================================
    # 4. NODE CPU (INFRA STABILITY)
    # =================================================
    node_cpu_max = summary.get("node_cpu_max")

    if node_cpu_max is not None:

        if node_cpu_max > 0.90:
            score -= 12
        elif node_cpu_max > 0.80:
            score -= 6
        elif node_cpu_max > 0.70:
            score -= 3

    # =================================================
    # 5. NODE LOAD (WEAK SUPPORT SIGNAL)
    # =================================================
    node_load_max = summary.get("node_load_max")

    if node_load_max is not None:

        if node_load_max > 1.20:
            score -= 5
        elif node_load_max > 1.00:
            score -= 3
        elif node_load_max > 0.80:
            score -= 1

    # =================================================
    # 6. CONTAINER CPU (STRESS, NOT FAILURE)
    # =================================================
    cpu_max = summary.get("cpu_max")

    if cpu_max is not None:

        if cpu_max > 0.95:
            score -= 12
        elif cpu_max > 0.85:
            score -= 6
        elif cpu_max > 0.70:
            score -= 3

    # =================================================
    # 7. CONTAINER MEMORY (CRITICAL BUT BELOW NODE)
    # =================================================
    memory_max = summary.get("memory_max")

    if memory_max is not None:

        if memory_max > 0.95:
            score -= 18
        elif memory_max > 0.85:
            score -= 10
        elif memory_max > 0.75:
            score -= 5

    # =================================================
    # 8. LATENCY (REDUCED IMPACT - ONLY USER IMPACT)
    # =================================================
    latency_p95 = summary.get("latency_p95")

    if latency_p95 is not None:

        # nur noch "impact indicator", nicht system failure
        if latency_p95 > 1500:
            score -= 8
        elif latency_p95 > 800:
            score -= 4
        elif latency_p95 > 400:
            score -= 1

    # =================================================
    # 9. THROUGHPUT (MINIMAL SIGNAL)
    # =================================================
    requests_rate = summary.get("requests_rate")

    if requests_rate is not None:

        if requests_rate < 1:
            score -= 2
        elif requests_rate < 3:
            score -= 1

    # =================================================
    # FINAL SCORE
    # =================================================
    return max(score, 0)

def calculate_soak_score(summary):

    score = 100

    # =================================================
    # MEMORY LEAK DETECTION
    # =================================================

    mem = summary.get("memory_growth_percent")

    if mem is not None:

        if mem > 30:
            score -= 40
        elif mem > 15:
            score -= 25
        elif mem > 5:
            score -= 10

    # =================================================
    # CPU DRIFT
    # =================================================

    cpu = summary.get("cpu_growth_percent")

    if cpu is not None:

        if cpu > 25:
            score -= 25
        elif cpu > 10:
            score -= 15
        elif cpu > 5:
            score -= 5

    # =================================================
    # LATENCY DRIFT
    # =================================================

    lat = summary.get("latency_growth_percent")

    if lat is not None:

        if lat > 30:
            score -= 25
        elif lat > 15:
            score -= 15
        elif lat > 5:
            score -= 5

    # =================================================
    # SYSTEM-WEITE DEGRADATION
    # =================================================

    if mem is not None and cpu is not None and lat is not None:

        if mem > 15 and cpu > 10 and lat > 10:
            score -= 20

    # =================================================
    # STABILITY BONUS CHECK (optional aber sinnvoll)
    # =================================================
    # Wenn alles stabil bleibt -> kein Drift

    if mem is not None and mem < 2 and cpu is not None and cpu < 2 and lat is not None and lat < 2:
        score += 5  # kleines Stabilitäts-Reward

    return max(min(score, 100), 0)

def calculate_chaos_reliability_score(summary):

    score = 100

    # =====================================================
    # 1. AVAILABILITY (gesamt Funktionsfähigkeit)
    # =====================================================
    #
    # availability = 1 - error_rate
    #
    # beantwortet: "wie oft hat das System korrekt geantwortet?"
    # =====================================================

    availability = summary.get("availability")

    if availability is not None:

        if availability < 0.90:
            score -= 45

        elif availability < 0.97:
            score -= 20

        elif availability < 0.99:
            score -= 8

    # =====================================================
    # 2. ERROR RATE (FALLBACK + STRESS SIGNAL)
    # =====================================================
    #
    # Wichtig:
    # Error Rate ist nicht nur "Teil von Availability",
    # sondern zeigt auch:
    # - wie instabil das System war
    # - wie stark es unter Last versagt hat
    # =====================================================
    error_rate = summary.get("error_rate")

    if error_rate is not None:

        if error_rate > 0.10:
            score -= 35

        elif error_rate > 0.05:
            score -= 20

        elif error_rate > 0.01:
            score -= 10

    # =====================================================
    # 3. RECOVERY (HARTE BEDINGUNG)
    # =====================================================

    recovered = summary.get("recovered")

    if recovered is False:
        return 0

    if recovered is None:
        score -= 15

    # =====================================================
    # 4. RECOVERY TIME
    # =====================================================

    recovery_time_ms = summary.get("recoveryTimeMs")

    if recovery_time_ms is not None:

        if recovery_time_ms > 30000:
            score -= 40

        elif recovery_time_ms > 15000:
            score -= 25

        elif recovery_time_ms > 7000:
            score -= 10

    # =====================================================
    # FINAL SCORE
    # =====================================================

    return max(score, 0)