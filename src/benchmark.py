import json
import subprocess
import time

from src.exporters.grafana_api import get_test_window
from src.exporters.grafana_api import cleanup_annotations
from src.exporters.prometheus_export import export_metrics
from src.analyze.analyze_results import analyze_results, analyze_update_results
from src.analyze.generate_plots import generate_plots


def run_benchmark(scenario, env, testType, run_id, testClass):

    if testType != "update":
        print("=== CLEANUP OLD ANNOTATIONS ===")

        cleanup_annotations(
            env=env,
            scenario=scenario,
            testType=testType,
            run_id=run_id,
            testClass=testClass
        )

    print(f"\n=== Running Benchmark ===")
    print(f"ENV: {env}")
    print(f"TESTCLASS: {testClass}")
    print(f"SCENARIO: {scenario}")
    print(f"TESTTYPE: {testType}")
    print(f"RUN: {run_id}")

    # ---------------------------------------------------
    # 1. k6 TEST STARTEN
    # ---------------------------------------------------
    subprocess.run(
        [
            "node",
            f"test/{testClass}/run-test.js",
            scenario,
            env,
            testType,
            str(run_id),
            "1"
        ])

    print("\nTest finished")

    if testType != "update":

        # ---------------------------------------------------
        # 2. ZEITFENSTER AUS ANNOTATIONS HOLEN
        # ---------------------------------------------------
        start, end = wait_for_window(scenario, env, testType, run_id, testClass)


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
            testClass=testClass,
            start=start,
            end=end
        )

        print("\nBenchmark export finished")

        # ---------------------------------------------------
        # 4. ANALYZE
        # ---------------------------------------------------
        print("Generating analysis...")

        analyze_results(
            scenario=scenario,
            env=env,
            testType=testType,
            run_id=run_id,
            testClass=testClass,
            startTime=start,
            endTime=end
        )

        if testType != "soak":
            generate_plots(
                scenario=scenario,
                env=env,
                testType=testType,
                run_id=run_id,
                testClass=testClass
            )
        else:
            print("Skipping plots for soak test")
    else:
        analyze_update_results(
            scenario=scenario,
            env=env,
            testType=testType,
            run_id=run_id,
            testClass=testClass
        )



def wait_for_window(scenario, env, testType, run_id, testClass):
    for _ in range(10):
        try:
            start, end = get_test_window(scenario=scenario,
                                         env=env,
                                         testType=testType,
                                         run_id=run_id,
                                         testClass=testClass)
            return start, end
        except:
            time.sleep(1)

    raise Exception("No START/END found")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--env", required=True)
    parser.add_argument("--testClass", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--testType", required=True)
    parser.add_argument("--run", required=True)

    args = parser.parse_args()

    run_benchmark(
        scenario=args.scenario,
        env=args.env,
        testType=args.testType,
        run_id=args.run,
        testClass=args.testClass
    )