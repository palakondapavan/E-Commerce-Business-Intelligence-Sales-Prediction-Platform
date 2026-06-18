"""
============================================================
 E-Commerce BI & Sales Prediction Platform
 Script 02 — Customer Segmentation
 RFM Analysis + K-Means Clustering
============================================================
"""

import os, warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# ── Paths ─────────────────────────────────────────────────
BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLN_CSV  = os.path.join(BASE, "Dataset", "Amazon_Sale_Report_Cleaned.csv")
RPT_DIR  = os.path.join(BASE, "Reports")
OUT_CSV  = os.path.join(BASE, "Dataset", "Customer_Segments.csv")
os.makedirs(RPT_DIR, exist_ok=True)

PALETTE  = ["#00d4ff","#ff6b6b","#ffd700","#51cf66","#cc5de8"]
BG       = "#0f1117"
PANEL    = "#1a1d2e"

print("\n" + "="*60)
print("  CUSTOMER SEGMENTATION — RFM + K-MEANS")
print("="*60)

# ═══════════════════════════════════════════════════════════
#  STEP 1 — Load Cleaned Data
# ═══════════════════════════════════════════════════════════
df = pd.read_csv(CLN_CSV, parse_dates=["date"], low_memory=False)

# Keep only completed / delivered orders for RFM
df_orders = df[df["status"].isin(["Delivered","Shipped","Shipped - Delivered To Buyer"])].copy()
print(f"\n  Orders available for segmentation : {len(df_orders):,}")

# Proxy for customer_id — use order_id prefix (first 15 chars simulate customer)
# In a real dataset, customer IDs would be available.
# Here we aggregate by order_id as a unique customer proxy.
df_orders["customer_id"] = df_orders["order_id"]

snapshot_date = df_orders["date"].max() + pd.Timedelta(days=1)
print(f"  Snapshot date (T+1) : {snapshot_date.date()}")

# ═══════════════════════════════════════════════════════════
#  STEP 2 — RFM Aggregation
# ═══════════════════════════════════════════════════════════
print("\n  Computing RFM features …")

rfm = df_orders.groupby("customer_id").agg(
    recency   = ("date",   lambda x: (snapshot_date - x.max()).days),
    frequency = ("order_id","count"),
    monetary  = ("amount",  "sum"),
).reset_index()

rfm["monetary"] = rfm["monetary"].round(2)

print(f"\n  RFM Table (sample):\n{rfm.head(5).to_string(index=False)}")
print(f"\n  RFM Summary Statistics:")
print(rfm[["recency","frequency","monetary"]].describe().round(2).to_string())

# ═══════════════════════════════════════════════════════════
#  STEP 3 — RFM Scoring (1–5)
# ═══════════════════════════════════════════════════════════
print("\n  Assigning RFM scores (1–5) …")

rfm["r_score"] = pd.qcut(rfm["recency"],   q=5, labels=[5,4,3,2,1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1,2,3,4,5]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"],  q=5, labels=[1,2,3,4,5]).astype(int)

rfm["rfm_score"]   = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
rfm["rfm_segment"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

print(f"  RFM Score range : {rfm['rfm_score'].min()} – {rfm['rfm_score'].max()}")

# ═══════════════════════════════════════════════════════════
#  STEP 4 — K-Means Clustering
# ═══════════════════════════════════════════════════════════
print("\n  Running K-Means clustering …")

features = ["recency","frequency","monetary"]
scaler   = StandardScaler()
X_scaled = scaler.fit_transform(rfm[features])

# ── Elbow method to find optimal K ────────────────────────
inertias    = []
sil_scores  = []
K_range     = range(2, 9)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X_scaled, km.labels_))

optimal_k = K_range[np.argmax(sil_scores)]
print(f"  Optimal K (max Silhouette) : {optimal_k}")
print(f"  Silhouette Score           : {max(sil_scores):.4f}")

# ── Final model ───────────────────────────────────────────
km_final  = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
rfm["cluster"] = km_final.fit_predict(X_scaled)

# ── Label clusters by RFM characteristics ─────────────────
cluster_summary = rfm.groupby("cluster")[features].mean().round(2)
cluster_summary["rfm_score_mean"] = rfm.groupby("cluster")["rfm_score"].mean().round(2)

print(f"\n  Cluster Centroids (original scale):\n{cluster_summary.to_string()}")

# Assign meaningful business labels
def label_cluster(row):
    r, f, m = row["recency"], row["frequency"], row["monetary"]
    # Sort centroid by monetary value to assign labels
    return row.name  # placeholder — overridden below

# Rank clusters: High Value = highest monetary, At Risk = highest recency
cluster_ranks = cluster_summary["monetary"].rank(ascending=False).astype(int)
labels_map = {}
sorted_clusters = cluster_summary["monetary"].sort_values(ascending=False).index.tolist()
label_names = [
    "High Value Customers",
    "Regular Customers",
    "Occasional Buyers",
    "At Risk Customers",
    "Lost Customers",
]
for i, c in enumerate(sorted_clusters):
    labels_map[c] = label_names[i] if i < len(label_names) else f"Segment {i+1}"

