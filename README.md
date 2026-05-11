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
python scripts/benchmark.py --env <docker/k3s> --scenario <login/vorlesung/...> --testType <smoke/averageLoad/...> --run <Runnummer>
````