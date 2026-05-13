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
    # =================================================

    if summary.get("latency_p95"):

        # Sehr hohe Latenz
        # -> starke Verschlechterung
        if summary["latency_p95"] > 1200:
            score -= 30

        # Mittlere hohe Latenz
        # -> moderate Verschlechterung
        elif summary["latency_p95"] > 800:
            score -= 15

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
    # =================================================

    if summary.get("error_rate"):

        # Mehr als 5 % Fehler
        # -> sehr kritisch
        if summary["error_rate"] > 0.05:
            score -= 40

        # Mehr als 1 % Fehler
        # -> problematisch
        elif summary["error_rate"] > 0.01:
            score -= 20

    # =================================================
    # CONTAINER CPU USAGE
    # =================================================
    #
    # Prüft die maximale CPU-Auslastung
    # aller Container.
    #
    # Werte nahe 1.0 bedeuten:
    # -> CPU fast vollständig ausgelastet
    #
    # Hohe CPU-Auslastung kann zu:
    # - längeren Antwortzeiten
    # - throttling
    # - Instabilität
    # führen.
    # =================================================

    if summary.get("cpu_max"):

        # CPU-Auslastung über 95 %
        if summary["cpu_max"] > 0.95:
            score -= 10

    # =================================================
    # CONTAINER MEMORY USAGE
    # =================================================
    #
    # Prüft die maximale RAM-Auslastung
    # aller Container.
    #
    # Hohe RAM-Auslastung kann:
    # - OOMKills verursachen
    # - Container abstürzen lassen
    # - Swapping auslösen
    # =================================================

    if summary.get("memory_max"):

        # Mehr als 95 % RAM-Auslastung
        if summary["memory_max"] > 0.95:
            score -= 10

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
    # =================================================

    if summary.get("node_cpu_max"):

        # Node CPU über 95 %
        if summary["node_cpu_max"] > 0.95:
            score -= 10

    # =================================================
    # NODE MEMORY USAGE
    # =================================================
    #
    # Prüft die RAM-Auslastung
    # der Nodes.
    #
    # Hohe Node-Memory-Auslastung kann:
    # - Evictions verursachen
    # - Pods neu starten
    # - Instabilität erzeugen
    # =================================================

    if summary.get("node_memory_max"):

        # Node RAM über 95 %
        if summary["node_memory_max"] > 0.95:
            score -= 10

    # =================================================
    # NODE LOAD
    # =================================================
    #
    # Prüft die Systemlast des Hosts.
    #
    # node_load misst:
    # - wie viele Prozesse auf CPU warten
    #
    # Hoher Load bedeutet:
    # - CPU überlastet
    # - zu viele gleichzeitige Prozesse
    # - Scheduling-Engpässe
    #
    # Ein Wert > 4 gilt hier als kritisch.
    # =================================================

    if summary.get("node_load_max"):

        # Sehr hohe Systemlast
        if summary["node_load_max"] > 4:
            score -= 10

    # =================================================
    # Finalen Score zurückgeben
    # =================================================
    #
    # Der Score darf niemals negativ werden.
    #
    # Beispiel:
    # -20 -> wird zu 0
    # =================================================

    return max(score, 0)

def calculate_soak_score(summary):

    # -------------------------------------------------
    # Startwert für den Soak Reliability Score
    #
    # Auch hier startet das System mit 100 Punkten.
    # Der Fokus ist aber NICHT Peak-Performance,
    # sondern Stabilität über Zeit.
    #
    # Typische Probleme bei Soak Tests:
    # - Memory Leaks
    # - CPU Drift
    # - steigende Latenzen über Zeit
    # - schleichende Instabilität
    # -------------------------------------------------

    score = 100

    # =================================================
    # MEMORY LEAK DETECTION
    # =================================================
    #
    # Beim Soak Test ist Memory-Verhalten über Zeit
    # extrem wichtig.
    #
    # Problem:
    # Wenn Memory kontinuierlich steigt,
    # liegt vermutlich ein Leak vor.
    #
    # Das ist kritischer als ein einzelner Peak.
    # =================================================

    mem = summary.get("memory_growth_percent")

    if mem is not None:

        # Starker Memory Leak
        # -> sehr kritisch
        if mem > 30:
            score -= 40

        # Moderater Memory Anstieg
        # -> potenziell problematisch
        elif mem > 15:
            score -= 20

        # Leichter kontinuierlicher Anstieg
        # -> frühes Leak-Signal
        elif mem > 5:
            score -= 10

    # =================================================
    # CPU DRIFT (langfristige Veränderung)
    # =================================================
    #
    # CPU darf im Soak Test NICHT dauerhaft steigen.
    #
    # Ein steigender CPU Trend bedeutet:
    # - ineffiziente Verarbeitung
    # - Hintergrundprozesse wachsen
    # - mögliche Deadlocks / Loops
    # =================================================

    cpu = summary.get("cpu_growth_percent")

    if cpu is not None:

        # Starker CPU-Anstieg über Zeit
        if cpu > 25:
            score -= 20

        # leichter CPU-Anstieg
        elif cpu > 10:
            score -= 10

        # sehr leichter Drift
        elif cpu > 5:
            score -= 5

    # =================================================
    # LATENCY DRIFT
    # =================================================
    #
    # Im Gegensatz zum Load Test ist hier wichtig:
    # NICHT nur p95,
    # sondern die Veränderung über Zeit.
    #
    # Wenn Latenz steigt:
    # -> System degradiert unter Dauerlast
    # =================================================

    lat = summary.get("latency_growth_percent")

    if lat is not None:

        # starke Verschlechterung der Latenz
        if lat > 30:
            score -= 20

        # moderate Verschlechterung
        elif lat > 15:
            score -= 10

        # leichter Drift
        elif lat > 5:
            score -= 5

    # =================================================
    # SYSTEM-WEITE DEGRADATION
    # =================================================
    #
    # Wenn mehrere Ressourcen gleichzeitig degradieren,
    # ist das ein Zeichen für systemische Probleme
    # und nicht nur einzelne Engpässe.
    # =================================================

    if mem and cpu and lat:

        if mem > 15 and cpu > 10 and lat > 15:
            score -= 15

    # =================================================
    # Finalen Score zurückgeben
    # =================================================
    #
    # Der Score darf niemals negativ werden.
    # =================================================

    return max(score, 0)