"""
Download Online Retail II dataset from UCI.
Run: python download_data.py
"""
import urllib.request
import os

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ZIP_PATH = "../data/online_retail_II.zip"
OUT_DIR  = "../data"

os.makedirs(OUT_DIR, exist_ok=True)

print("⬇️  Downloading Online Retail II dataset from UCI…")
print("   (file is ~45 MB, please wait)")

try:
    urllib.request.urlretrieve(URL, ZIP_PATH)
    print("✅  Download complete.")

    import zipfile
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(OUT_DIR)
    print("📦  Extracted. Files:")
    for f in os.listdir(OUT_DIR):
        print(f"   {f}")
    os.remove(ZIP_PATH)
except Exception as e:
    print(f"❌  Error: {e}")
    print()
    print("👉  Manual download:")
    print("    1. Go to https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci")
    print("    2. Download 'online_retail_II.xlsx'")
    print("    3. Place it in the data/ folder")
