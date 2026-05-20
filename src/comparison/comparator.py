import json
import os

from src.comparison.table_builder import (
    build_table,
    build_table_data
)
from src.comparison.plot_builder import generate_comparison_plots
from src.comparison.pdf_builder import build_pdf


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_group(docker_agg_path, k3s_agg_path, output_dir):

    if not docker_agg_path.endswith("aggregate.json") or not k3s_agg_path.endswith("aggregate.json"):
        raise ValueError("Comparator must use aggregate.json files")

    docker = load_json(docker_agg_path)
    k3s = load_json(k3s_agg_path)

    os.makedirs(output_dir, exist_ok=True)

    # =================================================
    # TABLE
    # =================================================
    table_data = build_table_data(docker, k3s)

    table_text = build_table(docker, k3s)

    table_path = os.path.join(output_dir, "comparison_table.txt")
    with open(table_path, "w", encoding="utf-8") as f:
        f.write(table_text)

    # =================================================
    # BASE PATHS EXTRACT (WICHTIG)
    # =================================================
    docker_base = os.path.dirname(docker_agg_path)
    k3s_base = os.path.dirname(k3s_agg_path)

    # =================================================
    # PLOTS
    # =================================================
    plot_files = generate_comparison_plots(
        docker_base_path=docker_base,
        k3s_base_path=k3s_base,
        output_dir=output_dir
    )

    # =================================================
    # PDF
    # =================================================
    pdf_path = build_pdf(
        table=table_data,
        plots=plot_files,
        output_dir=output_dir,
        meta={
            "docker": docker,
            "k3s": k3s
        }
    )

    return pdf_path