rfm["segment"] = rfm["cluster"].map(labels_map)
print(f"\n  Cluster → Segment mapping:")
for k, v in labels_map.items():
    print(f"    Cluster {k} → {v}")

# ═══════════════════════════════════════════════════════════
#  STEP 5 — Business Insights per Segment
# ═══════════════════════════════════════════════════════════
print("\n  Segment-Level Business Summary:")
seg_summary = rfm.groupby("segment").agg(
    customers        = ("customer_id", "count"),
    avg_recency_days = ("recency",    "mean"),
    avg_frequency    = ("frequency",  "mean"),
    avg_monetary     = ("monetary",   "mean"),
    total_revenue    = ("monetary",   "sum"),
).round(2).reset_index()
seg_summary["revenue_share_pct"] = (
    seg_summary["total_revenue"] / seg_summary["total_revenue"].sum() * 100
).round(2)
print(seg_summary.to_string(index=False))

# ═══════════════════════════════════════════════════════════
#  STEP 6 — Export Segments CSV
# ═══════════════════════════════════════════════════════════
rfm.to_csv(OUT_CSV, index=False)
print(f"\n  Segments CSV → {OUT_CSV}")

# ═══════════════════════════════════════════════════════════
#  STEP 7 — Visualisations
# ═══════════════════════════════════════════════════════════
print("\n  Generating segmentation visualisations …")

colors_seg = {seg: PALETTE[i % len(PALETTE)] for i, seg in enumerate(rfm["segment"].unique())}

fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor(BG)
plt.suptitle("Customer Segmentation — RFM & K-Means Analysis",
             color="white", fontsize=18, fontweight="bold", y=0.98)

# ── Plot 1: Elbow Curve ───────────────────────────────────
ax1 = fig.add_subplot(3, 3, 1)
ax1.set_facecolor(PANEL)
ax1.plot(list(K_range), inertias, color="#00d4ff", linewidth=2, marker="o", markersize=7)
ax1.axvline(optimal_k, color="#ff6b6b", linestyle="--", linewidth=1.5, label=f"Optimal K={optimal_k}")
ax1.set_title("Elbow Curve (Inertia)", color="white", fontweight="bold")
ax1.set_xlabel("Number of Clusters", color="white")
ax1.set_ylabel("Inertia", color="white")
ax1.tick_params(colors="white")
ax1.legend(labelcolor="white", facecolor=PANEL, edgecolor="#333")
for sp in ax1.spines.values(): sp.set_edgecolor("#333")

# ── Plot 2: Silhouette Scores ─────────────────────────────
ax2 = fig.add_subplot(3, 3, 2)
ax2.set_facecolor(PANEL)
bar_colors = ["#ffd700" if k == optimal_k else "#00d4ff" for k in K_range]
ax2.bar(list(K_range), sil_scores, color=bar_colors)
ax2.set_title("Silhouette Scores by K", color="white", fontweight="bold")
ax2.set_xlabel("Number of Clusters", color="white")
ax2.set_ylabel("Silhouette Score", color="white")
ax2.tick_params(colors="white")
for sp in ax2.spines.values(): sp.set_edgecolor("#333")

# ── Plot 3: Segment Distribution (Pie) ───────────────────
ax3 = fig.add_subplot(3, 3, 3)
ax3.set_facecolor(PANEL)
seg_counts = rfm["segment"].value_counts()
wedges, texts, autotexts = ax3.pie(
    seg_counts, labels=None, autopct="%1.1f%%",
    colors=PALETTE[:len(seg_counts)], startangle=140,
    pctdistance=0.82, wedgeprops=dict(linewidth=1.5, edgecolor=BG))
for t in autotexts: t.set_color("white"); t.set_fontsize(9)
ax3.legend(seg_counts.index, loc="lower left", fontsize=7,
           labelcolor="white", facecolor=PANEL, edgecolor="#333")
ax3.set_title("Customer Segment Distribution", color="white", fontweight="bold")

# ── Plot 4: RFM Recency by Segment ───────────────────────
ax4 = fig.add_subplot(3, 3, 4)
ax4.set_facecolor(PANEL)
seg_order = seg_summary.sort_values("avg_recency_days")["segment"].tolist()
recency_vals = [rfm[rfm["segment"] == s]["recency"].values for s in seg_order]
bp = ax4.boxplot(recency_vals, patch_artist=True,
                 medianprops=dict(color="white", linewidth=2))
for patch, color in zip(bp["boxes"], PALETTE):
    patch.set_facecolor(color); patch.set_alpha(0.8)
for element in ["whiskers","caps","fliers"]:
    for item in bp[element]: item.set_color("#aaa")
ax4.set_xticklabels([s.split()[0] for s in seg_order], color="white", fontsize=8)
ax4.set_title("Recency Distribution by Segment", color="white", fontweight="bold")
ax4.set_ylabel("Days Since Last Order", color="white")
ax4.tick_params(colors="white")
for sp in ax4.spines.values(): sp.set_edgecolor("#333")

