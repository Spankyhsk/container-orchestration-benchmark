import subprocess

from grafana_api import get_test_window
from prometheus_export import export_metrics
from analyze_results import analyze_results
from generate_plots import generate_plots


def run_benchmark(scenario, env, testType, run_id):

    print(f"\n=== Running Benchmark ===")
    print(f"ENV: {env}")
    print(f"SCENARIO: {scenario}")
    print(f"TESTTYPE: {testType}")
    print(f"RUN: {run_id}")

    # ---------------------------------------------------
    # 1. k6 TEST STARTEN
    # ---------------------------------------------------

    subprocess.run([
        "node",
        "test/load/run-test.js",
        scenario,
        env,
        testType,
        str(run_id),
        "1"
    ])

    print("\nTest finished")

    # ---------------------------------------------------
    # 2. ZEITFENSTER AUS ANNOTATIONS HOLEN
    # ---------------------------------------------------

    start, end = get_test_window(
        scenario=scenario,
        env=env,
        testType=testType,
        run_id=run_id
    )

    print(f"\nDetected Window:")
    print(f"START: {start}")
    print(f"END:   {end}")

    # ---------------------------------------------------
    # 3. PROMETHEUS EXPORT
    # ---------------------------------------------------

    export_metrics(
        env=env,
        scenario=scenario,
        testType=testType,
        run_id=run_id,
        start=start,
        end=end
    )

    print("\nBenchmark export finished")

    # ---------------------------------------------------
    # 4. automatische analyze
    # --------------------------------------------------
    print("Generating analysis...")

    analyze_results(
        scenario=scenario,
        env=env,
        testType=testType,
        run_id=run_id
    )

    generate_plots(
        scenario=scenario,
        env=env,
        testType=testType,
        run_id=run_id
    )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--env", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--testType", required=True)
    parser.add_argument("--run", required=True)

    args = parser.parse_args()

    run_benchmark(
        scenario=args.scenario,
        env=args.env,
        testType=args.testType,
        run_id=args.run
    )