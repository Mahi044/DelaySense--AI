"""
Step 0: Dataset Download
========================
Downloads all 3 datasets from GitHub into data/raw/
"""

import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

DATASETS = {
    "foodhub_orders.csv": "https://raw.githubusercontent.com/codekalimi/Foodhub-data-analysis/master/foodhub_order.csv",
    "delivery_logistics.csv": "https://raw.githubusercontent.com/MisterAare/delivery_time_prediction/main/delivery_time_data.csv",
    "customer_satisfaction.csv": "https://raw.githubusercontent.com/abhilash-antony/Customer-Satisfaction-Statistical-Analysis/main/restaurant_customer_satisfaction.csv",
}


def download_datasets():
    os.makedirs(RAW_DIR, exist_ok=True)
    results = {}

    for filename, url in DATASETS.items():
        filepath = os.path.join(RAW_DIR, filename)
        print(f"\n{'='*60}")
        print(f"Downloading: {filename}")
        print(f"Source:      {url}")

        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)

            size_kb = os.path.getsize(filepath) / 1024
            print(f"✓ Saved to:  {filepath}")
            print(f"  Size:      {size_kb:.1f} KB")
            results[filename] = True
        except Exception as e:
            print(f"✗ FAILED:    {e}")
            results[filename] = False

    print(f"\n{'='*60}")
    print("DOWNLOAD SUMMARY")
    print(f"{'='*60}")
    for fname, success in results.items():
        status = "✓ OK" if success else "✗ FAILED"
        print(f"  {status}  {fname}")

    return results


if __name__ == "__main__":
    download_datasets()
