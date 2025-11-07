
<h1 align="center">🧰 Data Cleaning Demos — Powered by Python 🐍</h1>

<p align="center">
  <a href="#"><img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue.svg?logo=python&logoColor=white"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="#"><img alt="Build" src="https://img.shields.io/badge/build-passing-brightgreen.svg"></a>
  <a href="#"><img alt="Made with" src="https://img.shields.io/badge/made%20with-love%20%26%20pandas-red"></a>
</p>

---

### 💡 Overview
Practical, reproducible **data cleaning and automation demos** using **Python, pandas, and reportlab**.  
Each folder contains a complete mini-project: code, data, and visual outputs that demonstrate professional data-analysis workflows.

---

## 🔹 Projects Included

### 1️⃣ [Sales Data Cleaning Demo](./sales_data_cleaning_demo)
**Goal:** Clean and visualize messy sales data to uncover insights.

**Highlights**
- Removes duplicates and missing values  
- Calculates total revenue  
- Generates a PDF summary and top-product chart  

**Key Files**
- `sales_raw.csv` – raw dataset  
- `sales_cleaned.csv` – cleaned dataset  
- `sales_summary.pdf` – summary report  
- `top_products.png` – chart visualization  

**Run It**
```bash
cd sales_data_cleaning_demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make report
````

---

### 2️⃣ [ServiceNow Incident Analysis Demo](./servicenow_incident_analysis_demo)

**Goal:** Analyze ServiceNow-style incident data for SLA health and team performance.

**Highlights**

* Cleans incident exports (duplicates, nulls)
* Calculates SLA breach rates and MTTR
* Produces PDF health report with charts

**Key Files**

* `sn_incidents_raw.csv` – simulated ServiceNow export
* `sn_incidents_cleaned.csv` – cleaned dataset
* `sn_summary.pdf` – report with KPIs and visuals

**Run It**

```bash
cd servicenow_incident_analysis_demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make report
```

---

## ⚙️ Tech Stack

* **Python 3.10+**
* **pandas** – data cleaning & manipulation
* **matplotlib** – charting
* **reportlab** – automated PDF reporting
* **Makefile** – one-command reproducibility

---

## 🚀 Why It Exists

This repository demonstrates **client-ready data cleaning workflows** ideal for:

* Freelance portfolios (Upwork/Fiverr)
* Python & pandas practice projects
* Automation examples for ServiceNow and business reporting

Each project includes:

* Reproducible code
* Synthetic datasets
* Visual and PDF deliverables
* `make report` for instant rebuilds

---

## 👩🏽‍💻 Author

**Samara Gaul**
ServiceNow Developer & Data Automation Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/samarag-developer)
[![GitHub](https://img.shields.io/badge/GitHub-Samara617-black?logo=github)](https://github.com/Samara617)

---



### 🪶 License

This project is licensed under the **MIT License** — free to fork and reuse with credit.

```


