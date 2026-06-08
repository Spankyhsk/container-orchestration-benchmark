import json
import os


from src.evaluation.aggregator import run_aggregation
from src.comparison.comparator import compare_group
from src.analyze.re_scoring import rescore_existing_result

# =================================================
# RESCORING PHASE (RUN-AWARE)
# =================================================
def run_rescoring(config):
    """
    Re-Scoring über alle Runs hinweg.

    Wichtig:
    - nutzt config["runsPerTest"]
    - erwartet summary_0_final.json ... summary_N_final.json
    - sorgt für konsistentes Chaos/Load re-evaluation
    """

    testClass = config["testClass"]
    runs_per_test = config.get("runsPerTest", 1)

    print("=== RESCORING PHASE ===")

    for env in config["envs"]:
        for scenario in config["scenarios"]:
            for testType in config["testTypes"]:

                base = f"results/{env}/{testClass}/{scenario}/{testType}"

                if not os.path.exists(base):
                    continue

                for run_id in range(runs_per_test):

                    # mögliche Dateinamen pro run
                    possible_files = [
                        f"summary_{run_id}_final.json",
                        f"summary_{run_id}_summary.json",
                        f"reanalysis_{run_id}.json"
                    ]

                    for file in possible_files:

                        path = os.path.join(base, file)

                        if not os.path.exists(path):
                            continue

                        try:
                            rescore_existing_result(
                                summary_path=path,
                                testClass=testClass,
                                testType=testType
                            )

                            print(f"[RESCORE OK] {path}")

                        except Exception as e:
                            print(f"[RESCORE ERROR] {path} -> {e}")


# =================================================
# AGGREGATION PHASE
# =================================================
def run_aggregation_phase(config):
    """
    Aggregation pro env/scenario/testType
    """

    testClass = config["testClass"]

    print("=== AGGREGATION PHASE ===")

    for env in config["envs"]:
        for scenario in config["scenarios"]:
            for testType in config["testTypes"]:

                try:
                    run_aggregation(
                        env,
                        testClass,
                        scenario,
                        testType
                    )
                except Exception as e:
                    print(f"[AGGREGATION ERROR] {env}/{scenario}/{testType} -> {e}")


# =================================================
# COMPARISON PHASE
# =================================================
def run_comparison_phase(config):
    """
    Docker vs K3s Vergleich
    """

    testClass = config["testClass"]

    print("=== COMPARISON PHASE ===")

    for scenario in config["scenarios"]:
        for testType in config["testTypes"]:

            docker_path = f"results/docker/{testClass}/{scenario}/{testType}/aggregate.json"
            k3s_path = f"results/k3s/{testClass}/{scenario}/{testType}/aggregate.json"
            output_dir = f"results/final_comparison/{scenario}/{testType}"

            try:
                compare_group(
                    docker_path,
                    k3s_path,
                    output_dir
                )
            except Exception as e:
                print(f"[COMPARE ERROR] {scenario}/{testType} -> {e}")


# =================================================
# FULL PIPELINE
# =================================================
def run_full_analysis(config):

    print("\n==============================")
    print(" START ANALYSIS PIPELINE")
    print("==============================\n")

    run_rescoring(config)
    run_aggregation_phase(config)
    run_comparison_phase(config)

    print("\n==============================")
    print(" ANALYSIS DONE")
    print("==============================\n")


# =================================================
# CLI ENTRY
# =================================================
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)

    args = parser.parse_args()

    if not os.path.exists(args.config):
        raise FileNotFoundError(f"Config not found: {args.config}")

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    run_full_analysis(config)