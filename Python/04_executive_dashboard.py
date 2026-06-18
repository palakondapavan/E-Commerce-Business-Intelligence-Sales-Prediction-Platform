"""
============================================================
 E-Commerce BI & Sales Prediction Platform
 Script 04 — Executive Analytics Dashboard
 Full-featured business intelligence visuals
============================================================
"""

import os, warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns

BG    = "#0d0d1a"
PANEL = "#13132b"
CARD  = "#1c1c3a"
TEXT  = "#e8e8f0"
ACC1  = "#00c8ff"
ACC2  = "#ff4d6d"
ACC3  = "#ffd166"
ACC4  = "#06d6a0"
ACC5  = "#c77dff"
PAL   = [ACC1, ACC2, ACC3, ACC4, ACC5,
         "#ff9f1c","#a8dadc","#f72585","#4cc9f0","#b5e48c"]

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLN_CSV = os.path.join(BASE, "Dataset", "Amazon_Sale_Report_Cleaned.csv")
RPT_DIR = os.path.join(BASE, "Reports")
os.makedirs(RPT_DIR, exist_ok=True)

print("\n  Loading cleaned dataset …")
df = pd.read_csv(CLN_CSV, parse_dates=["date"], low_memory=False)

# ── KPIs ──────────────────────────────────────────────────
total_revenue  = df["amount"].sum()
total_orders   = df["order_id"].nunique()
total_qty      = df["qty"].sum()
avg_order_val  = df["amount"].mean()
total_cats     = df["category"].nunique()

delivered_pct  = (df["status"].str.lower().str.contains("deliver").sum() / len(df)) * 100
cancel_pct     = (df["status"].str.lower().str.contains("cancel").sum()  / len(df)) * 100

print(f"  Total Revenue : ₹{total_revenue:,.0f}")
print(f"  Total Orders  : {total_orders:,}")

# ── Aggregations ───────────────────────────────────────────
monthly = (df.groupby(df["date"].dt.to_period("M"))
             .agg(revenue=("amount","sum"), orders=("order_id","count"))
             .reset_index())
monthly["date"]    = monthly["date"].astype(str)
monthly["revenue"] = monthly["revenue"].round(2)

cat_rev = (df.groupby("category")["amount"].sum()
             .sort_values(ascending=False).reset_index())
cat_rev.columns = ["category","revenue"]

state_rev = (df.groupby("ship_state")["amount"].sum()
               .sort_values(ascending=False)
               .head(10).reset_index())
state_rev.columns = ["state","revenue"]

status_counts = df["status"].value_counts()

daily = (df.groupby("date")
           .agg(revenue=("amount","sum"), orders=("order_id","count"))
           .reset_index())

size_qty  = df.groupby("size")["qty"].sum().sort_values(ascending=False).head(8)
channel   = df.groupby("sales_channel")["amount"].sum().reset_index()
channel.columns = ["channel","revenue"]

weekly = (df.assign(week=df["date"].dt.to_period("W"))
            .groupby("week")["amount"].sum().reset_index())
weekly["week"] = weekly["week"].astype(str)

cat_monthly = (df.groupby([df["date"].dt.to_period("M"),"category"])["amount"]
                 .sum().reset_index())
cat_monthly["date"] = cat_monthly["date"].astype(str)

# ═══════════════════════════════════════════════════════════
#  DASHBOARD 1 — Executive Overview (Page 1)
# ═══════════════════════════════════════════════════════════
fig = plt.figure(figsize=(24, 18))
fig.patch.set_facecolor(BG)
gs  = gridspec.GridSpec(4, 4, figure=fig, hspace=0.50, wspace=0.35,
                        top=0.93, bottom=0.04, left=0.05, right=0.97)

plt.suptitle("E-COMMERCE BUSINESS INTELLIGENCE — EXECUTIVE DASHBOARD",
             color=TEXT, fontsize=19, fontweight="bold", y=0.975,
             fontfamily="monospace")

