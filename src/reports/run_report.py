import sys
from src.reports.summary_report import build_summary_text
from src.reports.discord import send_message

if __name__ == "__main__":
    path = sys.argv[1]
    run_id = sys.argv[2] if len(sys.argv) > 2 else None

    text = build_summary_text(path, run_id)

    send_message(text)