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

    # ---------- 1) Load raw data ----------
    df_raw = pd.read_csv(raw_path)

    # ---------- 2) Basic cleaning ----------
    before = len(df_raw)
    df = df_raw.drop_duplicates()
    after = len(df)
    removed_dupes = before - after

    # Normalize columns
    has_qty = "quantity" in df.columns
    has_price = "price" in df.columns
    has_product = "product" in df.columns
    has_region = "region" in df.columns
    has_customer = "customer" in df.columns

    # Parse dates
    if "date" in df.columns:
        df["order_date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["order_date"] = pd.NaT

    # Quantity & price
    if has_qty:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        qty_med = df["quantity"].median()
        df["quantity"] = df["quantity"].fillna(qty_med).astype(int)

    if has_price:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        price_med = df["price"].median()
        df["price"] = df["price"].fillna(price_med)

    # Categorical cleanup
    if has_product:
        df["product"] = df["product"].fillna("Unknown")
    if has_region:
        df["region"] = df["region"].fillna("Unknown")
    if has_customer:
        df["customer"] = df["customer"].fillna("Unknown")

    # Revenue
    if has_qty and has_price:
        df["revenue"] = df["quantity"] * df["price"]

    has_revenue = "revenue" in df.columns

    # Save cleaned data
    df.to_csv(clean_path, index=False)

    # ---------- 3) Enterprise-style metrics ----------

    # Deal count = number of orders
    deals_count = df["order_id"].nunique() if "order_id" in df.columns else len(df)

    # Total revenue & average deal size
    if has_revenue:
        total_revenue = df["revenue"].sum()
        avg_deal_size = df["revenue"].mean()
    else:
        total_revenue = None
        avg_deal_size = None

    # CLTV (approx) – average revenue per customer over dataset window
    if has_customer and has_revenue:
        rev_per_customer = df.groupby("customer")["revenue"].sum()
        avg_cltv = rev_per_customer.mean()
    else:
        rev_per_customer = pd.Series(dtype=float)
        avg_cltv = None

    # Monthly revenue & revenue growth (last month vs previous)
    if has_revenue and df["order_date"].notna().any():
        df["year_month"] = df["order_date"].dt.to_period("M")
        monthly_rev = (
            df.groupby("year_month")["revenue"]
            .sum()
            .sort_index()
        )
        if len(monthly_rev) >= 2:
            last_rev = monthly_rev.iloc[-1]
            prev_rev = monthly_rev.iloc[-2]
            if prev_rev != 0:
                revenue_growth_pct = (last_rev - prev_rev) / prev_rev * 100.0
            else:
                revenue_growth_pct = None
        else:
            revenue_growth_pct = None
    else:
        monthly_rev = pd.Series(dtype=float)
        revenue_growth_pct = None

    # Churn rate (approx) – customers active in prev month but not in last month
    if has_customer and df.get("year_month") is not None and not monthly_rev.empty:
        last_period = monthly_rev.index[-1]
        prev_period = monthly_rev.index[-2] if len(monthly_rev) >= 2 else None

        if prev_period is not None:
            prev_customers = set(
                df.loc[df["year_month"] == prev_period, "customer"].dropna().unique()
            )
            last_customers = set(
                df.loc[df["year_month"] == last_period, "customer"].dropna().unique()
            )
            if prev_customers:
                churned_customers = prev_customers - last_customers
                churn_rate = len(churned_customers) / len(prev_customers) * 100.0
            else:
                churn_rate = None
        else:
            churn_rate = None
    else:
        churn_rate = None

    # Revenue by region
    if has_region and has_revenue:
        rev_by_region = (
            df.groupby("region")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
    else:
        rev_by_region = pd.DataFrame(columns=["region", "revenue"])

    # Top products by revenue
    if has_product and has_revenue:
        top_products = (
            df.groupby("product")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
    else:
        top_products = pd.DataFrame(columns=["product", "revenue"])

    # Top customers by lifetime value
    if not rev_per_customer.empty:
        top_customers = (
            rev_per_customer.sort_values(ascending=False)
            .head(10)
            .rename("revenue")
            .reset_index()
        )
    else:
        top_customers = pd.DataFrame(columns=["customer", "revenue"])

    # ---------- 4) Chart: Top products by revenue ----------
    chart_generated = False
    if not top_products.empty:
        chart_data = top_products.set_index("product")["revenue"]
        ax = chart_data.plot(kind="bar", figsize=(10, 6))
        ax.set_title("Top 10 Products by Revenue")
        ax.set_xlabel("Product")
        ax.set_ylabel("Revenue")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        chart_generated = True

    # ---------- 5) Build PDF report ----------
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(summary_pdf_path), pagesize=LETTER)
    story = []

    # Title
    story.append(Paragraph("Enterprise Sales Summary", styles["Title"]))
    story.append(Spacer(1, 12))

    # Executive summary
    summary_bits = [
        # f"This report analyzes {deals_count:,} deals after cleaning {total_rows_clean := after:,} rows ",
        f"and removing {removed_dupes:,} duplicate records from the original dataset of {before:,} rows. "
    ]
    if total_revenue is not None:
        summary_bits.append(
            f"Total revenue over the period is approximately ${total_revenue:,.2f}. "
        )
    if avg_deal_size is not None:
        summary_bits.append(
            f"The average deal size is ${avg_deal_size:,.2f}. "
        )
    if avg_cltv is not None:
        summary_bits.append(
            f"Average revenue per customer (CLTV over this data window) is about ${avg_cltv:,.2f}. "
        )
    if revenue_growth_pct is not None:
        summary_bits.append(
            f"Recent month-over-month revenue growth is {revenue_growth_pct:,.1f}%. "
        )
    if churn_rate is not None:
        summary_bits.append(
            f"Estimated customer churn between the last two months is {churn_rate:,.1f}%."
        )

    story.append(Paragraph("".join(summary_bits), styles["BodyText"]))
    story.append(Spacer(1, 14))

    # KPI table
    kpi_rows = [
        ["Metric", "Value"],
        ["Deals (orders)", f"{deals_count:,}"],
        ["Rows (raw)", f"{before:,}"],
        ["Rows (clean)", f"{after:,}"],
        ["Removed duplicates", f"{removed_dupes:,}"],
    ]
    if total_revenue is not None:
        kpi_rows.append(["Total revenue", f"${total_revenue:,.2f}"])
    if avg_deal_size is not None:
        kpi_rows.append(["Average deal size", f"${avg_deal_size:,.2f}"])
    if avg_cltv is not None:
        kpi_rows.append(["Avg CLTV (data window)", f"${avg_cltv:,.2f}"])
    if revenue_growth_pct is not None:
        kpi_rows.append(["MoM revenue growth", f"{revenue_growth_pct:,.1f}%"])
    if churn_rate is not None:
        kpi_rows.append(["Customer churn (last 2 months)", f"{churn_rate:,.1f}%"])

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
    story.append(Paragraph("<b>Core Sales KPIs</b>", styles["Heading3"]))
    story.append(kpi_table)
    story.append(Spacer(1, 16))

    # Revenue by region
    if not rev_by_region.empty:
        region_rows = [["Region", "Revenue"]]
        region_rows += [
            [row["region"], f"${row["revenue"]:,.2f}"]
            for _, row in rev_by_region.iterrows()
        ]
        region_table = Table(region_rows, hAlign="LEFT")
        region_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(Paragraph("<b>Revenue by Region</b>", styles["Heading3"]))
        story.append(region_table)
        story.append(Spacer(1, 16))

    # Top products
    if not top_products.empty:
        prod_rows = [["Product", "Revenue"]]
        prod_rows += [
            [row["product"], f"${row["revenue"]:,.2f}"]
            for _, row in top_products.iterrows()
        ]
        prod_table = Table(prod_rows, hAlign="LEFT")
        prod_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(Paragraph("<b>Top 10 Products by Revenue</b>", styles["Heading3"]))
        story.append(prod_table)
        story.append(Spacer(1, 16))

    # Top customers
    if not top_customers.empty:
        cust_rows = [["Customer", "Revenue"]]
        cust_rows += [
            [row["customer"], f"${row["revenue"]:,.2f}"]
            for _, row in top_customers.iterrows()
        ]
        cust_table = Table(cust_rows, hAlign="LEFT")
        cust_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(Paragraph("<b>Top 10 Customers by Revenue</b>", styles["Heading3"]))
        story.append(cust_table)
        story.append(Spacer(1, 16))

    # Build PDF
    doc.build(story)

    print("Done →")
    print(f"  - {clean_path}")
    print(f"  - {summary_pdf_path}")
    if chart_generated:
        print(f"  - {chart_path}")


if __name__ == "__main__":

    main()

    
