"""
============================================================
 E-Commerce BI & Sales Prediction Platform
 Script 01 — Data Cleaning & Quality Report
============================================================
 Author : Data Analytics Team
 Purpose: Load raw Amazon Sale Report CSV, clean it, generate
          a data quality report, and export a clean dataset.
============================================================
"""

# ── Standard Library ──────────────────────────────────────
import os
import json
import warnings
warnings.filterwarnings("ignore")

# ── Third-Party ───────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(BASE, "Dataset", "Amazon_Sale_Report.csv")
CLN_CSV = os.path.join(BASE, "Dataset", "Amazon_Sale_Report_Cleaned.csv")
RPT_DIR = os.path.join(BASE, "Reports")
os.makedirs(RPT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════
#  STEP 1 — Load Raw Data
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 1 : Loading Raw Dataset")
print("="*60)

df_raw = pd.read_csv(RAW_CSV, low_memory=False)
print(f"  Rows    : {len(df_raw):,}")
print(f"  Columns : {df_raw.shape[1]}")
print(f"  Memory  : {df_raw.memory_usage(deep=True).sum() / 1e6:.2f} MB")

# ═══════════════════════════════════════════════════════════
#  STEP 2 — Pre-Cleaning Quality Snapshot
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 2 : Pre-Cleaning Quality Snapshot")
print("="*60)

def quality_snapshot(df, label=""):
    """Return a DataFrame describing missing values and dtypes."""
    total = len(df)
    snap  = pd.DataFrame({
        "Column"        : df.columns,
        "Dtype"         : df.dtypes.values,
        "Non_Null"      : df.count().values,
        "Null_Count"    : df.isnull().sum().values,
        "Null_Pct"      : (df.isnull().sum().values / total * 100).round(2),
        "Unique_Values" : df.nunique().values,
        "Sample"        : [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "N/A"
                           for c in df.columns],
    })
    print(f"\n  [{label}] Shape: {df.shape}")
    print(snap[["Column","Dtype","Null_Count","Null_Pct","Unique_Values"]].to_string(index=False))
    return snap

snap_before = quality_snapshot(df_raw, "BEFORE CLEANING")
dup_before  = df_raw.duplicated().sum()
print(f"\n  Duplicate rows (before) : {dup_before:,}")

# ═══════════════════════════════════════════════════════════
#  STEP 3 — Column Standardisation
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 3 : Standardising Column Names")
print("="*60)

df = df_raw.copy()

# Strip whitespace, lowercase, replace special chars with underscores
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[\s\-]+", "_", regex=True)
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)
print("  Standardised columns:")
for c in df.columns:
    print(f"    • {c}")

# ═══════════════════════════════════════════════════════════
#  STEP 4 — Remove Duplicates
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 4 : Removing Duplicates")
print("="*60)

before = len(df)
df.drop_duplicates(inplace=True)
after  = len(df)
print(f"  Removed {before - after:,} duplicate rows  ({before:,} → {after:,})")

# ═══════════════════════════════════════════════════════════
#  STEP 5 — Date Column Conversion
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 5 : Converting Date Column")
print("="*60)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
null_dates  = df["date"].isnull().sum()
print(f"  Date column dtype  : {df['date'].dtype}")
print(f"  Null dates         : {null_dates}")
print(f"  Date range         : {df['date'].min().date()}  →  {df['date'].max().date()}")

# Drop rows where date is null (can't use for time-series analysis)
df = df[df["date"].notna()].copy()
print(f"  Rows after dropping null dates : {len(df):,}")

# Derived date features
df["year"]        = df["date"].dt.year
df["month"]       = df["date"].dt.month
df["month_name"]  = df["date"].dt.strftime("%b")
df["quarter"]     = df["date"].dt.quarter
df["week"]        = df["date"].dt.isocalendar().week.astype(int)
df["day_of_week"] = df["date"].dt.day_name()

# ═══════════════════════════════════════════════════════════
#  STEP 6 — Handle Missing Values
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 6 : Handling Missing Values")
print("="*60)

