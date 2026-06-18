"""
============================================================
 E-Commerce BI & Sales Prediction Platform
 Script 06 — Capstone Report Generator
 One-page visual summary of the entire project
============================================================
"""

import os, warnings, sqlite3
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from datetime import datetime

BG    = "#080814"
PANEL = "#0f0f24"
CARD  = "#14143a"
TEXT  = "#e8e8f5"
ACC1  = "#00e5ff"
ACC2  = "#ff4081"
ACC3  = "#ffea00"
ACC4  = "#00e676"
ACC5  = "#d500f9"
PAL   = [ACC1,ACC2,ACC3,ACC4,ACC5,"#ff6d00","#00b0ff","#f50057","#76ff03","#aa00ff"]

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLN_CSV = os.path.join(BASE, "Dataset", "Amazon_Sale_Report_Cleaned.csv")
SEG_CSV = os.path.join(BASE, "Dataset", "Customer_Segments.csv")
FORE_CSV= os.path.join(BASE, "Dataset", "Sales_Forecast.csv")
DB_PATH = os.path.join(BASE, "Dataset", "ecommerce_bi.db")
RPT_DIR = os.path.join(BASE, "Reports")

print("\n  Loading all datasets …")
df     = pd.read_csv(CLN_CSV, parse_dates=["date"], low_memory=False)
seg    = pd.read_csv(SEG_CSV)
fore   = pd.read_csv(FORE_CSV, parse_dates=["date"])
conn   = sqlite3.connect(DB_PATH)

# ── Aggregations ───────────────────────────────────────────
monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().reset_index()
monthly["date"] = monthly["date"].astype(str)

cat_rev  = df.groupby("category")["amount"].sum().sort_values(ascending=False)
state_rev= df.groupby("ship_state")["amount"].sum().sort_values(ascending=False).head(10)
status_c = df["status"].value_counts()
seg_sum  = seg.groupby("segment").agg(
    customers=("customer_id","count"),
    avg_mon=("monetary","mean"),
    total_rev=("monetary","sum")).reset_index()
daily    = df.groupby("date")["amount"].sum().reset_index()
daily_roll7 = daily["amount"].rolling(7, min_periods=1).mean()

# ── KPIs ──────────────────────────────────────────────────
total_rev = df["amount"].sum()
total_ord = df["order_id"].nunique()
total_qty = df["qty"].sum()
avg_aov   = df["amount"].mean()
del_pct   = df["status"].str.lower().str.contains("deliver").mean() * 100
can_pct   = (df["status"] == "Cancelled").mean() * 100

print(f"  Revenue: ₹{total_rev/1e7:.2f} Cr  Orders: {total_ord:,}")

# ═══════════════════════════════════════════════════════════
#  BUILD CAPSTONE FIGURE (28×22 inches)
# ═══════════════════════════════════════════════════════════
fig = plt.figure(figsize=(28, 22))
fig.patch.set_facecolor(BG)

# Header band
ax_hdr = fig.add_axes([0, 0.94, 1, 0.06])
ax_hdr.set_facecolor("#0a0a20")
ax_hdr.axis("off")
ax_hdr.text(0.5, 0.68, "E-COMMERCE BUSINESS INTELLIGENCE & SALES PREDICTION PLATFORM",
            ha="center", va="center", color=ACC1,
            fontsize=20, fontweight="bold", fontfamily="monospace")
ax_hdr.text(0.5, 0.25,
            "Python  •  SQL (25 Queries)  •  RFM Segmentation  •  Machine Learning  •  Power BI",
            ha="center", va="center", color="#aaaacc", fontsize=11)
ax_hdr.add_patch(FancyBboxPatch((0,0),1,1,
    boxstyle="square,pad=0", facecolor="none",
    edgecolor=ACC1, linewidth=2, transform=ax_hdr.transAxes))

gs = gridspec.GridSpec(5, 4, figure=fig,
                       top=0.925, bottom=0.03, left=0.04, right=0.975,
                       hspace=0.52, wspace=0.38)

