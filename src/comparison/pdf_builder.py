from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

import os


# =================================================
# SAFE GET
# =================================================

def safe_get(meta, key):
    return meta.get(key, "unknown")


# =================================================
# OVERALL WINNER
# =================================================

def calculate_overall_winner(docker, k3s):

    docker_score = docker.get("reliability_score") or 0
    k3s_score = k3s.get("reliability_score") or 0

    if docker_score > k3s_score:
        return "Docker"

    if k3s_score > docker_score:
        return "K3s"

    return "Tie"


# =================================================
# PDF BUILDER
# =================================================

def build_pdf(table, plots, output_dir, meta):

    os.makedirs(output_dir, exist_ok=True)

    pdf_path = f"{output_dir}/final_report.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    docker = meta.get("docker", meta)
    k3s = meta.get("k3s", meta)

    # =================================================
    # TITLE
    # =================================================

    title = "Docker vs K3s Benchmark Comparison"

    elements.append(
        Paragraph(title, styles["Title"])
    )

    elements.append(Spacer(1, 20))

    # =================================================
    # META INFO
    # =================================================

    overall = calculate_overall_winner(docker, k3s)

    meta_text = f"""
    <b>Scenario:</b> {safe_get(docker, "scenario")}<br/>
    <b>Test Type:</b> {safe_get(docker, "testType")}<br/>
    <b>Test Class:</b> {safe_get(docker, "testClass")}<br/>
    <br/>
    <b>Docker Reliability Score:</b> {docker.get("reliability_score", "N/A")}<br/>
    <b>K3s Reliability Score:</b> {k3s.get("reliability_score", "N/A")}<br/>
    <br/>
    <b>OVERALL WINNER:</b> {overall}
    """

    elements.append(
        Paragraph(meta_text, styles["BodyText"])
    )

    elements.append(Spacer(1, 20))

    # =================================================
    # TABLE TITLE
    # =================================================

    elements.append(
        Paragraph("Metric Comparison", styles["Heading2"])
    )

    elements.append(Spacer(1, 10))

    # =================================================
    # TABLE
    # =================================================

    t = Table(
        table,
        repeatRows=1,
        colWidths=[160, 110, 110, 90]
    )

    t.setStyle(TableStyle([

        # HEADER
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E2E2E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        # GRID
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        # ALIGN
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        # FONT
        ("FONTSIZE", (0, 0), (-1, -1), 8),

        # PADDING
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),

        # ROW COLORS
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F7F7"))
    ]))

    elements.append(t)

    elements.append(Spacer(1, 25))

    # =================================================
    # PLOTS
    # =================================================

    if plots:

        elements.append(
            Paragraph("Performance Comparison Plots", styles["Heading2"])
        )

        elements.append(Spacer(1, 10))

        for p in plots:

            if not os.path.exists(p):
                continue

            try:

                title = os.path.basename(p).replace(".png", "")

                elements.append(
                    Paragraph(title, styles["Heading3"])
                )

                elements.append(Spacer(1, 5))

                img = Image(
                    p,
                    width=500,
                    height=250
                )

                elements.append(img)

                elements.append(Spacer(1, 15))

            except Exception as e:
                print("Plot error:", e)

    # =================================================
    # BUILD
    # =================================================

    doc.build(elements)

    return pdf_path