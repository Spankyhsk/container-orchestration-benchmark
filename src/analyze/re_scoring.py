import json
import os

# =================================================
# RE-SCORE EXISTING RESULT FILE
# =================================================
def rescore_existing_result(summary_path, testClass, testType):

    if not os.path.exists(summary_path):
        raise FileNotFoundError(summary_path)

    # =================================================
    # LOAD META FROM FILE
    # =================================================
    with open(summary_path, "r", encoding="utf-8") as f:
        old = json.load(f)

    scenario = old.get("scenario")
    env = old.get("environment")
    run_id = old.get("run")
    startTime = old.get("startTime")
    endTime = old.get("endTime")

    # =================================================
    # RE-RUN FULL ANALYSIS PIPELINE
    # =================================================

    if testClass == "update":

        result = analyze_update_results(
            scenario=scenario,
            env=env,
            testType=testType,
            run_id=run_id,
            testClass=testClass
        )

    else:

        result = analyze_results(
            scenario=scenario,
            env=env,
            testType=testType,
            run_id=run_id,
            testClass=testClass,
            startTime=startTime,
            endTime=endTime
        )

    # =================================================
    # OVERWRITE FILE
    # =================================================
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[RESCORE] re-analyzed: {summary_path}")

    return result