# Amount — fill with median price * quantity
amount_median = df["amount"].median()
amount_null   = df["amount"].isnull().sum()
df["amount"]  = df["amount"].fillna(amount_median)
print(f"  'amount'     : filled {amount_null:,} nulls with median  (₹{amount_median:,.2f})")

# ship_city — fill with 'Unknown'
city_null        = df["ship_city"].isnull().sum()
df["ship_city"]  = df["ship_city"].fillna("Unknown")
print(f"  'ship_city'  : filled {city_null:,} nulls with 'Unknown'")

# ship_state — fill with 'Unknown'
state_null        = df["ship_state"].isnull().sum()
df["ship_state"]  = df["ship_state"].fillna("Unknown")
print(f"  'ship_state' : filled {state_null:,} nulls with 'Unknown'")

# status — fill with mode
status_mode  = df["status"].mode()[0]
status_null  = df["status"].isnull().sum()
df["status"] = df["status"].fillna(status_mode)
print(f"  'status'     : filled {status_null:,} nulls with mode  ('{status_mode}')")

# courier_status — fill with 'Unknown'
df["courier_status"] = df["courier_status"].fillna("Unknown")

# promotion_ids — fill with 'No Promotion'
df["promotion_ids"] = df["promotion_ids"].fillna("No Promotion")

# fulfilled_by — fill with 'Unknown'
df["fulfilled_by"] = df["fulfilled_by"].fillna("Unknown")

# ═══════════════════════════════════════════════════════════
#  STEP 7 — Type Casting & Value Cleaning
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 7 : Type Casting & Value Standardisation")
print("="*60)

# Ensure numeric types
df["qty"]    = pd.to_numeric(df["qty"],    errors="coerce").fillna(1).astype(int)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(amount_median).round(2)

# Derived: unit price
df["unit_price"] = (df["amount"] / df["qty"]).round(2)

# Standardise string columns
str_cols = ["status","fulfilment","sales_channel_","ship_service_level",
            "style","category","size","ship_city","ship_state","ship_country","currency"]
for col in str_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.title()

# Standardise B2B column
df["b2b"] = df["b2b"].astype(str).str.strip().str.upper().map(
    {"TRUE":"Yes","FALSE":"No","YES":"Yes","NO":"No"}
).fillna("No")

# Rename noisy columns
if "sales_channel_" in df.columns:
    df.rename(columns={"sales_channel_": "sales_channel"}, inplace=True)

print("  Numeric types confirmed: qty (int), amount (float), unit_price (float)")
print("  String columns title-cased")
print("  B2B column normalised (Yes/No)")

# ═══════════════════════════════════════════════════════════
#  STEP 8 — Outlier Detection & Capping
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 8 : Outlier Detection (IQR Method) on 'amount'")
print("="*60)

Q1  = df["amount"].quantile(0.25)
Q3  = df["amount"].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 3 * IQR
upper_bound = Q3 + 3 * IQR

outliers = df[(df["amount"] < lower_bound) | (df["amount"] > upper_bound)]
print(f"  Q1 = ₹{Q1:,.2f}   Q3 = ₹{Q3:,.2f}   IQR = ₹{IQR:,.2f}")
print(f"  Lower bound (Q1-3×IQR) = ₹{lower_bound:,.2f}")
print(f"  Upper bound (Q3+3×IQR) = ₹{upper_bound:,.2f}")
print(f"  Outlier rows detected  : {len(outliers):,}")

# Cap (Winsorise) rather than drop
df["amount"] = df["amount"].clip(lower=max(0, lower_bound), upper=upper_bound)
print("  Outliers capped (Winsorisation applied)")

# ═══════════════════════════════════════════════════════════
#  STEP 9 — Post-Cleaning Quality Snapshot
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 9 : Post-Cleaning Quality Snapshot")
print("="*60)

snap_after  = quality_snapshot(df, "AFTER CLEANING")
dup_after   = df.duplicated().sum()
print(f"\n  Duplicate rows (after)  : {dup_after:,}")

# ═══════════════════════════════════════════════════════════
#  STEP 10 — Export Cleaned Dataset
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 10: Exporting Cleaned Dataset")
print("="*60)

