# ServiceNow Incident Health Demo (Python + pandas)

ServiceNow-style incident dataset: cleaned and analyzed incident records, fixed missing values/duplicates,
and visualized SLA breach risk and MTTR by assignment group.

## Files

- `sn_incidents_raw.csv` – raw incident export with duplicates and nulls
- `sn_incidents_cleaned.csv` – cleaned incidents with normalized fields
- `sn_summary.pdf` – incident health report with KPIs and charts

## How to Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
make report      # or: python sn_clean_and_report.py
