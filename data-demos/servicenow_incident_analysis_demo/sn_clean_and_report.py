import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def build_sn_report(
    input_csv: str = "sn_incidents_raw.csv",
    cleaned_csv: str = "sn_incidents_cleaned.csv",
    output_pdf: str = "sn_summary.pdf",
    output_png: str = "sn_summary_chart.png",
):
    base = Path(".")
    raw_path = base / input_csv
    clean_path = base / cleaned_csv
    pdf_path = base / output_pdf
    png_path = base / output_png

    # ---------- 1) Load & basic cleaning ----------
    df_raw = pd.read_csv(raw_path)

    before = len(df_raw)
    df = df_raw.drop_duplicates()
    after = len(df)
    removed_dupes = before - after

    # Normalize columns if they exist
    if "priority" in df.columns:
        df["priority"] = df["priority"].fillna("3 - Moderate")

    if "assignment_group" in df.columns:
        df["assignment_group"] = df["assignment_group"].fillna("Unassigned Group")

    if "assignee" in df.columns:
        df["assignee"] = df["assignee"].fillna("unassigned")

    # Parse dates if present
    if "opened_at" in df.columns:
        df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    if "closed_at" in df.columns:
        df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")

    # Ensure ttc_hours numeric if present
    if "ttc_hours" in df.columns:
        df["ttc_hours"] = pd.to_numeric(df["ttc_hours"], errors="coerce")

    # Persist cleaned CSV
    df.to_csv(clean_path, index=False)

    # ---------- 2) KPI calculations ----------
    total_raw = before
    total_clean = after

    # Resolved vs open
    if "closed_at" in df.columns:
        closed_mask = df["closed_at"].notna()
        closed_count = int(closed_mask.sum())
        open_count = int((~closed_mask).sum())
        resolved_rate = closed_count / total_clean * 100 if total_clean else 0
    else:
        closed_count = open_count = 0
        resolved_rate = 0

    # SLA breach metrics
    if "sla_breach" in df.columns:
        overall_breach_rate = df["sla_breach"].mean() * 100
    else:
        overall_breach_rate = 0

    # MTTR (only closed tickets with ttc_hours)
    if "ttc_hours" in df.columns and "closed_at" in df.columns:
        closed_for_mttr = df[closed_mask & df["ttc_hours"].notna()]
        mttr_overall = closed_for_mttr["ttc_hours"].mean()
    else:
        mttr_overall = None

    # ---------- 3) Breakdown tables ----------
    # Volume by priority
    if "priority" in df.columns:
        pri_counts = (
            df["priority"]
            .value_counts()
            .sort_index()
            .rename_axis("priority")
            .reset_index(name="count")
        )
    else:
        pri_counts = pd.DataFrame(columns=["priority", "count"])

    # SLA breach rate by priority
    if {"priority", "sla_breach"} <= set(df.columns):
        pri_breach = (
            df.groupby("priority")["sla_breach"]
            .mean()
            .mul(100)
            .rename("breach_rate_pct")
            .reset_index()
            .sort_values("priority")
        )
    else:
        pri_breach = pd.DataFrame(columns=["priority", "breach_rate_pct"])

    # MTTR by assignment group
    if {"assignment_group", "ttc_hours"} <= set(df.columns):
        mttr_by_group = (
            df[df["ttc_hours"].notna()]
            .groupby("assignment_group")["ttc_hours"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .rename("mttr_hours")
            .reset_index()
        )
    else:
        mttr_by_group = pd.DataFrame(columns=["assignment_group", "mttr_hours"])

    # ---------- 3.5) PNG chart: SLA Breach Rate by Priority ----------
    if not pri_breach.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(pri_breach["priority"], pri_breach["breach_rate_pct"])
        ax.set_title("SLA Breach Rate by Priority")
        ax.set_xlabel("Priority")
        ax.set_ylabel("Breach Rate (%)")
        plt.tight_layout()
        plt.savefig(png_path)
        plt.close(fig)
        print(f"PNG chart written to {png_path.resolve()}")
    else:
        print("No data available to generate SLA breach chart PNG.")

    # ---------- 4) Build PDF report ----------
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=LETTER)
    story = []

    # Title
    story.append(Paragraph("ServiceNow Incident Health Report", styles["Title"]))
    story.append(Spacer(1, 10))

    # Executive summary paragraph
    summary_text = (
        f"This report summarizes {total_clean:,} ServiceNow-style incident records "
        f"after removing {removed_dupes:,} duplicate rows. "
    )
    if mttr_overall is not None:
        summary_text += (
            f"The average time to resolve a ticket is approximately {mttr_overall:,.1f} hours, "
        )
    if "sla_breach" in df.columns:
        summary_text += (
            f"with an overall SLA breach rate of {overall_breach_rate:,.1f}%. "
        )
    if "closed_at" in df.columns:
        summary_text += (
            f"Currently, {closed_count:,} incidents are resolved/closed "
            f"({resolved_rate:,.1f}% of all tickets), and {open_count:,} remain open."
        )

    story.append(Paragraph(summary_text, styles["BodyText"]))
    story.append(Spacer(1, 12))

    # KPI table
    kpi_rows = [
        ["Metric", "Value"],
        ["Rows (raw)", f"{total_raw:,}"],
        ["Rows (clean)", f"{total_clean:,}"],
        ["Removed duplicates", f"{removed_dupes:,}"],
        ["Resolved/Closed incidents", f"{closed_count:,}"],
        ["Open incidents", f"{open_count:,}"],
        ["Resolved/Closed rate", f"{resolved_rate:,.1f}%"],
        ["Overall SLA breach rate", f"{overall_breach_rate:,.1f}%"],
    ]
    if mttr_overall is not None:
        kpi_rows.append(["Average time to close (MTTR)", f"{mttr_overall:,.1f} hours"])

    kpi_table = Table(kpi_rows, hAlign="LEFT")
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    story.append(Paragraph("<b>Key KPIs</b>", styles["Heading3"]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # Volume by priority table
    if not pri_counts.empty:
        vol_rows = [["Priority", "Incident Count"]]
        vol_rows += [
            [row["priority"], f"{int(row['count']):,}"]
            for _, row in pri_counts.iterrows()
        ]
        vol_table = Table(vol_rows, hAlign="LEFT")
        vol_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(Paragraph("<b>Incident Volume by Priority</b>", styles["Heading3"]))
        story.append(vol_table)
        story.append(Spacer(1, 14))

    # SLA breach rate by priority
    if not pri_breach.empty:
        breach_rows = [["Priority", "SLA Breach Rate (%)"]]
        breach_rows += [
            [row["priority"], f"{row['breach_rate_pct']:,.1f}%"]
            for _, row in pri_breach.iterrows()
        ]
        breach_table = Table(breach_rows, hAlign="LEFT")
        breach_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(
            Paragraph("<b>SLA Breach Rate by Priority</b>", styles["Heading3"])
        )
        story.append(breach_table)
        story.append(Spacer(1, 14))

    # MTTR by assignment group
    if not mttr_by_group.empty:
        mttr_rows = [["Assignment Group", "MTTR (hours)"]]
        mttr_rows += [
            [row["assignment_group"], f"{row['mttr_hours']:,.1f}"]
            for _, row in mttr_by_group.iterrows()
        ]
        mttr_table = Table(mttr_rows, hAlign="LEFT")
        mttr_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(
            Paragraph("<b>Top 10 Assignment Groups by MTTR</b>", styles["Heading3"])
        )
        story.append(mttr_table)
        story.append(Spacer(1, 14))

    doc.build(story)
    print(f"Report written to {pdf_path.resolve()}")
    print(f"Cleaned CSV written to {clean_path.resolve()}")


if __name__ == "__main__":
    build_sn_report()