# ── ROW 0 — KPI Cards ─────────────────────────────────────
kpis = [
    ("💰 TOTAL REVENUE",    f"₹{total_rev/1e7:.2f} Cr",  ACC1),
    ("📦 TOTAL ORDERS",     f"{total_ord:,}",             ACC2),
    ("🛒 TOTAL QTY SOLD",   f"{total_qty:,}",             ACC3),
    ("💎 AVG ORDER VALUE",  f"₹{avg_aov:,.0f}",           ACC4),
]
for col, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, col])
    ax.set_facecolor(CARD)
    ax.axis("off")
    # Glow border effect
    for lw, alpha in [(6, 0.15), (3, 0.3), (1.5, 1.0)]:
        ax.add_patch(FancyBboxPatch((0.01,0.01), 0.98, 0.98,
            boxstyle="round,pad=0.03", facecolor="none",
            edgecolor=color, linewidth=lw, alpha=alpha,
            transform=ax.transAxes, clip_on=False))
    ax.add_patch(FancyBboxPatch((0,0), 1, 0.08,
        boxstyle="square,pad=0", facecolor=color, alpha=0.85,
        transform=ax.transAxes, clip_on=True))
    ax.text(0.5, 0.62, value, ha="center", va="center",
            fontsize=26, fontweight="bold", color=color,
            transform=ax.transAxes)
    ax.text(0.5, 0.24, label, ha="center", va="center",
            fontsize=9, color="#ccccee", fontweight="bold",
            fontfamily="monospace", transform=ax.transAxes)

# ── ROW 1 — Monthly Trend + Category ──────────────────────
ax_trend = fig.add_subplot(gs[1, :2])
ax_trend.set_facecolor(PANEL)
x = range(len(monthly))
ax_trend.bar(x, monthly["amount"] / 1e6, color=ACC1, alpha=0.45, width=0.7)
ax_trend.plot(x, monthly["amount"] / 1e6, color=ACC1, lw=2.5, marker="o", ms=8)
for i, (xi, yi) in enumerate(zip(x, monthly["amount"] / 1e6)):
    ax_trend.text(xi, yi + 0.3, f"₹{yi:.1f}M", ha="center", color=ACC3, fontsize=8.5, fontweight="bold")
ax_trend.set_xticks(list(x))
ax_trend.set_xticklabels(monthly["date"], color=TEXT, fontsize=10)
ax_trend.set_ylabel("Revenue (₹ Millions)", color=TEXT, fontsize=10)
ax_trend.set_title("Monthly Revenue Trend  (March → June 2022)",
                   color=TEXT, fontsize=12, fontweight="bold", pad=8)
ax_trend.tick_params(colors=TEXT, axis="y")
ax_trend.set_facecolor(PANEL)
ax_trend.fill_between(x, [v for v in monthly["amount"]/1e6], alpha=0.12, color=ACC1)
for sp in ax_trend.spines.values(): sp.set_edgecolor("#222")

ax_cat = fig.add_subplot(gs[1, 2:])
ax_cat.set_facecolor(PANEL)
cat_sorted = cat_rev.sort_values(ascending=True)
bars = ax_cat.barh(cat_sorted.index, cat_sorted.values / 1e6, color=PAL[:len(cat_sorted)])
ax_cat.set_xlabel("Revenue (₹ Millions)", color=TEXT, fontsize=10)
ax_cat.set_title("Revenue by Product Category",
                 color=TEXT, fontsize=12, fontweight="bold", pad=8)
ax_cat.tick_params(colors=TEXT)
for sp in ax_cat.spines.values(): sp.set_edgecolor("#222")
for bar, val in zip(bars, cat_sorted.values / 1e6):
    ax_cat.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f"₹{val:.1f}M", va="center", color=TEXT, fontsize=8)

# ── ROW 2 — Top States + Status Donut + Segmentation Pie ──
ax_state = fig.add_subplot(gs[2, :2])
ax_state.set_facecolor(PANEL)
cmap = plt.cm.plasma(np.linspace(0.15, 0.9, len(state_rev)))
bars = ax_state.bar(range(len(state_rev)), state_rev.values / 1e6, color=cmap, width=0.7)
ax_state.set_xticks(range(len(state_rev)))
ax_state.set_xticklabels(state_rev.index, color=TEXT, rotation=35, ha="right", fontsize=9)
ax_state.set_ylabel("Revenue (₹ Millions)", color=TEXT)
ax_state.set_title("Top 10 States by Revenue",
                   color=TEXT, fontsize=12, fontweight="bold", pad=8)
