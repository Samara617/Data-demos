import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def main():
    base = Path(".")
    raw_path = base / "sn_incidents_raw.csv"
    clean_path = base / "sn_incidents_cleaned.csv"
    summary_pdf_path = base / "sn_summary.pdf"

    df_raw = pd.read_csv(raw_path)

    # Basic cleaning
    before = len(df_raw)
    df = df_raw.drop_duplicates()
    after = len(df)

    if "priority" in df.columns:
        df["priority"] = df["priority"].fillna("3 - Moderate")
    if "assignment_group" in df.columns:
        df["assignment_group"] = df["assignment_group"].fillna("Unassigned Group")
    if "assignee" in df.columns:
        df["assignee"] = df["assignee"].fillna("unassigned")

    df.to_csv(clean_path, index=False)

    # Simple KPI summary
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(summary_pdf_path), pagesize=LETTER)
    story = []

    story.append(Paragraph("ServiceNow Incident Health Report", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Cleaned and analyzed ServiceNow-style incidents, fixed duplicates and missing values.",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 10))

    metrics = [
        ["Metric", "Value"],
        ["Rows (raw)", f"{before:,}"],
        ["Rows (clean)", f"{after:,}"],
    ]
    tbl = Table(metrics, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    doc.build(story)
    print("Done → sn_incidents_cleaned.csv, sn_summary.pdf")

if __name__ == "__main__":
    main()
