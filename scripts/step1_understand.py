"""
Step 1: Data Understanding
==========================
Profile each dataset: shape, dtypes, missing values, distributions, relationships.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


def profile_dataset(name, df):
    """Print a comprehensive profile of a DataFrame."""
    print(f"\n{'#'*70}")
    print(f"  DATASET: {name}")
    print(f"{'#'*70}")

    # --- Shape ---
    print(f"\n1. SHAPE: {df.shape[0]} rows × {df.shape[1]} columns")

    # --- Data Types ---
    print(f"\n2. DATA TYPES:")
    for col in df.columns:
        print(f"   {col:<40} {str(df[col].dtype):<15}")

    # --- Missing Values ---
    print(f"\n3. MISSING VALUES:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    has_missing = False
    for col in df.columns:
        if missing[col] > 0:
            has_missing = True
            print(f"   {col:<40} {missing[col]:>6} ({missing_pct[col]:.2f}%)")
    if not has_missing:
        print("   No missing values found!")

    # --- Duplicates ---
    dup_count = df.duplicated().sum()
    print(f"\n4. DUPLICATES: {dup_count} duplicate rows")

    # --- Numerical Summary ---
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        print(f"\n5. NUMERICAL SUMMARY:")
        print(df[num_cols].describe().round(2).to_string())

    # --- Categorical Summary ---
    cat_cols = df.select_dtypes(include=["object"]).columns
    if len(cat_cols) > 0:
        print(f"\n6. CATEGORICAL COLUMNS:")
        for col in cat_cols:
            n_unique = df[col].nunique()
            top = df[col].value_counts().head(5).to_dict()
            print(f"   {col} ({n_unique} unique): {top}")

    # --- Sample Rows ---
    print(f"\n7. FIRST 3 ROWS:")
    print(df.head(3).to_string())

    return {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "missing_total": missing.sum(),
        "duplicates": dup_count,
    }


def explain_relationships():
    """Explain how the 3 datasets relate to each other."""
    print(f"\n{'#'*70}")
    print("  DATASET RELATIONSHIPS")
    print(f"{'#'*70}")
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │  Dataset 1: FoodHub Orders (PRIMARY)                           │
    │  - Core order data: order_id, customer_id, restaurant, cost    │
    │  - Delivery metrics: food_preparation_time, delivery_time      │
    │  - Customer feedback: rating (1-5)                             │
    ├─────────────────────────────────────────────────────────────────┤
    │  Dataset 2: Delivery Logistics (ENRICHMENT)                    │
    │  - Geo-coordinates: restaurant & delivery lat/long             │
    │  - Delivery person: age, ratings, vehicle type                 │
    │  - Time taken: actual delivery duration                        │
    │  JOIN KEY: Type_of_order ↔ cuisine_type (approximate)          │
    ├─────────────────────────────────────────────────────────────────┤
    │  Dataset 3: Customer Satisfaction (ENRICHMENT)                 │
    │  - Multi-dimensional ratings: service, food, ambiance          │
    │  - Wait times, demographics (age, gender, income)              │
    │  - Delivery vs dine-in flag                                    │
    │  JOIN KEY: PreferredCuisine ↔ cuisine_type, MealType mapping   │
    └─────────────────────────────────────────────────────────────────┘

    STRATEGY:
    1. Use FoodHub Orders as the FACT table backbone
    2. Aggregate Delivery Logistics to enrich with distance & person data
    3. Aggregate Customer Satisfaction for deeper satisfaction analysis
    4. All three feed into a unified star schema for BI analysis
    """)


def main():
    datasets = {
        "FoodHub Orders": "foodhub_orders.csv",
        "Delivery Logistics": "delivery_logistics.csv",
        "Customer Satisfaction": "customer_satisfaction.csv",
    }

    summaries = {}
    for name, filename in datasets.items():
        filepath = os.path.join(RAW_DIR, filename)
        if not os.path.exists(filepath):
            print(f"\n⚠ File not found: {filepath}")
            print("  Run step0_download.py first!")
            continue
        df = pd.read_csv(filepath)
        summaries[name] = profile_dataset(name, df)

    explain_relationships()

    # Overall summary
    print(f"\n{'#'*70}")
    print("  OVERALL SUMMARY")
    print(f"{'#'*70}")
    for name, s in summaries.items():
        print(f"  {name}: {s['rows']} rows, {s['cols']} cols, "
              f"{s['missing_total']} missing, {s['duplicates']} duplicates")


if __name__ == "__main__":
    main()