# ── Plot 5: Revenue by Segment (Bar) ─────────────────────
ax5 = fig.add_subplot(3, 3, 5)
ax5.set_facecolor(PANEL)
seg_rev_sorted = seg_summary.sort_values("total_revenue", ascending=True)
bars = ax5.barh(seg_rev_sorted["segment"],
                seg_rev_sorted["total_revenue"] / 1e6,
                color=PALETTE[:len(seg_rev_sorted)])
ax5.set_title("Total Revenue by Segment (₹M)", color="white", fontweight="bold")
ax5.set_xlabel("Revenue (₹ Millions)", color="white")
ax5.tick_params(colors="white")
for sp in ax5.spines.values(): sp.set_edgecolor("#333")
for bar, val in zip(bars, seg_rev_sorted["total_revenue"] / 1e6):
    ax5.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
             f"₹{val:.1f}M", va="center", color="white", fontsize=8)

# ── Plot 6: Average Monetary by Segment ──────────────────
ax6 = fig.add_subplot(3, 3, 6)
ax6.set_facecolor(PANEL)
seg_mon = seg_summary.sort_values("avg_monetary", ascending=False)
bars = ax6.bar(range(len(seg_mon)), seg_mon["avg_monetary"],
               color=PALETTE[:len(seg_mon)])
ax6.set_xticks(range(len(seg_mon)))
ax6.set_xticklabels([s.split()[0] for s in seg_mon["segment"]],
                    color="white", rotation=15, fontsize=8)
ax6.set_title("Avg Monetary Value by Segment", color="white", fontweight="bold")
ax6.set_ylabel("Avg Spend (₹)", color="white")
ax6.tick_params(colors="white")
for sp in ax6.spines.values(): sp.set_edgecolor("#333")

# ── Plot 7: PCA 2D Cluster Visualisation ─────────────────
ax7 = fig.add_subplot(3, 3, (7, 9))
ax7.set_facecolor(PANEL)
pca    = PCA(n_components=2, random_state=42)
X_pca  = pca.fit_transform(X_scaled)
for i, seg in enumerate(rfm["segment"].unique()):
    mask = rfm["segment"] == seg
    ax7.scatter(X_pca[mask, 0], X_pca[mask, 1],
                c=PALETTE[i % len(PALETTE)], label=seg, alpha=0.5, s=8)
ax7.set_title("Customer Clusters — PCA 2D Projection", color="white", fontweight="bold")
ax7.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)", color="white")
ax7.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)", color="white")
ax7.tick_params(colors="white")
ax7.legend(loc="upper right", fontsize=8, labelcolor="white",
           facecolor=PANEL, edgecolor="#333")
for sp in ax7.spines.values(): sp.set_edgecolor("#333")

plt.tight_layout(rect=[0, 0, 1, 0.97])
viz_path = os.path.join(RPT_DIR, "customer_segmentation.png")
plt.savefig(viz_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  Segmentation PNG → {viz_path}")

# ═══════════════════════════════════════════════════════════
#  STEP 8 — RFM Heatmap
# ═══════════════════════════════════════════════════════════
fig2, axes = plt.subplots(1, 2, figsize=(16, 6))
fig2.patch.set_facecolor(BG)
plt.suptitle("RFM Score Distribution Heatmap",
             color="white", fontsize=16, fontweight="bold")

for ax, col, title in [(axes[0],"r_score","Recency Score"),
                       (axes[1],"m_score","Monetary Score")]:
    ax.set_facecolor(PANEL)
    pivot = rfm.pivot_table(index="f_score", columns=col,
                            values="monetary", aggfunc="mean")
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", annot=True, fmt=".0f",
                linewidths=0.5, linecolor="#0f1117",
                cbar_kws={"shrink": 0.8})
    ax.set_title(f"Avg Monetary  ×  Frequency vs {title}",
                 color="white", fontweight="bold")
    ax.set_xlabel(title, color="white")
    ax.set_ylabel("Frequency Score", color="white")
    ax.tick_params(colors="white")

plt.tight_layout()
heatmap_path = os.path.join(RPT_DIR, "rfm_heatmap.png")
plt.savefig(heatmap_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  RFM Heatmap PNG  → {heatmap_path}")

# ═══════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  ✅  CUSTOMER SEGMENTATION COMPLETE")
print(f"  Total customers analysed : {len(rfm):,}")
print(f"  Segments identified      : {rfm['segment'].nunique()}")
print(f"  Optimal K                : {optimal_k}")
print(f"  Silhouette Score         : {max(sil_scores):.4f}")
print("\n  Segment Breakdown:")
for _, row in seg_summary.iterrows():
    print(f"    {row['segment']:<28}: {int(row['customers']):>5} customers  "
          f"| Avg ₹{row['avg_monetary']:>8,.0f}  "
          f"| {row['revenue_share_pct']:.1f}% revenue")
print("="*60 + "\n")
