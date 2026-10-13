# 🛍️ Customer Segmentation — RFM + K-Means

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange?logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> **Segment e-commerce customers into actionable groups using RFM analysis and K-Means clustering.**

---

## 📌 Problem Statement

Not all customers are equal. A retailer needs to know **who are the VIPs**, **who is at risk of churning**, and **who has already left** — so they can apply the right marketing strategy to each group.

This project solves that by:
1. Computing an **RFM score** for every customer
2. Clustering customers automatically with **K-Means**
3. Producing **marketing recommendations** per segment

---

## 📂 Dataset

| Property | Value |
|----------|-------|
| Source | [UCI Online Retail II](https://archive.ics.uci.edu/ml/datasets/Online+Retail+II) |
| Period | 2009 – 2011 |
| Transactions | ~1,000,000 rows |
| Customers | ~5,900 unique |
| Country | United Kingdom (mainly) |

**Key columns:** `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country`

---

## 🔬 Methodology

```
Raw Data → Cleaning → RFM Calculation → Log-Transform → StandardScaler
    → Elbow Method + Silhouette → K-Means (k=4) → Profiling → Recommendations
```

### RFM Metrics

| Metric | Formula |
|--------|---------|
| Recency | Days between last purchase and snapshot date |
| Frequency | Number of distinct invoices |
| Monetary | Sum of (Quantity × Price) |

### Cleaning Steps
- Dropped rows with missing `Customer ID`
- Removed cancelled orders (Invoice starts with `'C'`)
- Removed negative or zero `Quantity` / `Price`
- Removed duplicates

### Normalisation
- **Log1p transform** on Frequency & Monetary (right-skewed)
- **StandardScaler** to zero-mean, unit-variance

---

## 📊 Results

| Segment | Customers | Avg Recency | Avg Frequency | Avg Monetary |
|---------|-----------|-------------|---------------|--------------|
| 🏆 Champions | ~18% | Low | High | High |
| 💛 Loyal Customers | ~28% | Medium | Medium | Medium |
| ⚠️ At Risk | ~25% | High | Low-Med | Medium |
| 💤 Lost / Inactive | ~29% | Very High | Very Low | Low |

### Key Charts

| Chart | Description |
|-------|-------------|
| `01_rfm_boxplots.png` | Distribution of raw RFM values |
| `02_elbow.png` | Inertia vs k — elbow at k=4 |
| `03_silhouette.png` | Silhouette score confirms k=4 |
| `04_snake_plot.png` | Normalised RFM profile per segment |
| `05_heatmap.png` | RFM heatmap by segment |
| `06_pca_scatter.png` | 2D PCA projection of clusters |
| `07_pie_chart.png` | Customer count per segment |
| `08_revenue_bar.png` | Total revenue per segment |

---

## 📣 Marketing Recommendations

| Segment | Actions |
|---------|---------|
| 🏆 **Champions** | VIP rewards, early access, ask for referrals |
| 💛 **Loyal** | Upsell, cross-sell, personalised emails |
| ⚠️ **At Risk** | Win-back campaign, discount, re-engagement sequence |
| 💤 **Lost** | Last-chance offer, churn survey |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/douhabrihab6-lang/customer-segmentation-rfm.git
cd customer-segmentation-rfm
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the dataset
- Go to: https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
- Download `online_retail_II.xlsx` → place in `data/`

### 4. Run the notebook
```bash
cd notebooks
jupyter notebook rfm_kmeans_segmentation.ipynb
```

---

## 🗂️ Project Structure

```
customer-segmentation-rfm/
├── data/
│   ├── online_retail_II.xlsx      # raw dataset (not tracked by git)
│   └── rfm_clustered.csv          # output with cluster labels
├── notebooks/
│   ├── rfm_kmeans_segmentation.ipynb   # main notebook
│   └── rfm_segmentation.py             # source script
├── assets/
│   └── screenshots/               # saved chart PNGs
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.13 | Core language |
| Pandas | Data wrangling & RFM |
| NumPy | Numerical ops |
| scikit-learn | StandardScaler, KMeans, silhouette |
| Matplotlib / Seaborn | Visualisations |
| Plotly | Interactive charts (bonus) |
| Jupyter Notebook | Analysis environment |

---

## 💼 CV Line

> **Customer Segmentation using RFM + K-Means (Python, scikit-learn)**  
> Analysed 1M+ transactions, identified 4 customer segments (Champions, Loyal, At Risk, Lost), produced targeted marketing recommendations — reduced churn potential by identifying 25% at-risk customers.

---

## 👩‍💻 Author

**Douha Brihab** — [GitHub](https://github.com/douhabrihab6-lang)
