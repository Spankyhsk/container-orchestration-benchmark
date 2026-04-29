# 📊 Metrics Definition

## 1. Ziel der Metrikdefinition

Zur systematischen Evaluation der untersuchten Systeme (Docker Compose und k3s) werden vorab definierte Qualitätskategorien und zugehörige Metriken festgelegt.
Diese ermöglichen eine objektive, reproduzierbare und vergleichbare Bewertung der Systeme unter verschiedenen Testszenarien.

---

## 2. Qualitätskategorien

Die Bewertung erfolgt anhand der folgenden fünf zentralen Kategorien:

1. Verfügbarkeit (Availability)
2. Performance
3. Skalierbarkeit (Scalability)
4. Fehlertoleranz (Fault Tolerance)
5. Wiederherstellungsfähigkeit (Recovery)

---

## 3. Definition der Metriken

### 3.1 Verfügbarkeit (Availability)

**Definition:**
Die Fähigkeit des Systems, Anfragen erfolgreich zu verarbeiten und erreichbar zu sein.

**Metriken:**

* **Uptime (%)**
  Anteil erfolgreicher Anfragen im Verhältnis zur Gesamtanzahl:

  Uptime = (erfolgreiche Requests / Gesamtanzahl Requests) * 100

* **Downtime (Sekunden)**
  Zeitspanne, in der das System nicht erreichbar ist (HTTP ≠ 200)

* **Success Rate (%)**
  Anteil erfolgreicher HTTP-Antworten (Status 2xx)

**Messmethoden:**

* Uptime-Check Script (1s Intervall)
* k6 (HTTP Status Codes)

---

### 3.2 Performance

**Definition:**
Die Geschwindigkeit und Effizienz der Anfrageverarbeitung unter Last.

**Metriken:**

* **Average Response Time (ms)**
  Durchschnittliche Antwortzeit aller Requests

* **p95 Response Time (ms)**
  95% aller Requests sind schneller als dieser Wert

* **p99 Response Time (ms)**
  99% aller Requests sind schneller als dieser Wert

* **Throughput (Requests/sec)**
  Anzahl verarbeiteter Anfragen pro Sekunde

**Messmethoden:**

* k6 (Load Testing Tool)
* Prometheus (optional)

---

### 3.3 Skalierbarkeit (Scalability)

**Definition:**
Die Fähigkeit des Systems, mit steigender Last umzugehen.

**Metriken:**

* **Response Time unter Last (ms)**
  Veränderung der Latenz bei steigenden Nutzerzahlen

* **Maximaler Durchsatz (RPS)**
  Maximale Anzahl Requests/sec ohne signifikanten Fehleranstieg

* **Fehlerrate unter Last (%)**
  Anteil fehlgeschlagener Requests bei hoher Last

* **Scaling Time (nur k3s)**
  Zeit bis neue Instanzen bereitgestellt sind

**Messmethoden:**

* k6 (Laststeigerung)
* Prometheus (Ressourcenverbrauch)

---

### 3.4 Fehlertoleranz (Fault Tolerance)

**Definition:**
Die Fähigkeit des Systems, bei Fehlern stabil weiterzuarbeiten.

**Metriken:**

* **Error Rate während Fehler (%)**
  Anteil fehlgeschlagener Requests während eines Crashs

* **Service Degradation**
  Veränderung der Performance während Fehlerzuständen

* **Teilweise Verfügbarkeit (%)**
  Anteil funktionierender Requests während Ausfällen

**Messmethoden:**

* k6 (parallel zu Chaos Tests)
* Uptime-Check Script

---

### 3.5 Wiederherstellungsfähigkeit (Recovery)

**Definition:**
Die Zeit und Fähigkeit des Systems, nach einem Fehler wieder stabil zu arbeiten.

**Metriken:**

* **Time to Recovery (TTR) (Sekunden)**
  Zeit zwischen Ausfall und vollständiger Wiederherstellung

* **Restart Duration (Sekunden)**
  Dauer eines Container-/Pod-Neustarts

* **Stabilisierungspunkt (Sekunden)**
  Zeitpunkt, an dem das System wieder stabile Antwortzeiten liefert

**Messmethoden:**

* Uptime-Check Script (Zeitmessung)
* Logs (Container / Pods)
* Prometheus (Stabilitätsverlauf)

---

## 4. Mapping: Kategorien zu Tools

| Kategorie      | Metrik                  | Tool                |
| -------------- | ----------------------- | ------------------- |
| Verfügbarkeit  | Downtime, Uptime        | Uptime Script, k6   |
| Performance    | p95, p99, Response Time | k6                  |
| Skalierbarkeit | RPS, Latenz unter Last  | k6, Prometheus      |
| Fehlertoleranz | Error Rate              | k6                  |
| Recovery       | Time to Recovery        | Uptime Script, Logs |

---

## 5. Messstrategie

Die Messung erfolgt durch eine Kombination aus:

* aktiven Messungen (k6, Uptime-Checks)
* passiven Monitoring-Daten (Prometheus)
* visueller Analyse (Grafana)

Alle Tests werden unter identischen Bedingungen für beide Systeme durchgeführt, um Vergleichbarkeit sicherzustellen.

---

## 6. Reproduzierbarkeit

Zur Sicherstellung reproduzierbarer Ergebnisse gelten folgende Regeln:

* identische Testdaten (Testuser, Szenarien)
* gleiche Testdauer und Lastprofile
* getrennte Setup- und Messphase
* automatisierte Testausführung

---

## 7. Zusammenfassung

Die definierten Metriken bilden die Grundlage für alle durchgeführten Experimente und ermöglichen eine objektive Bewertung der Systeme hinsichtlich ihrer Zuverlässigkeit, Leistungsfähigkeit und Skalierbarkeit.

---
