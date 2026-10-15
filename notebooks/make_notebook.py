"""
Convert rfm_segmentation.py → rfm_kmeans_segmentation.ipynb
Run: python make_notebook.py
"""
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

# ── Section definitions (marker, markdown title) ──────────────
SECTIONS = [
    ("# =====",        None),           # file header → markdown intro
    ("# ── 0.",        "## 📦 0. Imports"),
    ("# ── 1.",        "## 📂 1. Load Data"),
    ("# ── 2.",        "## 🧹 2. Data Cleaning"),
    ("# ── 3.",        "## 📊 3. RFM Calculation"),
    ("# ── 4.",        "## 📦 4. Outlier Analysis"),
    ("# ── 5.",        "## 🔢 5. Log-Transform & Normalisation"),
    ("# ── 6.",        "## 📈 6. Elbow Method"),
    ("# ── 7.",        "## 📏 7. Silhouette Score"),
    ("# ── 8.",        "## 🤖 8. Train K-Means"),
    ("# ── 9.",        "## 📋 9. Cluster Profiling & Labelling"),
    ("# ── 10.",       "## 🐍 10. Snake Plot"),
    ("# ── 11.",       "## 🌡️ 11. Heatmap"),
    ("# ── 12.",       "## 🔵 12. PCA 2D Scatter"),
    ("# ── 13.",       "## 🥧 13. Segment Distribution (Pie Chart)"),
    ("# ── 14.",       "## 💰 14. Revenue by Segment"),
    ("# ── 15.",       "## 📣 15. Marketing Recommendations"),
    ("# ── 16.",       "## 💾 16. Export Results"),
]

INTRO_MD = """# 🛍️ Customer Segmentation — RFM + K-Means Clustering

**Author:** Rihab Douhab  
**Dataset:** Online Retail II (UCI Machine Learning Repository)  
**Stack:** Python · Pandas · scikit-learn · Matplotlib · Seaborn

---

## 🎯 Objective

Segment customers into meaningful groups based on purchasing behaviour using the **RFM framework** and **K-Means clustering**.

| Metric | Description |
|--------|-------------|
| **Recency (R)** | Days since the customer's last purchase |
| **Frequency (F)** | Number of distinct orders placed |
| **Monetary (M)** | Total amount spent |

---

## 📋 Methodology

1. **Data Cleaning** — handle nulls, cancellations, negative values  
2. **RFM Calculation** — one row per customer  
3. **Normalisation** — log-transform + StandardScaler  
4. **Optimal k** — Elbow method + Silhouette score  
5. **K-Means Training** — fit & label clusters  
6. **Visualisation** — snake plot, heatmap, PCA scatter, pie chart  
7. **Recommendations** — per-segment marketing actions  
"""

with open("rfm_segmentation.py", encoding="utf-8") as f:
    raw = f.read()

lines = raw.splitlines()

# Split raw lines into blocks by section markers
blocks = []
current = []
for line in lines:
    is_section = any(line.strip().startswith(m) for m in [s[0] for s in SECTIONS])
    if is_section and current:
        blocks.append("\n".join(current))
        current = [line]
    else:
        current.append(line)
if current:
    blocks.append("\n".join(current))

nb = new_notebook()
nb.cells.append(new_markdown_cell(INTRO_MD))

section_titles = [s[1] for s in SECTIONS if s[1]]
title_idx = 0

for block in blocks:
    stripped = block.strip()
    if not stripped:
        continue
    # First block is file header → skip (already have INTRO_MD)
    if stripped.startswith("# ==="):
        continue
    # Section header comment line
    if stripped.startswith("# ── ") and title_idx < len(section_titles):
        nb.cells.append(new_markdown_cell(section_titles[title_idx]))
        title_idx += 1
        # Remove the comment line itself from code
        code_lines = block.splitlines()[1:]
        code = "\n".join(code_lines).strip()
        if code:
            nb.cells.append(new_code_cell(code))
    else:
        nb.cells.append(new_code_cell(stripped))

out_path = "rfm_kmeans_segmentation.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"✅ Created {out_path}  ({len(nb.cells)} cells)")
