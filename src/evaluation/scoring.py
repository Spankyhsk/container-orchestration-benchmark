# =================================================
# SCORE ROUTER
# =================================================
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
    """
    CHAOS RELIABILITY SCORE (0–100)

    Fokus NICHT auf Performance,
    sondern auf System-Resilienz:

    1. Availability (funktioniert das System überhaupt?)
    2. Fault Tolerance (wie stark bricht es unter Fehlern?)
    3. Recovery (wie schnell erholt es sich?)
    4. Stability after recovery (bleibt es stabil?)

    Ziel:
    Ein System ist "gut", wenn es
    - Fehler überlebt
    - sich schnell erholt
    - danach stabil bleibt
    """

    score = 100

    # =====================================================
    # 1. AVAILABILITY (WICHTIGSTER BASISFAKTOR)
    # =====================================================
    #
    # Warum:
    # Chaos ist irrelevant, wenn System nicht erreichbar ist.
    # Verfügbarkeit ist die Grundvoraussetzung für Reliability.
    #
    # Beispiel:
    # - API down → massiver Abzug
    # - teilweise Fehler → moderater Abzug
    # =====================================================

    availability = summary.get("availability_rate")  # 0..1

    if availability is not None:

        if availability < 0.90:
            score -= 50  # System größtenteils unbrauchbar

        elif availability < 0.98:
            score -= 25

        elif availability < 0.995:
            score -= 10

    # =====================================================
    # 2. RECOVERY TIME (KERN DER CHAOS ENGINEERING)
    # =====================================================
    #
    # Warum:
    # Ein resilientes System heilt sich schnell selbst.
    #
    # Interpretation:
    # - < 5s    → exzellent
    # - < 15s   → gut
    # - < 30s   → akzeptabel
    # - > 30s   → kritisch
    #
    # Gewichtung: sehr hoch
    # =====================================================

    recovery_time_ms = summary.get("recoveryTimeMs")

    if recovery_time_ms is not None:

        if recovery_time_ms > 30000:
            score -= 40

        elif recovery_time_ms > 15000:
            score -= 25

        elif recovery_time_ms > 5000:
            score -= 10

    # =====================================================
    # 3. FAULT TOLERANCE (FEHLERVERHALTEN)
    # =====================================================
    #
    # Warum:
    # Ein gutes System:
    # - crasht nicht sofort
    # - degradiert kontrolliert
    #
    # schlechte Systeme:
    # - komplette Ausfälle bei Teilfehlern
    #
    # =====================================================

    error_rate = summary.get("error_rate")

    if error_rate is not None:

        if error_rate > 0.10:
            score -= 35  # System bricht stark unter Fehlerlast

        elif error_rate > 0.05:
            score -= 20

        elif error_rate > 0.01:
            score -= 10

    # =====================================================
    # 4. STABILITY AFTER RECOVERY
    # =====================================================
    #
    # Warum:
    # Klassischer Chaos Failure:
    # → System "kommt zurück"
    # → bleibt aber instabil
    #
    # Gute Systeme stabilisieren sich vollständig.
    # =====================================================

    post_error_rate = summary.get("post_recovery_error_rate")

    if post_error_rate is not None:

        if post_error_rate > 0.02:
            score -= 15

        elif post_error_rate > 0.005:
            score -= 8

    post_latency = summary.get("post_recovery_latency_p95")

    if post_latency is not None:

        if post_latency > 1000:
            score -= 10

        elif post_latency > 500:
            score -= 5

    # =====================================================
    # 5. PARTIAL DEGRADATION vs HARD FAILURE
    # =====================================================
    #
    # Warum:
    # Sehr wichtig für Chaos Engineering:
    #
    # - Soft failure (teilweise Fehler) → ok
    # - Hard failure (kompletter Ausfall) → schlecht
    #
    # Wenn du später erweiterst:
    # Hier kannst du "graceful degradation" messen.
    # =====================================================

    hard_failure = summary.get("hard_failure")  # boolean

    if hard_failure is True:
        score -= 25

    # =====================================================
    # FINAL SCORE
    # =====================================================

    return max(score, 0)