# ── KPI Cards (Row 0) ─────────────────────────────────────
kpis = [
    ("TOTAL REVENUE",         f"₹{total_revenue/1e7:.2f}Cr",  ACC1),
    ("TOTAL ORDERS",          f"{total_orders:,}",             ACC2),
    ("TOTAL QTY SOLD",        f"{total_qty:,}",                ACC3),
    ("AVG ORDER VALUE",       f"₹{avg_order_val:,.0f}",        ACC4),
]
for col, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, col])
    ax.set_facecolor(CARD)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis("off")
    for sp in ax.spines.values(): sp.set_edgecolor(color); sp.set_linewidth(2)
    ax.add_patch(mpatches.FancyBboxPatch((0,0),1,1,
                 boxstyle="round,pad=0.02", facecolor=CARD,
                 edgecolor=color, linewidth=2, transform=ax.transAxes, clip_on=False))
    ax.text(0.5, 0.72, value, ha="center", va="center",
            fontsize=24, fontweight="bold", color=color,
            transform=ax.transAxes)
    ax.text(0.5, 0.28, label, ha="center", va="center",
            fontsize=9, color="#aaaacc", fontweight="bold",
            fontfamily="monospace", transform=ax.transAxes)
    ax.add_patch(mpatches.Rectangle((0, 0), 1, 0.04,
                 transform=ax.transAxes, color=color, clip_on=True))

# ── Monthly Revenue Trend (Row 1, Full Width) ─────────────
ax_trend = fig.add_subplot(gs[1, :])
ax_trend.set_facecolor(PANEL)
x_pos = range(len(monthly))
ax_trend.bar(x_pos, monthly["revenue"] / 1e6, color=ACC1, alpha=0.55, width=0.7, label="Revenue")
ax2t = ax_trend.twinx()
ax2t.plot(x_pos, monthly["orders"], color=ACC2, linewidth=2.5,
          marker="D", markersize=6, label="Orders")
ax_trend.set_xticks(list(x_pos))
ax_trend.set_xticklabels(monthly["date"], color=TEXT, rotation=45, fontsize=8)
ax_trend.set_ylabel("Revenue (₹ Millions)", color=ACC1)
ax2t.set_ylabel("Orders", color=ACC2)
ax_trend.tick_params(colors=TEXT, axis="y")
ax2t.tick_params(colors=ACC2, axis="y")
ax_trend.set_title("Monthly Revenue & Orders Trend", color=TEXT,
                   fontsize=13, fontweight="bold", pad=8)
ax_trend.set_facecolor(PANEL)
for sp in ax_trend.spines.values(): sp.set_edgecolor("#333")
lines1, labels1 = ax_trend.get_legend_handles_labels()
lines2, labels2 = ax2t.get_legend_handles_labels()
ax_trend.legend(lines1+lines2, labels1+labels2,
                labelcolor=TEXT, facecolor=CARD, edgecolor="#444", fontsize=9,
                loc="upper left")

# ── Top Categories Bar (Row 2, Col 0-1) ───────────────────
ax_cat = fig.add_subplot(gs[2, :2])
ax_cat.set_facecolor(PANEL)
top_cats = cat_rev.head(8)
bars = ax_cat.barh(top_cats["category"][::-1], top_cats["revenue"][::-1] / 1e6,
                   color=PAL[:len(top_cats)])
ax_cat.set_xlabel("Revenue (₹ Millions)", color=TEXT)
ax_cat.set_title("Revenue by Category", color=TEXT, fontsize=12, fontweight="bold")
ax_cat.tick_params(colors=TEXT)
for sp in ax_cat.spines.values(): sp.set_edgecolor("#333")
for bar, val in zip(bars, top_cats["revenue"][::-1] / 1e6):
    ax_cat.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"₹{val:.1f}M", va="center", color=TEXT, fontsize=8)

# ── Top States (Row 2, Col 2-3) ───────────────────────────
ax_state = fig.add_subplot(gs[2, 2:])
ax_state.set_facecolor(PANEL)
colors_state = plt.cm.plasma(np.linspace(0.2, 0.8, len(state_rev)))
bars = ax_state.bar(range(len(state_rev)), state_rev["revenue"] / 1e6, color=colors_state)
ax_state.set_xticks(range(len(state_rev)))
ax_state.set_xticklabels(state_rev["state"], color=TEXT, rotation=45, ha="right", fontsize=8)
ax_state.set_ylabel("Revenue (₹ Millions)", color=TEXT)
ax_state.set_title("Top 10 States by Revenue", color=TEXT, fontsize=12, fontweight="bold")
ax_state.tick_params(colors=TEXT, axis="y")
for sp in ax_state.spines.values(): sp.set_edgecolor("#333")

# ── Order Status Donut (Row 3, Col 0) ─────────────────────
ax_status = fig.add_subplot(gs[3, 0])
ax_status.set_facecolor(PANEL)
wedges, texts, autotexts = ax_status.pie(
    status_counts, labels=None, autopct="%1.1f%%",
    colors=PAL[:len(status_counts)], startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2))
for t in autotexts: t.set_color(TEXT); t.set_fontsize(8)
ax_status.legend(status_counts.index, loc="lower center", fontsize=7,
                 labelcolor=TEXT, facecolor=CARD, edgecolor="#444",
                 bbox_to_anchor=(0.5, -0.18), ncol=2)
