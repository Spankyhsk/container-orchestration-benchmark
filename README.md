# container-orchestration-benchmark

## Test Kategorien

1. Verfügbarkeit
    + Uptime(%)
    + HTTP Success
    + Downtime (Sekunden)
2. Recovery
    + Time to Recovery (TTR)
    + Restart Duration
3. Skalierbarkeit
    + Request/sec
    + Verhalten bei steigenden Usern
    + Auto Scaling (k3s)
4. Fehlertoleranz
    + Error Rate während Fehler
    + Service Degradation
5. Performance
    + p95 / p99 Latenz
    + Durchschnittliche Response Time

## Setup

+ k6
+ Grafana
+ Playwright
+ Chaos Mesh/LitmusChaos
+ Pumba/Toxipeoxy

## Benchmark ausführen
````powershell
python -m src.benchmark --env docker --testClass load --scenario login --testType smoke --run 0
````

## Grafana von Kubernetes erreichbar machen
````powershell
sudo kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
````
````powershell
sudo kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
````

## Annotaion manuell löschen
````powershell
Invoke-RestMethod -Uri "http://localhost:3000/api/annotations" -Headers @{Authorization="Bearer YOUR_TOKEN"}
````
Löschen:
````powershell
Invoke-RestMethod -Method Delete -Uri "http://localhost:3000/api/annotations/17" -Headers @{Authorization="Bearer YOUR_TOKEN"}
````

Alle Löschen:
````powershell
(Invoke-RestMethod -Uri "http://localhost:3000/api/annotations" -Headers @{Authorization="Bearer YOUR_TOKEN"}) | ForEach-Object { Invoke-RestMethod -Method Delete -Uri "http://localhost:3000/api/annotations/$($_.id)" -Headers @{Authorization="Bearer YOUR_TOKEN"} }
````