df.to_csv(CLN_CSV, index=False)
print(f"  Cleaned CSV  → {CLN_CSV}")
print(f"  Final shape  : {df.shape}")

# ═══════════════════════════════════════════════════════════
#  STEP 11 — Data Quality Report (Text + JSON)
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 11: Writing Data Quality Report")
print("="*60)

report = {
    "report_generated_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "raw_dataset"         : {
        "rows"            : int(df_raw.shape[0]),
        "columns"         : int(df_raw.shape[1]),
        "duplicates"      : int(dup_before),
        "total_nulls"     : int(df_raw.isnull().sum().sum()),
        "memory_mb"       : round(df_raw.memory_usage(deep=True).sum() / 1e6, 2),
    },
    "cleaned_dataset"     : {
        "rows"            : int(df.shape[0]),
        "columns"         : int(df.shape[1]),
        "duplicates"      : int(dup_after),
        "total_nulls"     : int(df.isnull().sum().sum()),
        "memory_mb"       : round(df.memory_usage(deep=True).sum() / 1e6, 2),
        "date_range"      : f"{df['date'].min().date()} to {df['date'].max().date()}",
        "total_revenue"   : round(float(df["amount"].sum()), 2),
        "total_orders"    : int(df["order_id"].nunique()),
        "total_qty"       : int(df["qty"].sum()),
        "avg_order_value" : round(float(df["amount"].mean()), 2),
        "categories"      : int(df["category"].nunique()),
        "states"          : int(df["ship_state"].nunique()),
    },
    "cleaning_actions"    : [
        f"Removed {dup_before} duplicate rows",
        "Standardised all column names (lowercase, underscores)",
        "Converted 'date' to datetime, extracted year/month/quarter/week features",
        f"Filled {amount_null} missing 'amount' values with median (₹{amount_median:,.2f})",
        f"Filled {city_null} missing 'ship_city' with 'Unknown'",
        f"Filled {state_null} missing 'ship_state' with 'Unknown'",
        f"Filled {status_null} missing 'status' with mode ('{status_mode}')",
        "Filled missing courier_status, promotion_ids, fulfilled_by",
        "Computed unit_price = amount / qty",
        "Capped amount outliers via IQR Winsorisation (3×IQR)",
        "Normalised B2B column to Yes/No",
        "Title-cased all categorical string columns",
    ],
}

json_path = os.path.join(RPT_DIR, "data_quality_report.json")
with open(json_path, "w") as f:
    json.dump(report, f, indent=2)
print(f"  JSON report  → {json_path}")

# Text report
txt_path  = os.path.join(RPT_DIR, "data_quality_report.txt")
with open(txt_path, "w") as f:
    f.write("="*65 + "\n")
    f.write("  E-COMMERCE BI PLATFORM — DATA QUALITY REPORT\n")
    f.write(f"  Generated: {report['report_generated_at']}\n")
    f.write("="*65 + "\n\n")
    f.write("RAW DATASET\n")
    f.write("-"*40 + "\n")
    for k, v in report["raw_dataset"].items():
        f.write(f"  {k:<25}: {v}\n")
    f.write("\nCLEANED DATASET\n")
    f.write("-"*40 + "\n")
    for k, v in report["cleaned_dataset"].items():
        f.write(f"  {k:<25}: {v}\n")
    f.write("\nCLEANING ACTIONS PERFORMED\n")
    f.write("-"*40 + "\n")
    for i, action in enumerate(report["cleaning_actions"], 1):
        f.write(f"  {i:02d}. {action}\n")
print(f"  TXT report   → {txt_path}")

# ═══════════════════════════════════════════════════════════
#  STEP 12 — Quality Visualisations
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 12: Saving Quality Visualisation")
print("="*60)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.patch.set_facecolor("#0f1117")
plt.suptitle("Data Quality Dashboard — Amazon Sale Report",
             color="white", fontsize=16, fontweight="bold", y=0.98)

colors = ["#00d4ff","#ff6b6b","#ffd700","#51cf66","#cc5de8","#ff8c00",
          "#20c997","#74c0fc","#f06595","#a9e34b"]

