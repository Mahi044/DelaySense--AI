"""
Step 2: Data Cleaning
=====================
Heavy cleaning pipeline: missing values, inconsistencies, duplicates, outliers.
Outputs cleaned CSVs to data/cleaned/
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")


def clean_foodhub(df):
    """Clean FoodHub Orders dataset."""
    print("\n--- Cleaning FoodHub Orders ---")
    original_rows = len(df)

    # 0. Rename columns for consistency
    if "cost_of_the_order" in df.columns:
        df = df.rename(columns={"cost_of_the_order": "cost"})
        print("  Renamed 'cost_of_the_order' → 'cost'")

    # 1. Handle missing values
    # Rating: 'Not given' or NaN → replace with NaN, then fill with median
    if df["rating"].dtype == object:
        df["rating"] = df["rating"].replace("Not given", np.nan)
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    missing_ratings = df["rating"].isna().sum()
    print(f"  Missing ratings: {missing_ratings} → filled with median")
    df["rating"] = df["rating"].fillna(df["rating"].median())

    # Fill any other missing values
    for col in df.columns:
        if df[col].isna().sum() > 0:
            if df[col].dtype in [np.float64, np.int64, float, int]:
                df[col] = df[col].fillna(df[col].median())
                print(f"  {col}: filled {df[col].isna().sum()} missing with median")
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
                print(f"  {col}: filled missing with mode")

    # 2. Fix inconsistent formats
    # Standardize cuisine_type
    df["cuisine_type"] = df["cuisine_type"].str.strip().str.title()
    # Standardize day_of_the_week
    df["day_of_the_week"] = df["day_of_the_week"].str.strip().str.title()

    # 3. Remove duplicates
    dups = df.duplicated().sum()
    if dups > 0:
        df = df.drop_duplicates()
        print(f"  Removed {dups} duplicate rows")

    # 4. Handle outliers - cap delivery_time and food_preparation_time at 99th percentile
    for col in ["delivery_time", "food_preparation_time"]:
        if col in df.columns:
            q99 = df[col].quantile(0.99)
            q01 = df[col].quantile(0.01)
            outliers = ((df[col] > q99) | (df[col] < q01)).sum()
            df[col] = df[col].clip(lower=q01, upper=q99)
            print(f"  {col}: capped {outliers} outliers at [{q01:.1f}, {q99:.1f}]")

    # 5. Ensure correct data types
    df["order_id"] = df["order_id"].astype(int)
    df["customer_id"] = df["customer_id"].astype(int)
    df["cost"] = df["cost"].astype(float)
    df["rating"] = df["rating"].astype(float).round(1)

    # 6. Create total_time column
    df["total_time"] = df["food_preparation_time"] + df["delivery_time"]

    print(f"  Rows: {original_rows} → {len(df)}")
    return df


def clean_delivery_logistics(df):
    """Clean Delivery Logistics dataset."""
    print("\n--- Cleaning Delivery Logistics ---")
    original_rows = len(df)

    # 1. Clean column names (remove spaces and special chars)
    df.columns = df.columns.str.strip()

    # 2. Handle Time_taken(min) - might have "min" text
    if "Time_taken(min)" in df.columns:
        df["Time_taken_min"] = (
            df["Time_taken(min)"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
        df["Time_taken_min"] = pd.to_numeric(df["Time_taken_min"], errors="coerce")
        df = df.drop(columns=["Time_taken(min)"])
    elif "Time_taken (min)" in df.columns:
        df["Time_taken_min"] = (
            df["Time_taken (min)"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
        df["Time_taken_min"] = pd.to_numeric(df["Time_taken_min"], errors="coerce")
        df = df.drop(columns=["Time_taken (min)"])

    # 3. Handle missing values
    for col in df.columns:
        na_count = df[col].isna().sum()
        if na_count > 0:
            if df[col].dtype in [np.float64, np.int64, float, int]:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
            print(f"  {col}: filled {na_count} missing values")

    # 4. Clean ratings
    if "Delivery_person_Ratings" in df.columns:
        df["Delivery_person_Ratings"] = pd.to_numeric(
            df["Delivery_person_Ratings"], errors="coerce"
        )
        df["Delivery_person_Ratings"] = df["Delivery_person_Ratings"].fillna(
            df["Delivery_person_Ratings"].median()
        )

    # 5. Clean age
    if "Delivery_person_Age" in df.columns:
        df["Delivery_person_Age"] = pd.to_numeric(
            df["Delivery_person_Age"], errors="coerce"
        )
        df["Delivery_person_Age"] = df["Delivery_person_Age"].fillna(
            df["Delivery_person_Age"].median()
        )
        # Cap unrealistic ages
        df["Delivery_person_Age"] = df["Delivery_person_Age"].clip(18, 65)

    # 6. Validate coordinates
    for lat_col in ["Restaurant_latitude", "Delivery_location_latitude"]:
        if lat_col in df.columns:
            df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
            invalid = ((df[lat_col].abs() > 90) | df[lat_col].isna()).sum()
            if invalid > 0:
                df[lat_col] = df[lat_col].fillna(df[lat_col].median())
                print(f"  {lat_col}: fixed {invalid} invalid values")

    for lon_col in ["Restaurant_longitude", "Delivery_location_longitude"]:
        if lon_col in df.columns:
            df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
            invalid = ((df[lon_col].abs() > 180) | df[lon_col].isna()).sum()
            if invalid > 0:
                df[lon_col] = df[lon_col].fillna(df[lon_col].median())
                print(f"  {lon_col}: fixed {invalid} invalid values")

    # 7. Standardize categorical columns
    if "Type_of_order" in df.columns:
        df["Type_of_order"] = df["Type_of_order"].astype(str).str.strip().str.title()
    if "Type_of_vehicle" in df.columns:
        df["Type_of_vehicle"] = df["Type_of_vehicle"].astype(str).str.strip().str.title()

    # 8. Remove duplicates
    dups = df.duplicated().sum()
    if dups > 0:
        df = df.drop_duplicates()
        print(f"  Removed {dups} duplicate rows")

    # 9. Outlier handling for Time_taken_min
    if "Time_taken_min" in df.columns:
        q99 = df["Time_taken_min"].quantile(0.99)
        q01 = df["Time_taken_min"].quantile(0.01)
        outliers = ((df["Time_taken_min"] > q99) | (df["Time_taken_min"] < q01)).sum()
        df["Time_taken_min"] = df["Time_taken_min"].clip(lower=q01, upper=q99)
        print(f"  Time_taken_min: capped {outliers} outliers at [{q01:.1f}, {q99:.1f}]")

    print(f"  Rows: {original_rows} → {len(df)}")
    return df


def clean_customer_satisfaction(df):
    """Clean Customer Satisfaction dataset."""
    print("\n--- Cleaning Customer Satisfaction ---")
    original_rows = len(df)

    # 1. Handle missing values
    for col in df.columns:
        na_count = df[col].isna().sum()
        if na_count > 0:
            if df[col].dtype in [np.float64, np.int64, float, int]:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
            print(f"  {col}: filled {na_count} missing values")

    # 2. Standardize categories
    for col in ["Gender", "PreferredCuisine", "TimeOfVisit", "DiningOccasion", "MealType"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # 3. Ensure boolean columns are int
    for col in ["OnlineReservation", "DeliveryOrder", "LoyaltyProgramMember", "HighSatisfaction"]:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # 4. Validate rating columns (should be 1-5)
    for col in ["ServiceRating", "FoodRating", "AmbianceRating"]:
        if col in df.columns:
            df[col] = df[col].clip(1, 5)

    # 5. Cap WaitTime outliers
    if "WaitTime" in df.columns:
        q99 = df["WaitTime"].quantile(0.99)
        outliers = (df["WaitTime"] > q99).sum()
        df["WaitTime"] = df["WaitTime"].clip(upper=q99)
        print(f"  WaitTime: capped {outliers} outliers at {q99:.1f}")

    # 6. Remove duplicates
    dups = df.duplicated().sum()
    if dups > 0:
        df = df.drop_duplicates()
        print(f"  Removed {dups} duplicate rows")

    print(f"  Rows: {original_rows} → {len(df)}")
    return df


def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    print("=" * 60)
    print("  STEP 2: DATA CLEANING PIPELINE")
    print("=" * 60)

    # Clean FoodHub
    df_fh = pd.read_csv(os.path.join(RAW_DIR, "foodhub_orders.csv"))
    df_fh = clean_foodhub(df_fh)
    df_fh.to_csv(os.path.join(CLEAN_DIR, "foodhub_orders_clean.csv"), index=False)
    print(f"  ✓ Saved: foodhub_orders_clean.csv")

    # Clean Delivery Logistics
    df_dl = pd.read_csv(os.path.join(RAW_DIR, "delivery_logistics.csv"))
    df_dl = clean_delivery_logistics(df_dl)
    df_dl.to_csv(os.path.join(CLEAN_DIR, "delivery_logistics_clean.csv"), index=False)
    print(f"  ✓ Saved: delivery_logistics_clean.csv")

    # Clean Customer Satisfaction
    df_cs = pd.read_csv(os.path.join(RAW_DIR, "customer_satisfaction.csv"))
    df_cs = clean_customer_satisfaction(df_cs)
    df_cs.to_csv(os.path.join(CLEAN_DIR, "customer_satisfaction_clean.csv"), index=False)
    print(f"  ✓ Saved: customer_satisfaction_clean.csv")

    print(f"\n{'='*60}")
    print("  CLEANING COMPLETE — all files in data/cleaned/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
