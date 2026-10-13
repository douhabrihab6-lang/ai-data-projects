# =============================================================
# CUSTOMER SEGMENTATION — RFM + K-Means Clustering
# Dataset  : Online Retail II (UCI / Kaggle)
# Author   : Douha Brihab
# Date     : 2026
# =============================================================

# ── 0. IMPORTS ───────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import os

warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.family"] = "DejaVu Sans"
PALETTE = ["#6C63FF", "#F7931E", "#2EC4B6", "#E71D36", "#011627"]

print("✅ Imports OK")

# ── 1. LOAD DATA ─────────────────────────────────────────────
DATA_PATH = "../data/online_retail_II.xlsx"

print("📂 Loading dataset (this may take ~30 seconds)…")
df = pd.read_excel(DATA_PATH, sheet_name="Year 2010-2011", engine="openpyxl")
print(f"Shape: {df.shape}")
print(df.head())
print(df.dtypes)
print(df.isnull().sum())

# ── 2. CLEAN DATA ─────────────────────────────────────────────
print("\n🧹 Cleaning data…")

# Drop rows without CustomerID
df.dropna(subset=["Customer ID"], inplace=True)
df["Customer ID"] = df["Customer ID"].astype(int)

# Remove cancelled orders (InvoiceNo starts with 'C')
df = df[~df["Invoice"].astype(str).str.startswith("C")]

# Remove negative / zero Quantity and Price
df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

# Drop duplicates
df.drop_duplicates(inplace=True)

# Compute line total
df["TotalPrice"] = df["Quantity"] * df["Price"]

print(f"Clean shape: {df.shape}")
print(df.describe())

# ── 3. RFM CALCULATION ───────────────────────────────────────
print("\n📊 Computing RFM…")

SNAPSHOT_DATE = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("Customer ID").agg(
    Recency   = ("InvoiceDate",  lambda x: (SNAPSHOT_DATE - x.max()).days),
    Frequency = ("Invoice",      "nunique"),
    Monetary  = ("TotalPrice",   "sum")
).reset_index()

print(rfm.describe())
print(rfm.head(10))

# ── 4. OUTLIER ANALYSIS ──────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, col, c in zip(axes, ["Recency", "Frequency", "Monetary"], PALETTE):
    ax.boxplot(rfm[col], patch_artist=True,
               boxprops=dict(facecolor=c, alpha=0.6))
    ax.set_title(col)
plt.suptitle("RFM — Boxplots (raw)", fontsize=14, fontweight="bold")
plt.tight_layout()
os.makedirs("../assets/screenshots", exist_ok=True)
plt.savefig("../assets/screenshots/01_rfm_boxplots.png")
plt.show()
print("✅ Saved 01_rfm_boxplots.png")

# ── 5. LOG TRANSFORM + NORMALISATION ────────────────────────
print("\n🔢 Log-transform & StandardScaler…")

rfm_log = rfm[["Recency", "Frequency", "Monetary"]].copy()
rfm_log["Frequency"] = np.log1p(rfm_log["Frequency"])
rfm_log["Monetary"]  = np.log1p(rfm_log["Monetary"])

scaler   = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log)

# ── 6. ELBOW METHOD ──────────────────────────────────────────
print("📈 Elbow method…")
inertias = []
K_RANGE  = range(2, 12)

for k in K_RANGE:
    km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
    km.fit(rfm_scaled)
    inertias.append(km.inertia_)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(list(K_RANGE), inertias, "o-", color=PALETTE[0], linewidth=2.5)
ax.set_xlabel("Number of Clusters (k)")
ax.set_ylabel("Inertia (SSE)")
ax.set_title("Elbow Method — Optimal k", fontweight="bold")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("../assets/screenshots/02_elbow.png")
plt.show()
print("✅ Saved 02_elbow.png")

# ── 7. SILHOUETTE SCORE ──────────────────────────────────────
print("📏 Silhouette scores…")
sil_scores = []

for k in K_RANGE:
    km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
    labels = km.fit_predict(rfm_scaled)
    sil_scores.append(silhouette_score(rfm_scaled, labels))

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(list(K_RANGE), sil_scores, color=PALETTE[1], alpha=0.8, edgecolor="white")
ax.set_xlabel("Number of Clusters (k)")
ax.set_ylabel("Silhouette Score")
ax.set_title("Silhouette Score per k", fontweight="bold")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("../assets/screenshots/03_silhouette.png")
plt.show()

BEST_K = list(K_RANGE)[sil_scores.index(max(sil_scores))]
print(f"✅ Best k by silhouette = {BEST_K}")

# Override if elbow is visually at 4
CHOSEN_K = 4
print(f"🎯 Chosen k = {CHOSEN_K}")

# ── 8. TRAIN K-MEANS ─────────────────────────────────────────
km_final = KMeans(n_clusters=CHOSEN_K, init="k-means++", n_init=20, random_state=42)
rfm["Cluster"] = km_final.fit_predict(rfm_scaled)
print(rfm["Cluster"].value_counts())

# ── 9. CLUSTER PROFILING ─────────────────────────────────────
cluster_summary = rfm.groupby("Cluster")[["Recency","Frequency","Monetary"]].mean().round(1)
print("\n📋 Cluster Means:\n", cluster_summary)