ax_status.set_title("Order Status Distribution", color=TEXT, fontsize=11, fontweight="bold")

# ── Size Distribution (Row 3, Col 1) ──────────────────────
ax_size = fig.add_subplot(gs[3, 1])
ax_size.set_facecolor(PANEL)
ax_size.bar(size_qty.index, size_qty.values, color=PAL[:len(size_qty)])
ax_size.set_xlabel("Size", color=TEXT)
ax_size.set_ylabel("Qty Sold", color=TEXT)
ax_size.set_title("Top Sizes by Qty Sold", color=TEXT, fontsize=11, fontweight="bold")
ax_size.tick_params(colors=TEXT)
for sp in ax_size.spines.values(): sp.set_edgecolor("#333")

# ── Sales Channel (Row 3, Col 2) ──────────────────────────
ax_ch = fig.add_subplot(gs[3, 2])
ax_ch.set_facecolor(PANEL)
ax_ch.bar(channel["channel"], channel["revenue"] / 1e6, color=[ACC1, ACC3])
ax_ch.set_ylabel("Revenue (₹ Millions)", color=TEXT)
ax_ch.set_title("Sales Channel Revenue", color=TEXT, fontsize=11, fontweight="bold")
ax_ch.tick_params(colors=TEXT)
for sp in ax_ch.spines.values(): sp.set_edgecolor("#333")

# ── Fulfilment Split (Row 3, Col 3) ───────────────────────
ax_ful = fig.add_subplot(gs[3, 3])
ax_ful.set_facecolor(PANEL)
ful = df.groupby("fulfilment")["amount"].sum()
ax_ful.pie(ful, labels=ful.index, autopct="%1.1f%%",
           colors=[ACC4, ACC5], startangle=90,
           wedgeprops=dict(edgecolor=BG, linewidth=2))
ax_ful.set_title("Fulfilment Split", color=TEXT, fontsize=11, fontweight="bold")
for t in ax_ful.texts: t.set_color(TEXT); t.set_fontsize(9)