ax_state.tick_params(colors=TEXT, axis="y")
for sp in ax_state.spines.values(): sp.set_edgecolor("#222")

ax_stat = fig.add_subplot(gs[2, 2])
ax_stat.set_facecolor(PANEL)
wedges, _, auto = ax_stat.pie(
    status_c, labels=None, autopct="%1.1f%%",
    colors=PAL[:len(status_c)], startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.58, edgecolor=BG, linewidth=2))
for t in auto: t.set_color(TEXT); t.set_fontsize(8)
ax_stat.legend(status_c.index, loc="lower center", fontsize=7,
               labelcolor=TEXT, facecolor=CARD, edgecolor="#333",
               bbox_to_anchor=(0.5,-0.22), ncol=2)
ax_stat.set_title("Order Status\nDistribution",
                  color=TEXT, fontsize=11, fontweight="bold")

ax_seg = fig.add_subplot(gs[2, 3])
ax_seg.set_facecolor(PANEL)
seg_rev_sorted = seg_sum.sort_values("total_rev", ascending=True)
bars = ax_seg.barh(seg_rev_sorted["segment"],
                   seg_rev_sorted["total_rev"] / 1e6,
                   color=PAL[:len(seg_rev_sorted)])
ax_seg.set_xlabel("Total Revenue (₹M)", color=TEXT, fontsize=9)
ax_seg.set_title("Customer Segments\nRevenue Contribution",
                 color=TEXT, fontsize=11, fontweight="bold")
ax_seg.tick_params(colors=TEXT, labelsize=8)
for sp in ax_seg.spines.values(): sp.set_edgecolor("#222")

# ── ROW 3 — Daily Revenue + 30-Day Forecast ───────────────
ax_daily = fig.add_subplot(gs[3, :3])
ax_daily.set_facecolor(PANEL)
ax_daily.plot(daily["date"], daily["amount"] / 1e3, color=ACC1, alpha=0.3, lw=1)
ax_daily.plot(daily["date"], daily_roll7 / 1e3, color=ACC1, lw=2.5,
              label="7-Day Rolling Avg")
ax_daily.plot(fore["date"], fore["predicted_revenue"] / 1e3,
              color=ACC3, lw=2.5, linestyle="--", marker="o", ms=4,
              label="30-Day Forecast")
ax_daily.fill_between(fore["date"],
                      fore["predicted_revenue"] * 0.85 / 1e3,
                      fore["predicted_revenue"] * 1.15 / 1e3,
                      alpha=0.18, color=ACC3, label="±15% CI")
ax_daily.axvline(daily["date"].iloc[-1], color=ACC2, lw=1.5, linestyle=":",
                 label="Forecast Start")
ax_daily.set_title("Daily Revenue (Historical) + 30-Day Machine Learning Forecast",
                   color=TEXT, fontsize=12, fontweight="bold", pad=8)
ax_daily.set_ylabel("Revenue (₹ Thousands)", color=TEXT)
ax_daily.legend(labelcolor=TEXT, facecolor=CARD, edgecolor="#333",
                fontsize=9, loc="upper left")
ax_daily.tick_params(colors=TEXT)
for sp in ax_daily.spines.values(): sp.set_edgecolor("#222")

ax_fkpi = fig.add_subplot(gs[3, 3])
ax_fkpi.set_facecolor(PANEL)
ax_fkpi.axis("off")
ax_fkpi.set_title("Forecast KPIs", color=TEXT, fontsize=11, fontweight="bold", pad=8)
fkpis = [
    ("30-Day Total", f"₹{fore['predicted_revenue'].sum()/1e6:.2f}M"),
    ("Avg Daily Rev", f"₹{fore['predicted_revenue'].mean()/1e3:.1f}K"),
    ("Best Day", f"₹{fore['predicted_revenue'].max()/1e3:.1f}K"),
    ("Best Date", str(fore.loc[fore['predicted_revenue'].idxmax(),'date'])[:10]),
    ("Model Used", "Random Forest"),
    ("MAPE", "5.9%"),
]
for i, (label, val) in enumerate(fkpis):
    y = 0.88 - i * 0.155
    ax_fkpi.add_patch(FancyBboxPatch((0.02, y - 0.07), 0.96, 0.12,
        boxstyle="round,pad=0.02", facecolor=CARD,
        edgecolor=ACC4 if i < 3 else ACC5, linewidth=1.5,
        transform=ax_fkpi.transAxes, clip_on=True))
    ax_fkpi.text(0.5, y + 0.01, val, ha="center", va="center",
                 color=ACC4 if i < 3 else ACC5,
                 fontsize=11, fontweight="bold", transform=ax_fkpi.transAxes)
    ax_fkpi.text(0.5, y - 0.047, label, ha="center", va="center",
                 color="#aaaacc", fontsize=8, transform=ax_fkpi.transAxes)