# Assign segment labels based on profile
#  Sort clusters: Champions = high F, high M, low R
cluster_summary["Score"] = (
    -cluster_summary["Recency"] +
     cluster_summary["Frequency"] * 10 +
     cluster_summary["Monetary"] / 100
)
rank = cluster_summary["Score"].rank(ascending=False).astype(int)
label_map = {
    rank[rank==1].index[0]: "🏆 Champions",
    rank[rank==2].index[0]: "💛 Loyal Customers",
    rank[rank==3].index[0]: "⚠️  At Risk",
    rank[rank==4].index[0]: "💤 Lost / Inactive",
}
rfm["Segment"] = rfm["Cluster"].map(label_map)
print("\n🏷️  Segment distribution:\n", rfm["Segment"].value_counts())

# ── 10. SNAKE PLOT ───────────────────────────────────────────
rfm_norm = rfm.copy()
for col in ["Recency", "Frequency", "Monetary"]:
    rfm_norm[col] = (rfm[col] - rfm[col].min()) / (rfm[col].max() - rfm[col].min())

snake = rfm_norm.groupby("Segment")[["Recency","Frequency","Monetary"]].mean()

fig, ax = plt.subplots(figsize=(9, 5))
for i, (seg, row) in enumerate(snake.iterrows()):
    ax.plot(["Recency","Frequency","Monetary"], row.values,
            "o-", linewidth=2.5, color=PALETTE[i], label=seg, markersize=8)
ax.set_title("Snake Plot — Normalised RFM per Segment", fontweight="bold")
ax.set_ylabel("Normalised Value  (0–1)")
ax.legend(loc="upper right")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("../assets/screenshots/04_snake_plot.png")
plt.show()
print("✅ Saved 04_snake_plot.png")

# ── 11. HEATMAP ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(snake, annot=True, fmt=".2f", cmap="YlOrRd",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Normalised Value"})
ax.set_title("RFM Heatmap by Segment", fontweight="bold")
plt.tight_layout()
plt.savefig("../assets/screenshots/05_heatmap.png")
plt.show()
print("✅ Saved 05_heatmap.png")

# ── 12. PCA 2D SCATTER ───────────────────────────────────────
pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(rfm_scaled)
rfm["PC1"] = coords[:, 0]
rfm["PC2"] = coords[:, 1]

fig, ax = plt.subplots(figsize=(9, 6))
for i, seg in enumerate(rfm["Segment"].unique()):
    sub = rfm[rfm["Segment"] == seg]
    ax.scatter(sub["PC1"], sub["PC2"], label=seg,
               color=PALETTE[i], alpha=0.5, s=18, edgecolors="none")
ax.set_title("Customer Clusters — PCA 2D", fontweight="bold")
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
ax.legend()
ax.grid(alpha=0.2)
plt.tight_layout()
plt.savefig("../assets/screenshots/06_pca_scatter.png")
plt.show()
print("✅ Saved 06_pca_scatter.png")

# ── 13. SEGMENT PIE CHART ────────────────────────────────────
counts = rfm["Segment"].value_counts()
fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    counts, labels=counts.index, autopct="%1.1f%%",
    colors=PALETTE[:len(counts)], startangle=140,
    wedgeprops=dict(edgecolor="white", linewidth=2)
)
for t in autotexts:
    t.set_fontsize(12)
ax.set_title("Customer Segment Distribution", fontweight="bold", fontsize=14)
plt.tight_layout()
plt.savefig("../assets/screenshots/07_pie_chart.png")
plt.show()
print("✅ Saved 07_pie_chart.png")

# ── 14. MONETARY BAR CHART ───────────────────────────────────
rev = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(rev.index, rev.values, color=PALETTE[:len(rev)],
              edgecolor="white", linewidth=1.5)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
ax.set_title("Total Revenue by Segment", fontweight="bold")
ax.set_ylabel("Total Monetary Value (£)")
ax.grid(axis="y", alpha=0.3)
for bar, val in zip(bars, rev.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + rev.max()*0.01,
            f"£{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig("../assets/screenshots/08_revenue_bar.png")
plt.show()
print("✅ Saved 08_revenue_bar.png")

# ── 15. MARKETING RECOMMENDATIONS ───────────────────────────
recommendations = {
    "🏆 Champions": [
        "Reward with VIP loyalty program & exclusive offers",
        "Ask for reviews / referrals",
        "Early access to new products"
    ],
    "💛 Loyal Customers": [
        "Upsell & cross-sell complementary products",
        "Send personalised thank-you emails",
        "Offer membership / subscription deals"
    ],
    "⚠️  At Risk": [
        "Send win-back campaign: 'We miss you!' + discount",
        "Personalised product recommendations",
        "SMS/email re-engagement sequence"
    ],
    "💤 Lost / Inactive": [
        "Last-chance reactivation offer (big discount)",
        "Survey: why did they stop?",
        "Consider removing from active mailing list"
    ],
}

print("\n" + "="*55)
print("  📣  MARKETING RECOMMENDATIONS BY SEGMENT")
print("="*55)
for seg, actions in recommendations.items():
    print(f"\n{seg}")
    for a in actions:
        print(f"   → {a}")

# ── 16. EXPORT ───────────────────────────────────────────────
rfm.to_csv("../data/rfm_clustered.csv", index=False)
print("\n✅ rfm_clustered.csv exported.")
print("\n🎉 Done! All charts saved to assets/screenshots/")
