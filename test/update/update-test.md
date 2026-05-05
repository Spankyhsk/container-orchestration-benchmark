# 🧪 Test Documentation: Update Test - K6Api update

---

## 🧾 1. Allgemeine Informationen

**Test Name:**
Update Test - K6Api update

**Kategorie:**
 Availability

**Ziel des Tests:**
Messung der Downtime, Recovery Time, Fehler während Update und Verhalten unter Update
Wichtig dabei die Zeit bis Service wieder erreichbar ist/ausfällt

**System unter Test:**
beides

**Datum:**
{{DATE}}

---

## 🎓 2. Szenario

**Beschreibung:**
Ein Bug wurde aus der K6Api gepatched und deployed

**Nutzerverhalten / Ablauf:**

* {{STEP_1}}
* {{STEP_2}}
* {{STEP_3}}
* {{...}}


---

## ⚙️ 3. Testkonfiguration

**Verwendete Tools:**

* Uptime-Check-Script
* Prometheus
* Grafana

**Lastparameter (falls zutreffend):**

* Virtuelle Nutzer: {{VUS}}
* Dauer: {{DURATION}}
* Ramp-Up: {{RAMP_UP}}

**Umgebung:**

* Docker: {{DOCKER_URL}}
* k3s: {{K3S_URL}}

**Testdaten:**

* {{TEST_USERS}} *(z. B. 100 User: student1–student100)*

---

## 💥 4. Störereignisse / Eingriffe

*(Falls zutreffend, sonst „keine“ eintragen)*

* {{EVENT_1}} *(z. B. Container Crash bei Minute 3)*
* {{EVENT_2}}
* {{EVENT_3}}

---

## 📊 5. Messmethoden

**Erfasste Metriken:**

* {{METRIC_1}} *(z. B. Response Time p95)*
* {{METRIC_2}} *(z. B. Error Rate)*
* {{METRIC_3}} *(z. B. Downtime)*
* {{METRIC_4}}

**Messwerkzeuge:**

* {{MEASUREMENT_TOOL_1}} *(z. B. k6)*
* {{MEASUREMENT_TOOL_2}} *(z. B. Prometheus)*
* {{MEASUREMENT_TOOL_3}} *(z. B. Grafana)*
* {{MEASUREMENT_TOOL_4}} *(z. B. Uptime Script)*

---

## 📈 6. Erwartetes Verhalten

{{EXPECTED_BEHAVIOR}}

---

## 🧪 7. Testdurchführung

1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}
4. {{STEP_4}}
5. {{STEP_5}}

---

## 📉 8. Ergebnisse

### Docker Compose

* {{RESULT_METRIC_1}}
* {{RESULT_METRIC_2}}
* {{RESULT_METRIC_3}}

### k3s

* {{RESULT_METRIC_1}}
* {{RESULT_METRIC_2}}
* {{RESULT_METRIC_3}}

---

## 📊 9. Analyse

{{ANALYSIS}}

---

## 🧠 10. Fazit

{{CONCLUSION}}

---

## 📎 11. Anhänge (optional)

* Logs: {{LOG_PATH}}
* Grafana Dashboard: {{LINK}}
* Rohdaten: {{RESULT_PATH}}

---
