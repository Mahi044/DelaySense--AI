"""
Generate comprehensive JSON data for the dashboard.
Exports per-row data so client-side filters can re-aggregate.
"""

import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "data", "modeled")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
DASH_DIR = os.path.join(BASE_DIR, "dashboard")


def main():
    os.makedirs(DASH_DIR, exist_ok=True)
    df = pd.read_csv(os.path.join(MODEL_DIR, "fact_orders.csv"))
    dim_rest = pd.read_csv(os.path.join(MODEL_DIR, "dim_restaurant.csv"))
    df = df.merge(dim_rest, on="restaurant_id", how="left")



    # Export per-row data for client-side filtering
    row_cols = [
        "order_id", "cost", "rating", "food_preparation_time", "delivery_time",
        "total_time", "delivery_delay", "order_hour", "time_of_day", "peak_hour_flag",
        "traffic_level", "delay_category", "day_of_the_week", "distance_km",
        "cuisine_type", "restaurant_name", "latitude", "longitude"
    ]
    if "sentiment" in df.columns:
        row_cols += ["sentiment", "sentiment_score"]

    # Keep only existing columns
    row_cols = [c for c in row_cols if c in df.columns]
    rows = df[row_cols].to_dict(orient="records")

    # Clean NaN values for JSON
    for row in rows:
        for k, v in row.items():
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                row[k] = None

    # Metadata
    data = {
        "rows": rows,
        "cuisines": sorted(df["cuisine_type"].dropna().unique().tolist()) if "cuisine_type" in df.columns else [],
        "days": sorted(df["day_of_the_week"].dropna().unique().tolist()),
        "restaurants": sorted(df["restaurant_name"].dropna().unique().tolist()) if "restaurant_name" in df.columns else [],
    }

    output_path = os.path.join(DASH_DIR, "data.js")
    with open(output_path, "w") as f:
        f.write(f"const RAW_DATA = {json.dumps(data)};")

    print(f"  > Dashboard data exported to {output_path}")
    print(f"  > Rows: {len(rows)}, Cuisines: {len(data['cuisines'])}, Restaurants: {len(data['restaurants'])}")


if __name__ == "__main__":
    main()
