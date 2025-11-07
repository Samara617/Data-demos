# Sales Data Cleaning Demo (Python + pandas)

Cleaned and analyzed 10K+ sales records, identified missing entries and duplicates, and visualized top products by revenue.

## Files

- `sales_raw.csv` – raw sales data with duplicates and missing values
- `sales_cleaned.csv` – cleaned dataset with fixed nulls and recomputed revenue
- `sales_summary.pdf` – short report with key metrics and a chart
- `top_products.png` – bar chart of top products by revenue

## How to Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
make report      # or: python clean_and_report.py