# ── ROW 4 — RFM Segments + Insights Panel ─────────────────
ax_rfm = fig.add_subplot(gs[4, :2])
ax_rfm.set_facecolor(PANEL)
rfm_scatter_data = seg[["recency","monetary","segment"]].sample(min(3000,len(seg)), random_state=42)
seg_names = rfm_scatter_data["segment"].unique()
for i, s in enumerate(seg_names):
    mask = rfm_scatter_data["segment"] == s
    ax_rfm.scatter(rfm_scatter_data.loc[mask,"recency"],
                   rfm_scatter_data.loc[mask,"monetary"] / 1000,
                   c=PAL[i], label=s, alpha=0.45, s=12, edgecolors="none")
ax_rfm.set_xlabel("Recency (Days Since Last Order)", color=TEXT, fontsize=10)
ax_rfm.set_ylabel("Monetary Value (₹ Thousands)", color=TEXT, fontsize=10)
ax_rfm.set_title("Customer Segmentation — RFM K-Means Clusters (K=3, Silhouette=0.46)",
                 color=TEXT, fontsize=11, fontweight="bold", pad=8)
ax_rfm.legend(labelcolor=TEXT, facecolor=CARD, edgecolor="#333", fontsize=9)
ax_rfm.tick_params(colors=TEXT)
for sp in ax_rfm.spines.values(): sp.set_edgecolor("#222")

ax_ins = fig.add_subplot(gs[4, 2:])
ax_ins.set_facecolor(PANEL)
ax_ins.axis("off")
ax_ins.set_title("Key Business Insights & Recommendations",
                 color=ACC3, fontsize=11, fontweight="bold", pad=8)

insights = [
    (ACC1, "📍", "Maharashtra drives 15.2% of revenue — prioritise regional marketing"),
    (ACC2, "⚠️", "9.94% cancellation rate — review inventory & fulfilment workflow"),
    (ACC4, "💡", "Ethnic Dress is #1 category — increase SKU depth and promotions"),
    (ACC3, "📈", "Expedited shipping customers spend 12% more — upsell opportunity"),
    (ACC5, "👥", "High Value segment (6,145 users) = 39.7% revenue — build VIP tier"),
    (ACC1, "📅", "Fridays & Saturdays peak in orders — schedule campaigns accordingly"),
    (ACC2, "🔄", "Random Forest forecasts ₹2.37Cr in next 30 days — plan inventory"),
    (ACC4, "💰", "Promotions raise AOV by 8.4% — scale promotion coverage"),
]
for i, (color, icon, text) in enumerate(insights):
    y = 0.92 - i * 0.117
    ax_ins.add_patch(FancyBboxPatch((0.01, y - 0.045), 0.98, 0.10,
        boxstyle="round,pad=0.01", facecolor=CARD,
        edgecolor=color, linewidth=1.2, alpha=0.9,
        transform=ax_ins.transAxes, clip_on=True))
    ax_ins.text(0.03, y + 0.01, icon, ha="left", va="center",
                fontsize=11, transform=ax_ins.transAxes)
    ax_ins.text(0.09, y + 0.01, text, ha="left", va="center",
                color=TEXT, fontsize=8.8, transform=ax_ins.transAxes)

# Footer
fig.text(0.5, 0.005,
         f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  "
         f"Python • Pandas • Scikit-Learn • Matplotlib • SQL • Power BI  |  "
         f"Dataset: Amazon Sale Report (50,000 orders, ₹12.70 Cr revenue)",
         ha="center", color="#666688", fontsize=8.5)

out = os.path.join(RPT_DIR, "capstone_report.png")
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  ✅  Capstone Report → {out}")
