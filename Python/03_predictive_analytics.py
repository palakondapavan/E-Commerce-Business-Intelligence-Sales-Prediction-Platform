"""
============================================================
 E-Commerce BI & Sales Prediction Platform
 Script 03 — Predictive Analytics
 Linear Regression + Random Forest Sales Forecasting
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
import seaborn as sns

from sklearn.model_selection   import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.linear_model      import LinearRegression, Ridge
from sklearn.ensemble          import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing     import StandardScaler
from sklearn.metrics           import (mean_absolute_error, mean_squared_error,
                                       r2_score, mean_absolute_percentage_error)
from sklearn.pipeline          import Pipeline

BG    = "#0f1117"
PANEL = "#1a1d2e"
PAL   = ["#00d4ff","#ff6b6b","#ffd700","#51cf66","#cc5de8"]

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLN_CSV = os.path.join(BASE, "Dataset", "Amazon_Sale_Report_Cleaned.csv")
RPT_DIR = os.path.join(BASE, "Reports")
OUT_CSV = os.path.join(BASE, "Dataset", "Sales_Forecast.csv")
os.makedirs(RPT_DIR, exist_ok=True)

print("\n" + "="*60)
print("  PREDICTIVE ANALYTICS — SALES FORECASTING")
print("="*60)

# ═══════════════════════════════════════════════════════════
#  STEP 1 — Load & Aggregate to Daily/Weekly Time Series
# ═══════════════════════════════════════════════════════════
df = pd.read_csv(CLN_CSV, parse_dates=["date"], low_memory=False)
df = df[df["status"].isin(["Delivered","Shipped","Shipped - Delivered To Buyer"])].copy()

print(f"\n  Loaded {len(df):,} completed orders")

# Daily aggregation
daily = (df.groupby("date")
           .agg(daily_orders  = ("order_id","count"),
                daily_revenue = ("amount",  "sum"),
                daily_qty     = ("qty",     "sum"))
           .reset_index()
           .sort_values("date"))

daily["daily_revenue"] = daily["daily_revenue"].round(2)
print(f"  Daily time series : {len(daily)} days")
print(f"  Revenue range     : ₹{daily['daily_revenue'].min():,.0f} – ₹{daily['daily_revenue'].max():,.0f}")

# ═══════════════════════════════════════════════════════════
#  STEP 2 — Feature Engineering (Lag / Rolling / Calendar)
# ═══════════════════════════════════════════════════════════
print("\n  Engineering time-series features …")

ts = daily.copy().set_index("date").asfreq("D").fillna(0).reset_index()

# Calendar features
ts["day_of_week"]  = ts["date"].dt.dayofweek
ts["day_of_month"] = ts["date"].dt.day
ts["week_number"]  = ts["date"].dt.isocalendar().week.astype(int)
ts["month"]        = ts["date"].dt.month
ts["quarter"]      = ts["date"].dt.quarter
ts["is_weekend"]   = ts["day_of_week"].isin([5, 6]).astype(int)

# Lag features
for lag in [1, 2, 3, 7, 14]:
    ts[f"revenue_lag_{lag}"]  = ts["daily_revenue"].shift(lag)
    ts[f"orders_lag_{lag}"]   = ts["daily_orders"].shift(lag)

# Rolling averages
for win in [3, 7, 14]:
    ts[f"revenue_roll_{win}"] = ts["daily_revenue"].shift(1).rolling(win).mean()

# Time index
ts["t"] = range(len(ts))

# Drop rows with NaN from lagging
ts.dropna(inplace=True)
print(f"  Feature-engineered rows : {len(ts)}")

# ═══════════════════════════════════════════════════════════
#  STEP 3 — Train / Test Split (80/20 temporal)
# ═══════════════════════════════════════════════════════════
TARGET   = "daily_revenue"
FEATURES = [c for c in ts.columns if c not in ["date", TARGET, "daily_orders","daily_qty"]]

X = ts[FEATURES].values
y = ts[TARGET].values

split = int(len(ts) * 0.80)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]
dates_test       = ts["date"].iloc[split:].values

print(f"\n  Train size : {len(X_train)} days")
print(f"  Test size  : {len(X_test)} days")

scaler  = StandardScaler()
Xs_train = scaler.fit_transform(X_train)
Xs_test  = scaler.transform(X_test)

# ═══════════════════════════════════════════════════════════
#  STEP 4 — Model Training & Evaluation
# ═══════════════════════════════════════════════════════════
def evaluate(name, y_true, y_pred):
    mae   = mean_absolute_error(y_true, y_pred)
    rmse  = np.sqrt(mean_squared_error(y_true, y_pred))
    r2    = r2_score(y_true, y_pred)
    mape  = mean_absolute_percentage_error(y_true, y_pred) * 100
    return dict(Model=name, MAE=round(mae,2), RMSE=round(rmse,2),
                R2=round(r2,4), MAPE_pct=round(mape,2))

results    = []
all_preds  = {}

# ── Model 1: Linear Regression ────────────────────────────
print("\n  Training Linear Regression …")
lr = LinearRegression()
lr.fit(Xs_train, y_train)
pred_lr = lr.predict(Xs_test)
res_lr  = evaluate("Linear Regression", y_test, pred_lr)
results.append(res_lr)
all_preds["Linear Regression"] = pred_lr
print(f"    R²={res_lr['R2']}  MAE=₹{res_lr['MAE']:,.0f}  RMSE=₹{res_lr['RMSE']:,.0f}  MAPE={res_lr['MAPE_pct']}%")

# ── Model 2: Ridge Regression ─────────────────────────────
print("  Training Ridge Regression …")
ridge = Ridge(alpha=10)
ridge.fit(Xs_train, y_train)
pred_ridge = ridge.predict(Xs_test)
res_ridge  = evaluate("Ridge Regression", y_test, pred_ridge)
results.append(res_ridge)
all_preds["Ridge Regression"] = pred_ridge
print(f"    R²={res_ridge['R2']}  MAE=₹{res_ridge['MAE']:,.0f}  RMSE=₹{res_ridge['RMSE']:,.0f}  MAPE={res_ridge['MAPE_pct']}%")

# ── Model 3: Random Forest ────────────────────────────────
print("  Training Random Forest …")
rf = RandomForestRegressor(n_estimators=150, max_depth=10,
                            min_samples_leaf=3, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)                     # RF handles unscaled features
pred_rf  = rf.predict(X_test)
res_rf   = evaluate("Random Forest", y_test, pred_rf)
results.append(res_rf)
all_preds["Random Forest"] = pred_rf
print(f"    R²={res_rf['R2']}  MAE=₹{res_rf['MAE']:,.0f}  RMSE=₹{res_rf['RMSE']:,.0f}  MAPE={res_rf['MAPE_pct']}%")

# ── Model 4: Gradient Boosting ────────────────────────────
print("  Training Gradient Boosting …")
gb = GradientBoostingRegressor(n_estimators=150, learning_rate=0.08,
                                max_depth=5, random_state=42)
gb.fit(X_train, y_train)
pred_gb  = gb.predict(X_test)
res_gb   = evaluate("Gradient Boosting", y_test, pred_gb)
results.append(res_gb)
all_preds["Gradient Boosting"] = pred_gb
print(f"    R²={res_gb['R2']}  MAE=₹{res_gb['MAE']:,.0f}  RMSE=₹{res_gb['RMSE']:,.0f}  MAPE={res_gb['MAPE_pct']}%")

# ── Results Table ─────────────────────────────────────────
results_df = pd.DataFrame(results).sort_values("R2", ascending=False)
print(f"\n  ── Model Comparison ──────────────────────────────────")
print(results_df.to_string(index=False))

best_model_name = results_df.iloc[0]["Model"]
best_pred       = all_preds[best_model_name]
print(f"\n  Best Model : {best_model_name}")

# ═══════════════════════════════════════════════════════════
#  STEP 5 — 30-Day Forecast (using best model)
# ═══════════════════════════════════════════════════════════
print("\n  Generating 30-day rolling forecast …")

# Build future feature rows iteratively
last_known = ts.copy()
future_rows = []
last_revenue = list(last_known["daily_revenue"].values)
last_orders  = list(last_known["daily_orders"].values)

last_date = ts["date"].max()
for i in range(1, 31):
    fdate = last_date + pd.Timedelta(days=i)
    row = {
        "date"         : fdate,
        "day_of_week"  : fdate.dayofweek,
        "day_of_month" : fdate.day,
        "week_number"  : fdate.isocalendar().week,
        "month"        : fdate.month,
        "quarter"      : fdate.quarter,
        "is_weekend"   : int(fdate.dayofweek in [5,6]),
        "t"            : last_known["t"].max() + i,
    }
    for lag in [1,2,3,7,14]:
        row[f"revenue_lag_{lag}"] = last_revenue[-lag] if len(last_revenue) >= lag else 0
        row[f"orders_lag_{lag}"]  = last_orders[-lag]  if len(last_orders)  >= lag else 0
    for win in [3,7,14]:
        row[f"revenue_roll_{win}"] = np.mean(last_revenue[-win:]) if len(last_revenue) >= win else 0

    feat_vec = np.array([[row[f] for f in FEATURES]])
    if best_model_name in ("Linear Regression","Ridge Regression"):
        feat_scaled = scaler.transform(feat_vec)
        model_obj   = lr if best_model_name == "Linear Regression" else ridge
        pred_val    = max(0, float(model_obj.predict(feat_scaled)[0]))
    else:
        model_obj = rf if best_model_name == "Random Forest" else gb
        pred_val  = max(0, float(model_obj.predict(feat_vec)[0]))

    row["predicted_revenue"] = round(pred_val, 2)
    future_rows.append(row)
    last_revenue.append(pred_val)
    last_orders.append(int(pred_val // last_known["daily_revenue"].mean() or 1))

future_df = pd.DataFrame(future_rows)[["date","predicted_revenue"]]
print(f"  30-day forecast revenue : ₹{future_df['predicted_revenue'].sum():,.2f}")
future_df.to_csv(OUT_CSV, index=False)
print(f"  Forecast CSV → {OUT_CSV}")

# Feature importances (Random Forest)
feat_imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
top_features = feat_imp.head(10)

# ═══════════════════════════════════════════════════════════
#  STEP 6 — Visualisations
# ═══════════════════════════════════════════════════════════
print("\n  Generating prediction visualisations …")

fig = plt.figure(figsize=(22, 18))
fig.patch.set_facecolor(BG)
plt.suptitle("Sales Prediction & Forecasting Dashboard",
             color="white", fontsize=18, fontweight="bold", y=0.99)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

# ── Plot 1: Actual vs Predicted (Best Model) ──────────────
ax1 = fig.add_subplot(gs[0, :])
ax1.set_facecolor(PANEL)
ax1.plot(dates_test, y_test,      color="#00d4ff", linewidth=1.5,
         label="Actual Revenue",   alpha=0.9)
ax1.plot(dates_test, best_pred,   color="#ff6b6b", linewidth=1.5,
         linestyle="--", label=f"Predicted ({best_model_name})")
ax1.fill_between(dates_test, y_test, best_pred, alpha=0.15, color="#ffd700")
ax1.set_title(f"Actual vs Predicted Daily Revenue — {best_model_name}",
              color="white", fontweight="bold")
ax1.set_ylabel("Revenue (₹)", color="white")
ax1.legend(labelcolor="white", facecolor=PANEL, edgecolor="#333")
ax1.tick_params(colors="white")
for sp in ax1.spines.values(): sp.set_edgecolor("#333")

# ── Plot 2: 30-Day Forecast ───────────────────────────────
ax2 = fig.add_subplot(gs[1, :2])
ax2.set_facecolor(PANEL)
hist_tail = ts.tail(30)
ax2.plot(hist_tail["date"], hist_tail["daily_revenue"],
         color="#00d4ff", linewidth=2, label="Historical (Last 30d)")
ax2.plot(future_df["date"], future_df["predicted_revenue"],
         color="#ffd700", linewidth=2.5, linestyle="--", marker="o",
         markersize=5, label="30-Day Forecast")
ax2.fill_between(future_df["date"],
                 future_df["predicted_revenue"] * 0.85,
                 future_df["predicted_revenue"] * 1.15,
                 alpha=0.2, color="#ffd700", label="±15% CI")
ax2.axvline(ts["date"].max(), color="#ff6b6b", linestyle=":", linewidth=1.5,
            label="Forecast Start")
ax2.set_title("30-Day Revenue Forecast", color="white", fontweight="bold")
ax2.set_ylabel("Revenue (₹)", color="white")
ax2.legend(labelcolor="white", facecolor=PANEL, edgecolor="#333", fontsize=8)
ax2.tick_params(colors="white", axis="x", rotation=30)
for sp in ax2.spines.values(): sp.set_edgecolor("#333")

# ── Plot 3: Model Comparison Radar ────────────────────────
ax3 = fig.add_subplot(gs[1, 2])
ax3.set_facecolor(PANEL)
x_pos = range(len(results_df))
bars  = ax3.bar(x_pos, results_df["R2"], color=PAL[:len(results_df)])
ax3.set_xticks(list(x_pos))
ax3.set_xticklabels([n.split()[0] for n in results_df["Model"]],
                    color="white", fontsize=8, rotation=15)
ax3.set_title("Model R² Comparison", color="white", fontweight="bold")
ax3.set_ylabel("R² Score", color="white")
ax3.set_ylim(0, 1)
ax3.tick_params(colors="white")
for sp in ax3.spines.values(): sp.set_edgecolor("#333")
for bar, val in zip(bars, results_df["R2"]):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f"{val:.3f}", ha="center", color="white", fontsize=9)

# ── Plot 4: Feature Importance ────────────────────────────
ax4 = fig.add_subplot(gs[2, :2])
ax4.set_facecolor(PANEL)
bars = ax4.barh(top_features.index[::-1], top_features.values[::-1],
                color=PAL[0])
ax4.set_title("Top 10 Feature Importances (Random Forest)",
              color="white", fontweight="bold")
ax4.set_xlabel("Importance", color="white")
ax4.tick_params(colors="white")
for sp in ax4.spines.values(): sp.set_edgecolor("#333")

# ── Plot 5: Metrics Table ─────────────────────────────────
ax5 = fig.add_subplot(gs[2, 2])
ax5.set_facecolor(PANEL)
ax5.axis("off")
tbl_data = results_df[["Model","R2","MAPE_pct"]].values.tolist()
table = ax5.table(
    cellText   = [[row[0].replace(" ","\n"), f"{row[1]:.4f}", f"{row[2]:.1f}%"]
                  for row in tbl_data],
    colLabels  = ["Model","R²","MAPE"],
    cellLoc    = "center",
    loc        = "center",
    bbox       = [0, 0, 1, 1],
)
table.auto_set_font_size(False)
table.set_fontsize(9)
for (r, c), cell in table.get_celld().items():
    cell.set_facecolor("#252840" if r == 0 else PANEL)
    cell.set_edgecolor("#444")
    cell.set_text_props(color="white")
ax5.set_title("Model Metrics", color="white", fontweight="bold", pad=10)

viz_path = os.path.join(RPT_DIR, "sales_prediction.png")
plt.savefig(viz_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  Prediction PNG → {viz_path}")

# ═══════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  ✅  PREDICTIVE ANALYTICS COMPLETE")
print(f"\n  Best Model     : {best_model_name}")
best = results_df.iloc[0]
print(f"  R² Score       : {best['R2']}")
print(f"  MAE            : ₹{best['MAE']:,.0f}")
print(f"  RMSE           : ₹{best['RMSE']:,.0f}")
print(f"  MAPE           : {best['MAPE_pct']}%")
print(f"\n  30-Day Forecast: ₹{future_df['predicted_revenue'].sum():,.2f} total revenue")
print(f"  Avg Daily Rev  : ₹{future_df['predicted_revenue'].mean():,.2f}")
print("="*60 + "\n")