ax_style = dict(facecolor="#1a1d2e", tick_params=dict(colors="white"))

# ── Plot 1: Missing values heatmap (top cols) ──────────────
ax1 = axes[0, 0]
ax1.set_facecolor("#1a1d2e")
miss = snap_before[snap_before["Null_Pct"] > 0][["Column","Null_Pct"]].sort_values("Null_Pct", ascending=False)
if len(miss):
    bars = ax1.barh(miss["Column"], miss["Null_Pct"], color="#ff6b6b")
    ax1.set_xlabel("Missing %", color="white")
    ax1.set_title("Missing Values (Raw Dataset)", color="white", fontweight="bold")
    ax1.tick_params(colors="white")
    for spine in ax1.spines.values(): spine.set_edgecolor("#333")
    for bar, val in zip(bars, miss["Null_Pct"]):
        ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                 f"{val:.1f}%", va="center", color="white", fontsize=8)
else:
    ax1.text(0.5, 0.5, "No Missing Values\nin Raw Data",
             ha="center", va="center", color="white", fontsize=14)
    ax1.set_title("Missing Values (Raw Dataset)", color="white", fontweight="bold")

# ── Plot 2: Orders by Status ───────────────────────────────
ax2 = axes[0, 1]
ax2.set_facecolor("#1a1d2e")
status_counts = df["status"].value_counts()
wedges, texts, autotexts = ax2.pie(
    status_counts, labels=None, autopct="%1.1f%%",
    colors=colors[:len(status_counts)], startangle=140,
    pctdistance=0.8, wedgeprops=dict(linewidth=1.5, edgecolor="#0f1117"))
for t in autotexts: t.set_color("white"); t.set_fontsize(8)
ax2.legend(status_counts.index, loc="lower left", fontsize=7,
           labelcolor="white", facecolor="#1a1d2e", edgecolor="#333")
ax2.set_title("Order Status Distribution", color="white", fontweight="bold")

# ── Plot 3: Revenue by Category ───────────────────────────
ax3 = axes[1, 0]
ax3.set_facecolor("#1a1d2e")
cat_rev = df.groupby("category")["amount"].sum().sort_values(ascending=True)
bars = ax3.barh(cat_rev.index, cat_rev.values / 1e6, color=colors[:len(cat_rev)])
ax3.set_xlabel("Revenue (₹ Millions)", color="white")
ax3.set_title("Revenue by Category", color="white", fontweight="bold")
ax3.tick_params(colors="white")
for spine in ax3.spines.values(): spine.set_edgecolor("#333")

# ── Plot 4: Monthly Revenue Trend ─────────────────────────
ax4 = axes[1, 1]
ax4.set_facecolor("#1a1d2e")
monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().reset_index()
monthly["date"] = monthly["date"].astype(str)
ax4.plot(monthly["date"], monthly["amount"] / 1e6,
         color="#00d4ff", linewidth=2.5, marker="o", markersize=7)
ax4.fill_between(range(len(monthly)), monthly["amount"] / 1e6, alpha=0.15, color="#00d4ff")
ax4.set_xlabel("Month", color="white")
ax4.set_ylabel("Revenue (₹ Millions)", color="white")
ax4.set_title("Monthly Revenue Trend", color="white", fontweight="bold")
ax4.tick_params(colors="white", axis="x", rotation=30)
for spine in ax4.spines.values(): spine.set_edgecolor("#333")

plt.tight_layout(rect=[0, 0, 1, 0.96])
viz_path = os.path.join(RPT_DIR, "data_quality_dashboard.png")
plt.savefig(viz_path, dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print(f"  Dashboard PNG → {viz_path}")

print("\n" + "="*60)
print("  ✅  DATA CLEANING COMPLETE")
print(f"  Raw rows      : {len(df_raw):,}")
print(f"  Cleaned rows  : {len(df):,}")
print(f"  Total Revenue : ₹{df['amount'].sum():,.2f}")
print(f"  Total Orders  : {df['order_id'].nunique():,}")
print("="*60 + "\n")
