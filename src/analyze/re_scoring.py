import json
import os

from src.evaluation.scoring import calculate_score_by_type
from src.evaluation.recommendations import generate_recommendations


# =================================================
# RE-SCORE EXISTING RESULT FILE
# =================================================
def rescore_existing_result(
        summary_path,
        testClass,
        testType
):
    """
    Lädt ein bereits fertiges Analyse-JSON,
    berechnet Score + Recommendations neu
    und überschreibt die Datei.

    Zweck:
    - Scoring kann iterativ angepasst werden
    - keine erneuten Tests nötig
    - perfekt für Chaos/Load Score Tuning
    """

    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Missing file: {summary_path}")

    # -------------------------------------------------
    # LOAD EXISTING RESULT
    # -------------------------------------------------
    with open(summary_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    # -------------------------------------------------
    # SCORE RECOMPUTE
    # -------------------------------------------------
    result["reliability_score"] = calculate_score_by_type(
        testClass,
        testType,
        result
    )

    # -------------------------------------------------
    # RECOMMENDATIONS RECOMPUTE
    # -------------------------------------------------
    result["recommendations"] = generate_recommendations(result)

    # -------------------------------------------------
    # SAVE (overwrite same file)
    # -------------------------------------------------
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[RESCORE] updated: {summary_path}")

    return result