# ── Save Page 1 ───────────────────────────────────────────
p1_path = os.path.join(RPT_DIR, "executive_dashboard_p1.png")
plt.savefig(p1_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  Executive Dashboard P1 → {p1_path}")

# ═══════════════════════════════════════════════════════════
#  DASHBOARD 2 — Deep-Dive Analytics (Page 2)
# ═══════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(24, 16))
fig2.patch.set_facecolor(BG)
gs2  = gridspec.GridSpec(3, 3, figure=fig2, hspace=0.45, wspace=0.35,
                         top=0.93, bottom=0.05, left=0.05, right=0.97)

plt.suptitle("E-COMMERCE ANALYTICS — DEEP DIVE REPORT",
             color=TEXT, fontsize=19, fontweight="bold", y=0.975,
             fontfamily="monospace")

# ── Daily Revenue + Rolling Average ──────────────────────
ax21 = fig2.add_subplot(gs2[0, :])
ax21.set_facecolor(PANEL)
ax21.plot(daily["date"], daily["revenue"] / 1e3, color=ACC1, alpha=0.4,
          linewidth=1, label="Daily Revenue")
roll7 = daily["revenue"].rolling(7).mean() / 1e3
ax21.plot(daily["date"], roll7, color=ACC3, linewidth=2.5,
          label="7-Day Rolling Avg")
roll14 = daily["revenue"].rolling(14).mean() / 1e3
ax21.plot(daily["date"], roll14, color=ACC2, linewidth=2,
          linestyle="--", label="14-Day Rolling Avg")
ax21.fill_between(daily["date"], daily["revenue"] / 1e3, alpha=0.08, color=ACC1)
ax21.set_title("Daily Revenue with Rolling Averages", color=TEXT,
               fontsize=13, fontweight="bold")
ax21.set_ylabel("Revenue (₹ Thousands)", color=TEXT)
ax21.legend(labelcolor=TEXT, facecolor=CARD, edgecolor="#444", fontsize=9)
ax21.tick_params(colors=TEXT)
for sp in ax21.spines.values(): sp.set_edgecolor("#333")

# ── Category × Month Heatmap ──────────────────────────────
ax22 = fig2.add_subplot(gs2[1, :2])
ax22.set_facecolor(PANEL)
pivot = cat_monthly.pivot_table(index="category", columns="date",
                                 values="amount", aggfunc="sum", fill_value=0)
sns.heatmap(pivot / 1e6, ax=ax22, cmap="YlOrRd", annot=True, fmt=".1f",
            linewidths=0.5, linecolor=BG,
            cbar_kws={"label": "Revenue (₹M)", "shrink": 0.8})
ax22.set_title("Category Revenue Heatmap — Monthly (₹ Millions)",
               color=TEXT, fontsize=12, fontweight="bold")
ax22.set_xlabel("Month", color=TEXT)
ax22.set_ylabel("Category", color=TEXT)
ax22.tick_params(colors=TEXT, axis="x", rotation=45)
ax22.tick_params(colors=TEXT, axis="y", rotation=0)
ax22.yaxis.label.set_color(TEXT)

# ── Revenue by Service Level ──────────────────────────────
ax23 = fig2.add_subplot(gs2[1, 2])
ax23.set_facecolor(PANEL)
svc = df.groupby("ship_service_level").agg(
    revenue=("amount","sum"), orders=("order_id","count")).reset_index()
ax23.bar(svc["ship_service_level"], svc["revenue"] / 1e6, color=[ACC1, ACC4])
ax23.set_title("Revenue by Service Level", color=TEXT, fontsize=11, fontweight="bold")
ax23.set_ylabel("Revenue (₹ Millions)", color=TEXT)
ax23.tick_params(colors=TEXT)
for sp in ax23.spines.values(): sp.set_edgecolor("#333")

# ── B2B vs B2C Trend ─────────────────────────────────────
ax24 = fig2.add_subplot(gs2[2, 0])
ax24.set_facecolor(PANEL)
b2b_mon = (df.assign(month=df["date"].dt.to_period("M"))
             .groupby(["month","b2b"])["amount"].sum()
             .reset_index())
b2b_mon["month"] = b2b_mon["month"].astype(str)
for seg, color in [("Yes", ACC2), ("No", ACC1)]:
    sub = b2b_mon[b2b_mon["b2b"] == seg]
    ax24.plot(sub["month"], sub["amount"] / 1e6, color=color,
              linewidth=2, marker="o", markersize=5, label=f"B2B={seg}")
ax24.set_title("B2B vs B2C Monthly Revenue", color=TEXT, fontsize=11, fontweight="bold")
ax24.set_ylabel("Revenue (₹M)", color=TEXT)
ax24.legend(labelcolor=TEXT, facecolor=CARD, edgecolor="#444", fontsize=8)
ax24.tick_params(colors=TEXT, axis="x", rotation=45)
for sp in ax24.spines.values(): sp.set_edgecolor("#333")

# ── Promotion Impact ─────────────────────────────────────
ax25 = fig2.add_subplot(gs2[2, 1])
ax25.set_facecolor(PANEL)
promo = df.copy()
promo["promo_segment"] = np.where(
    promo["promotion_ids"] == "No Promotion", "No Promo", "With Promo")
promo_grp = promo.groupby("promo_segment").agg(
    revenue=("amount","sum"), orders=("order_id","count")).reset_index()
colors_promo = [ACC4, ACC5]
ax25.bar(promo_grp["promo_segment"], promo_grp["revenue"] / 1e6,
         color=colors_promo, edgecolor=BG, linewidth=1.5)
ax25.set_title("Promotion Impact on Revenue", color=TEXT, fontsize=11, fontweight="bold")
ax25.set_ylabel("Revenue (₹M)", color=TEXT)
ax25.tick_params(colors=TEXT)
for sp in ax25.spines.values(): sp.set_edgecolor("#333")

# ── Weekly Revenue Heatmap ────────────────────────────────
ax26 = fig2.add_subplot(gs2[2, 2])
ax26.set_facecolor(PANEL)
dow_month = (df.assign(dow=df["date"].dt.day_name(),
                       mth=df["date"].dt.strftime("%b"))
               .groupby(["mth","dow"])["amount"].mean()
               .unstack(fill_value=0))
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow_month = dow_month.reindex(columns=[d for d in day_order if d in dow_month.columns])
sns.heatmap(dow_month / 1e3, ax=ax26, cmap="Blues",
            linewidths=0.3, linecolor=BG, annot=True, fmt=".0f",
            cbar_kws={"shrink": 0.8})
ax26.set_title("Avg Revenue (₹K) — Month × Day", color=TEXT, fontsize=11, fontweight="bold")
ax26.tick_params(colors=TEXT, axis="x", rotation=45)
ax26.tick_params(colors=TEXT, axis="y", rotation=0)

p2_path = os.path.join(RPT_DIR, "executive_dashboard_p2.png")
plt.savefig(p2_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  Executive Dashboard P2 → {p2_path}")

print("\n  ✅  All dashboard visualisations saved to Reports/")
