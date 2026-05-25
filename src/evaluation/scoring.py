def calculate_load_score(summary):

    # -------------------------------------------------
    # Startwert für den Reliability Score
    #
    # Das System startet immer mit 100 Punkten.
    # Schlechte Performance oder Instabilität
    # ziehen Punkte ab.
    # -------------------------------------------------

    score = 100

    # =================================================
    # LATENCY (Antwortzeiten)
    # =================================================
    #
    # Es wird die p95-Latenz geprüft.
    #
    # p95 bedeutet:
    # 95 % aller Requests waren schneller
    # als dieser Wert.
    #
    # Hohe Latenzen bedeuten:
    # - langsame APIs
    # - Überlastung
    # - schlechte Skalierung
    #
    # Latenz ist eines der wichtigsten
    # Performance-Signale.
    # =================================================

    latency_p95 = summary.get("latency_p95")

    if latency_p95 is not None:

        if latency_p95 > 1200:
            score -= 30

        elif latency_p95 > 800:
            score -= 15

        elif latency_p95 > 400:
            score -= 5

    # =================================================
    # ERROR RATE (Fehlerrate)
    # =================================================
    #
    # Prüft den Anteil fehlgeschlagener Requests.
    #
    # Beispiel:
    # 0.05 = 5 % Fehler
    #
    # Viele Fehler bedeuten:
    # - Instabilität
    # - Timeouts
    # - Crashes
    # - Überlastung
    #
    # Fehler sind der wichtigste
    # Reliability-Indikator.
    # =================================================

    error_rate = summary.get("error_rate")

    if error_rate is not None:

        if error_rate > 0.05:
            score -= 40

        elif error_rate > 0.01:
            score -= 20

        elif error_rate > 0:
            score -= 5

    # =================================================
    # CONTAINER CPU USAGE
    # =================================================
    #
    # Prüft die maximale CPU-Auslastung
    # aller Container relativ zur
    # verfügbaren Cluster-/Host-Kapazität.
    #
    # Werte:
    # 1.0 = 100 % CPU-Auslastung
    #
    # Hohe CPU-Auslastung kann zu:
    # - längeren Antwortzeiten
    # - throttling
    # - Instabilität
    # führen.
    #
    # CPU ist wichtig, aber weniger kritisch
    # als Fehler oder Speicherprobleme.
    # =================================================

    cpu_max = summary.get("cpu_max")

    if cpu_max is not None:

        if cpu_max > 0.95:
            score -= 15

        elif cpu_max > 0.85:
            score -= 10

        elif cpu_max > 0.70:
            score -= 5

    # =================================================
    # CONTAINER MEMORY USAGE
    # =================================================
    #
    # Prüft die maximale RAM-Auslastung
    # aller Container relativ zur
    # verfügbaren Cluster-/Host-Kapazität.
    #
    # Hohe RAM-Auslastung kann:
    # - OOMKills verursachen
    # - Container abstürzen lassen
    # - Swapping auslösen
    #
    # Memory-Probleme sind oft kritischer
    # als CPU-Probleme.
    # =================================================

    memory_max = summary.get("memory_max")

    if memory_max is not None:

        if memory_max > 0.95:
            score -= 20

        elif memory_max > 0.85:
            score -= 10

        elif memory_max > 0.75:
            score -= 5

    # =================================================
    # NODE CPU USAGE
    # =================================================
    #
    # Prüft die CPU-Auslastung
    # der Kubernetes- oder Docker-Nodes.
    #
    # Hohe Node-CPU bedeutet:
    # - gesamter Host ist ausgelastet
    # - Scheduling-Probleme möglich
    # - alle Container betroffen
    #
    # Node CPU erkennt Infrastruktur-
    # Überlastung.
    # =================================================

    node_cpu_max = summary.get("node_cpu_max")

    if node_cpu_max is not None:

        if node_cpu_max > 0.90:
            score -= 10

        elif node_cpu_max > 0.80:
            score -= 5

        elif node_cpu_max > 0.70:
            score -= 2

    # =================================================
    # NODE MEMORY USAGE
    # =================================================
    #
    # Prüft den RAM-Verbrauch der Nodes.
    #
    # Hohe Auslastung kann:
    # - Pod Evictions verursachen
    # - Instabilität im Cluster erzeugen
    # - OOMKills triggern
    #
    # Node Memory ist besonders kritisch,
    # da der gesamte Cluster betroffen sein kann.
    # =================================================

    node_memory_max = summary.get("node_memory_max")

    if node_memory_max is not None:

        if node_memory_max > 0.95:
            score -= 15

        elif node_memory_max > 0.85:
            score -= 8

        elif node_memory_max > 0.75:
            score -= 3

    # =================================================
    # NODE LOAD
    # =================================================
    #
    # System Load zeigt:
    # wie viele Prozesse auf CPU warten.
    #
    # Der Wert ist bereits pro CPU-Core
    # normalisiert und daher zwischen
    # Docker und Kubernetes vergleichbar.
    #
    # Hoher Load bedeutet:
    # - CPU Überlastung
    # - Scheduling Engpässe
    # - Wartende Prozesse
    #
    # Node Load ist ein unterstützendes
    # Infrastruktur-Signal und wird daher
    # schwächer gewichtet.
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
    # CONTAINER RESTARTS
    # =================================================
    #
    # Prüft wie oft Container oder Pods
    # neu gestartet wurden.
    #
    # Gründe für Restarts:
    # - CrashLoopBackOff
    # - OOMKilled
    # - Node instability
    # - Deployment issues
    #
    # Viele Restarts bedeuten:
    # - Instabile Anwendung
    # - Cluster Probleme
    #
    # Restarts sind ein starker
    # Reliability-Indikator.
    # =================================================

    restarts = summary.get("restarts")

    if restarts is not None:

        if restarts >= 5:
            score -= 30

        elif restarts >= 3:
            score -= 20

        elif restarts >= 1:
            score -= 10

    # =================================================
    # THROUGHPUT (leichtes Signal)
    # =================================================
    #
    # Prüft Requests pro Sekunde.
    #
    # Niedriger Throughput bedeutet nicht
    # automatisch schlechte Reliability,
    # da kleine Tests bewusst wenig Last
    # erzeugen können.
    #
    # Daher wird Throughput nur sehr
    # schwach gewichtet.
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
    #
    # Score wird nie negativ.
    # Minimum ist 0.
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