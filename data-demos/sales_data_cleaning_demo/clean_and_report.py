import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def main():
    base = Path(".")
    raw_path = base / "sales_raw.csv"
    clean_path = base / "sales_cleaned.csv"
    chart_path = base / "top_products.png"
    summary_pdf_path = base / "sales_summary.pdf"

    df_raw = pd.read_csv(raw_path)

    # Basic cleaning
    before = len(df_raw)
    df = df_raw.drop_duplicates()
    after = len(df)

    if "quantity" in df.columns and "price" in df.columns:
        qty_med = df["quantity"].median()
        price_med = df["price"].median()
        df["quantity"] = df["quantity"].fillna(qty_med).astype(int)
        df["price"] = df["price"].fillna(price_med)
        df["revenue"] = df["quantity"] * df["price"]

    if "product" in df.columns:
        df["product"] = df["product"].fillna("Unknown")
    if "region" in df.columns:
        df["region"] = df["region"].fillna("Unknown")

    df.to_csv(clean_path, index=False)

    # Chart: top products
    if {"product", "revenue"} <= set(df.columns):
        top = (
            df.groupby("product")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        ax = top.plot(kind="bar", figsize=(10, 6))
        ax.set_title("Top 10 Products by Revenue")
        ax.set_xlabel("Product")
        ax.set_ylabel("Revenue")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

    # PDF summary
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(summary_pdf_path), pagesize=LETTER)
    story = []
    story.append(Paragraph("Sales Summary Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Cleaned and analyzed sales records, identified missing entries, "
        "and visualized top products by revenue.",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 12))

    metrics = [
        ["Metric", "Value"],
        ["Rows (raw)", f"{before:,}"],
        ["Rows (clean)", f"{after:,}"],
        ["Removed duplicates", f"{before - after:,}"],
    ]
    tbl = Table(metrics, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    doc.build(story)
    print("Done → sales_cleaned.csv, top_products.png (if product/revenue exist), sales_summary.pdf")

if __name__ == "__main__":
    main()
