# 🛍️ E-Commerce Business Intelligence & Sales Prediction Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/ScikitLearn-1.3+-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-MySQL%20%7C%20SQLite-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-Reports-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

**An end-to-end data analytics and machine learning project demonstrating professional-grade skills across the full data science lifecycle — from raw data ingestion to executive dashboards and sales forecasting.**

[Key Features](#-key-features) • [Project Structure](#-project-structure) • [Quick Start](#-quick-start) • [Dashboard](#-power-bi-dashboard) • [ML Models](#-machine-learning-models) • [Business Insights](#-business-insights)

</div>

---

## 📌 Project Overview

This project simulates a **real-world e-commerce analytics platform** built on Amazon Sale Report data. It covers every stage of a professional data analytics workflow:

| Stage | Tools | Output |
|---|---|---|
| Data Ingestion & Cleaning | Python, Pandas | Cleaned CSV + Quality Report |
| SQL Analytics | SQLite / MySQL | 25 Business Queries + Excel Report |
| Customer Segmentation | K-Means, RFM | Segment Labels + Visualisations |
| Sales Forecasting | Random Forest, Gradient Boosting | 30-Day Revenue Forecast |
| Executive Dashboard | Matplotlib, Seaborn | 2-Page BI Dashboard |
| Power BI | DAX, Power Query | Interactive 4-Page Report |

### 📊 Dataset at a Glance

| Metric | Value |
|---|---|
| **Total Revenue** | ₹12.70 Crore |
| **Total Orders** | 50,000 |
| **Total Qty Sold** | 82,365 units |
| **Avg Order Value** | ₹2,540 |
| **Top Category** | Ethnic Dress |
| **Top State** | Maharashtra |
| **Cancellation Rate** | 9.94% |
| **Date Range** | March 2022 – June 2022 |
| **Product Categories** | 10 |
| **States Covered** | 20 |

---

## ✨ Key Features

### 🧹 Data Engineering
- Automated data quality audit with null/duplicate detection
- Column standardisation (snake_case, type casting)
- Outlier detection & Winsorisation (IQR method)
- Derived feature engineering (year, month, quarter, unit_price)
- Exportable JSON + TXT quality reports

### 🗄️ SQL Analytics (25 Queries)
- Star-schema design: `fact_orders` + 4 dimension tables
- 25 business queries across 6 analytical categories:
  - Overall KPIs | Time Trends | Product & Category | Geography | Channel | Customer Insights
- Window functions: `LAG`, `LEAD`, `NTILE`, `SUM OVER`, `RANK`
- Auto-generated styled Excel workbook with all query results

### 👥 Customer Segmentation
- **RFM Analysis** (Recency, Frequency, Monetary)
- **K-Means Clustering** with elbow + silhouette method
- Automatic cluster labelling: High Value / Regular / Occasional / At Risk
- PCA 2D cluster projection visualisation
- RFM heatmaps by score dimension

### 🤖 Machine Learning — Sales Forecasting
- 4 models compared: Linear Regression, Ridge, **Random Forest**, Gradient Boosting
- Time-series feature engineering: lag features (1, 2, 3, 7, 14 days), rolling averages
- Time-series train/test split (80/20 temporal)
- **30-day rolling revenue forecast** with confidence interval
- Feature importance analysis

### 📈 Dashboards & Visualisations
- 2-page executive dashboard (24×18 inch, 150 DPI)
- Dark corporate theme throughout
- Page 1: KPI Cards, Monthly Trend, Category Revenue, Top States, Status Distribution
- Page 2: Daily rolling averages, Category × Month heatmap, B2B/B2C trend, Promotion impact

### 📊 Power BI Dashboard (4 Pages)
- 15+ DAX measures with time-intelligence
- Interactive slicers: Date, Category, State, Status, Channel, B2B
- Custom dark JSON theme included
- Mobile layout support

---

## 📁 Project Structure

```
E-Commerce-Business-Intelligence-Sales-Prediction-Platform/
│
├── 📂 Dataset/
│   ├── Amazon_Sale_Report.csv              # Raw dataset (50,200 rows)
│   ├── Amazon_Sale_Report_Cleaned.csv      # Cleaned dataset (50,000 rows)
│   ├── Customer_Segments.csv               # RFM + K-Means segment output
│   ├── Sales_Forecast.csv                  # 30-day revenue forecast
│   └── ecommerce_bi.db                     # SQLite database
│
├── 📂 Python/
│   ├── 00_run_all.py                       # ★ Master pipeline runner
│   ├── 01_data_cleaning.py                 # Data cleaning & quality report
│   ├── 02_customer_segmentation.py         # RFM + K-Means clustering
│   ├── 03_predictive_analytics.py          # ML models + 30-day forecast
│   ├── 04_executive_dashboard.py           # BI dashboard visualisations
│   ├── 05_sql_analytics_runner.py          # 25 SQL queries + Excel export
│   └── generate_dataset.py                 # Synthetic data generator
│
├── 📂 SQL/
│   ├── 01_schema_creation.sql              # Star schema DDL (MySQL)
│   ├── 02_data_import.sql                  # Staging + ETL procedures
│   ├── 03_business_analysis_queries.sql    # 25 business queries (MySQL)
│   └── query_catalogue.md                  # Query index + insights
│
├── 📂 PowerBI/
│   └── PowerBI_Setup_Guide.md              # DAX measures + setup guide
│
├── 📂 Reports/                             # All generated outputs
│   ├── data_quality_dashboard.png
│   ├── data_quality_report.json
│   ├── data_quality_report.txt
│   ├── executive_dashboard_p1.png
│   ├── executive_dashboard_p2.png
│   ├── customer_segmentation.png
│   ├── rfm_heatmap.png
│   ├── sales_prediction.png
│   ├── sql_analytics_summary.png
│   └── SQL_Analytics_Report.xlsx          # 27-sheet styled Excel report
│
├── 📂 Screenshots/                         # Power BI dashboard screenshots
│
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip
- (Optional) MySQL 8.0+ for production SQL deployment
- (Optional) Power BI Desktop for interactive dashboard

### 1. Clone / Download
```bash
git clone https://github.com/palakondapavan/ecommerce-bi-platform.git
cd ecommerce-bi-platform
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Full Pipeline (One Command)
```bash
python3 Python/00_run_all.py
```

This runs all 6 scripts in sequence and prints a full timing summary.

### 4. Run Individual Scripts
```bash
# Data Cleaning only
python3 Python/01_data_cleaning.py

# Customer Segmentation only
python3 Python/02_customer_segmentation.py

# ML Forecasting only
python3 Python/03_predictive_analytics.py

# Executive Dashboard only
python3 Python/04_executive_dashboard.py

# SQL Analytics + Excel Report
python3 Python/05_sql_analytics_runner.py
```

### 5. MySQL Setup (Optional — for production SQL)
```bash
# In MySQL client:
SOURCE SQL/01_schema_creation.sql;
SOURCE SQL/02_data_import.sql;
SOURCE SQL/03_business_analysis_queries.sql;
```

### 6. Power BI Setup
1. Open **Power BI Desktop**
2. Follow `PowerBI/PowerBI_Setup_Guide.md` step by step
3. Import `Dataset/Amazon_Sale_Report_Cleaned.csv`
4. Copy DAX measures from the guide
5. Import `PowerBI/ecommerce_theme.json` as custom theme

---

## 📊 Power BI Dashboard

### Page 1 — Executive Overview
| KPI Card | Value |
|---|---|
| Total Revenue | ₹12.70 Cr |
| Total Orders | 50,000 |
| Total Qty Sold | 82,365 |
| Avg Order Value | ₹2,540 |

**Visuals:** Monthly Revenue Trend, Order Status Donut, Top 10 Categories, Top 10 States Map, Sales Channel Split

### Page 2 — Product & Category Analysis
Category revenue matrix, top SKUs table, size distribution treemap, price histogram

### Page 3 — Geographic Analysis
India filled map by revenue, city rankings, state × category matrix

### Page 4 — Channel & Operations
Channel comparison, fulfilment split, B2B vs B2C trend, promotion impact

### DAX Measures Included
```
Total Revenue         Total Orders          Total Quantity Sold
Avg Order Value       Revenue MoM Change    Revenue MoM Growth %
Revenue YTD           Revenue PYTD          Revenue YoY %
Delivery Rate %       Cancellation Rate %   B2B Revenue %
Promo Lift %          Category Revenue Share %   Top Category
```

---

## 🤖 Machine Learning Models

### Feature Engineering
| Feature Type | Features |
|---|---|
| Calendar | day_of_week, day_of_month, week_number, month, quarter, is_weekend |
| Lag Features | revenue_lag_1/2/3/7/14, orders_lag_1/2/3/7/14 |
| Rolling Avg | revenue_roll_3/7/14 |

### Model Results

| Model | R² | MAE | RMSE | MAPE |
|---|---|---|---|---|
| **Random Forest** ⭐ | 0.105 | ₹45,373 | ₹54,271 | 5.9% |
| Gradient Boosting | -0.18 | ₹50,428 | ₹62,255 | 6.7% |
| Linear Regression | -0.83 | ₹63,885 | ₹77,556 | 8.6% |
| Ridge Regression | -0.77 | ₹62,156 | ₹76,234 | 8.2% |

> Note: Low R² scores are expected for highly volatile daily e-commerce revenue. The model's MAPE of 5.9% means the 30-day forecast is within 6% of actual values on average — acceptable for business planning.

### 30-Day Forecast
- **Total Forecast Revenue**: ₹2.37 Crore
- **Average Daily Revenue**: ₹7.89 Lakh
- **Confidence Interval**: ±15%

---

## 👥 Customer Segmentation

### RFM Methodology
- **Recency** — Days since last order (lower = better)
- **Frequency** — Number of orders placed
- **Monetary** — Total spend

### K-Means Results (K=3, Silhouette=0.46)

| Segment | Customers | Avg Spend | Revenue Share |
|---|---|---|---|
| 🏆 High Value | 6,145 | ₹6,103 | 39.7% |
| 🔄 Regular | 15,573 | ₹1,835 | 30.3% |
| 🛒 Occasional | 15,487 | ₹1,830 | 30.0% |

### Business Recommendations by Segment

**High Value Customers (6,145 — 39.7% revenue)**
- Launch VIP loyalty programme with exclusive early access
- Personalised product recommendations
- Premium packaging and dedicated customer support

**Regular Customers (15,573 — 30.3% revenue)**
- Re-engagement email campaigns with targeted offers
- Upsell to higher-value categories (Set, Saree)
- Bundle deals to increase order value

**Occasional Buyers (15,487 — 30.0% revenue)**
- Win-back campaigns with 10–15% discount coupons
- Push notifications for category restocks
- Exit-intent surveys to understand barriers

---

## 💡 Business Insights

### Revenue Insights
1. **Maharashtra** contributes the highest revenue (15.2%) — invest in localised marketing
2. **Ethnic Dress** and **Set** categories are top performers — prioritise inventory
3. **Expedited shipping** customers spend 12% more on average — upsell opportunity
4. **Amazon.in** channel drives 90%+ of revenue — diversify non-Amazon presence

### Operational Insights
5. **Friday and Saturday** record the highest daily orders — schedule promotions accordingly
6. **Cancellation rate of 9.94%** — review order confirmation flow and stock availability
7. **Amazon fulfilment** has 2.3% lower cancellation rate than merchant-fulfilled orders
8. **Promotions** increase average order value by 8.4% — expand promotion coverage

### Predictive Insights
9. **Lag-7 revenue** is the strongest predictor — last week's sales best predict current week
10. **Weekend patterns** (is_weekend) rank in top 5 features — factor into campaign timing
11. **30-day forecast shows ₹2.37 Crore** in projected revenue — align procurement ahead

---

## 🛠️ Technologies Used

| Category | Tool | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.10+ | Core scripting |
| Data Manipulation | Pandas | 2.0+ | ETL & analysis |
| Numerical | NumPy | 1.24+ | Array operations |
| Machine Learning | Scikit-Learn | 1.3+ | ML models |
| Visualisation | Matplotlib | 3.7+ | Charts & dashboards |
| Visualisation | Seaborn | 0.12+ | Statistical plots |
| Database | SQLite | Built-in | Portable SQL analytics |
| Database | MySQL | 8.0+ | Production database |
| Excel | OpenPyXL | 3.1+ | Styled Excel reports |
| BI Tool | Power BI Desktop | Latest | Interactive dashboard |

---

## 📈 SQL Query Categories

| Category | Queries | Topics |
|---|---|---|
| A — Overall KPIs | Q01–Q03 | Total Revenue, Order Status, B2B/B2C |
| B — Time Analysis | Q04–Q07 | Monthly/Quarterly/Weekly/Day-of-Week |
| C — Product & Category | Q08–Q12 | Revenue, Top SKUs, Size Distribution |
| D — Geography | Q13–Q15 | States, Cities, Cancellation by State |
| E — Channel & Ops | Q16–Q19 | Channel, Fulfilment, Shipping, Promotions |
| F — Customer Insights | Q20–Q25 | High-Value Tiers, RFM, Executive Summary |

---

## 🔮 Future Enhancements

- [ ] **Real-time Dashboard** — Connect to live MySQL via Power BI DirectQuery
- [ ] **Deep Learning Forecast** — LSTM / Transformer for sequence modelling
- [ ] **NLP Product Reviews** — Sentiment analysis on product descriptions
- [ ] **Price Elasticity Model** — Quantify demand response to price changes
- [ ] **Inventory Optimisation** — EOQ model integrated with demand forecast
- [ ] **Churn Prediction** — Logistic Regression / XGBoost on customer activity
- [ ] **A/B Test Framework** — Statistical significance testing for promotions
- [ ] **REST API** — FastAPI endpoints serving model predictions
- [ ] **Streamlit App** — Interactive self-serve analytics portal
- [ ] **Airflow DAG** — Scheduled pipeline automation

---

## 🎯 Skills Demonstrated

This project is suitable as a portfolio project for:

| Role | Relevant Components |
|---|---|
| **Data Analyst** | Cleaning, SQL (25 queries), Excel report, BI Dashboard |
| **Business Analyst** | KPI design, RFM insights, business recommendations |
| **Data Engineer** | Star schema design, ETL pipeline, SQLite/MySQL scripts |
| **ML Engineer** | Feature engineering, 4 ML models, forecasting, evaluation |
| **Python Developer** | Modular scripts, OOP helpers, subprocess pipeline runner |
| **Power BI Developer** | DAX measures, data model, theme design, 4-page report |

---


---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
<i>Built as a professional portfolio project demonstrating end-to-end data analytics, business intelligence, and machine learning capabilities.</i>
</div>
