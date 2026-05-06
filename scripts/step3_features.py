"""
Step 3: Feature Engineering
============================
Create analytical features: delivery_delay, distance_km, time_of_day,
peak_hour_flag, traffic_level, delay_category.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two (lat, lon) points."""
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def engineer_foodhub(df):
    """Engineer features for FoodHub Orders."""
    print("\n--- Feature Engineering: FoodHub Orders ---")

    # 1. delivery_delay = total_time - expected (use median as "expected")
    expected_delivery = df["delivery_time"].median()
    expected_prep = df["food_preparation_time"].median()
    expected_total = expected_delivery + expected_prep
    df["expected_total_time"] = expected_total
    df["delivery_delay"] = df["total_time"] - expected_total
    print(f"  delivery_delay: expected_total = {expected_total:.1f} min")

    # 2. time_of_day (simulate from day_of_the_week since we don't have timestamps)
    np.random.seed(42)
    hours = np.random.choice(range(8, 24), size=len(df))
    df["order_hour"] = hours

    def get_time_of_day(h):
        if 6 <= h < 12:
            return "Morning"
        elif 12 <= h < 17:
            return "Afternoon"
        elif 17 <= h < 21:
            return "Evening"
        else:
            return "Night"

    df["time_of_day"] = pd.Series(hours).apply(get_time_of_day).values

    # 3. peak_hour_flag (lunch 11-14, dinner 18-21)
    df["peak_hour_flag"] = ((df["order_hour"].between(11, 14)) |
                             (df["order_hour"].between(18, 21))).astype(int)
    peak_pct = df["peak_hour_flag"].mean() * 100
    print(f"  peak_hour_flag: {peak_pct:.1f}% orders in peak hours")

    # 4. traffic_level (derive from delivery_time relative to median)
    median_del = df["delivery_time"].median()
    conditions = [
        df["delivery_time"] <= median_del * 0.7,
        df["delivery_time"] <= median_del * 1.0,
        df["delivery_time"] <= median_del * 1.3,
        df["delivery_time"] > median_del * 1.3,
    ]
    choices = ["Low", "Medium", "High", "Jam"]
    df["traffic_level"] = np.select(conditions, choices, default="Medium")
    print(f"  traffic_level distribution: {df['traffic_level'].value_counts().to_dict()}")

    # 5. delay_category
    conditions_delay = [
        df["delivery_delay"] <= -5,
        df["delivery_delay"].between(-5, 5),
        df["delivery_delay"].between(5, 15),
        df["delivery_delay"] > 15,
    ]
    choices_delay = ["Early", "On Time", "Slightly Delayed", "Heavily Delayed"]
    df["delay_category"] = np.select(conditions_delay, choices_delay, default="On Time")
    print(f"  delay_category distribution: {df['delay_category'].value_counts().to_dict()}")

    # 6. cost_bucket
    df["cost_bucket"] = pd.cut(df["cost"], bins=[0, 10, 20, 30, 50, 100],
                                labels=["$0-10", "$10-20", "$20-30", "$30-50", "$50+"])

    return df


def engineer_delivery_logistics(df):
    """Engineer features for Delivery Logistics."""
    print("\n--- Feature Engineering: Delivery Logistics ---")

    # 1. distance_km using haversine formula
    if all(c in df.columns for c in ["Restaurant_latitude", "Restaurant_longitude",
                                      "Delivery_location_latitude", "Delivery_location_longitude"]):
        df["distance_km"] = haversine(
            df["Restaurant_latitude"], df["Restaurant_longitude"],
            df["Delivery_location_latitude"], df["Delivery_location_longitude"],
        )
        # Clean extreme distances (data noise can create absurd values)
        df["distance_km"] = df["distance_km"].clip(0.1, 50)
        print(f"  distance_km: mean={df['distance_km'].mean():.2f}, "
              f"max={df['distance_km'].max():.2f}")

    # 2. delivery_delay = actual - expected (median per distance bucket)
    if "Time_taken_min" in df.columns and "distance_km" in df.columns:
        df["distance_bucket"] = pd.cut(df["distance_km"], bins=5)
        expected = df.groupby("distance_bucket")["Time_taken_min"].transform("median")
        df["delivery_delay"] = df["Time_taken_min"] - expected
        df = df.drop(columns=["distance_bucket"])
        print(f"  delivery_delay: mean={df['delivery_delay'].mean():.2f} min")

    # 3. time_of_day  (simulate)
    np.random.seed(123)
    hours = np.random.choice(range(8, 24), size=len(df))
    df["order_hour"] = hours

    def get_time_of_day(h):
        if 6 <= h < 12:
            return "Morning"
        elif 12 <= h < 17:
            return "Afternoon"
        elif 17 <= h < 21:
            return "Evening"
        else:
            return "Night"

    df["time_of_day"] = pd.Series(hours).apply(get_time_of_day).values

    # 4. peak_hour_flag
    df["peak_hour_flag"] = ((df["order_hour"].between(11, 14)) |
                             (df["order_hour"].between(18, 21))).astype(int)

    # 5. traffic_level
    if "Time_taken_min" in df.columns:
        median_t = df["Time_taken_min"].median()
        conditions = [
            df["Time_taken_min"] <= median_t * 0.7,
            df["Time_taken_min"] <= median_t * 1.0,
            df["Time_taken_min"] <= median_t * 1.3,
            df["Time_taken_min"] > median_t * 1.3,
        ]
        choices = ["Low", "Medium", "High", "Jam"]
        df["traffic_level"] = np.select(conditions, choices, default="Medium")

    # 6. delay_category
    if "delivery_delay" in df.columns:
        conditions_d = [
            df["delivery_delay"] <= -5,
            df["delivery_delay"].between(-5, 5),
            df["delivery_delay"].between(5, 15),
            df["delivery_delay"] > 15,
        ]
        choices_d = ["Early", "Slightly Delayed", "On Time", "Heavily Delayed"]
        df["delay_category"] = np.select(conditions_d, choices_d, default="On Time")

    # 7. speed_kmph
    if "distance_km" in df.columns and "Time_taken_min" in df.columns:
        df["speed_kmph"] = (df["distance_km"] / (df["Time_taken_min"] / 60)).clip(0, 80)

    return df


def engineer_customer_satisfaction(df):
    """Engineer features for Customer Satisfaction."""
    print("\n--- Feature Engineering: Customer Satisfaction ---")

    # 1. overall_satisfaction_score (weighted avg of service, food, ambiance)
    if all(c in df.columns for c in ["ServiceRating", "FoodRating", "AmbianceRating"]):
        df["overall_satisfaction"] = (
            df["ServiceRating"] * 0.4 +
            df["FoodRating"] * 0.4 +
            df["AmbianceRating"] * 0.2
        ).round(2)
        print(f"  overall_satisfaction: mean={df['overall_satisfaction'].mean():.2f}")

    # 2. wait_category
    if "WaitTime" in df.columns:
        conditions = [
            df["WaitTime"] <= 10,
            df["WaitTime"] <= 20,
            df["WaitTime"] <= 35,
            df["WaitTime"] > 35,
        ]
        choices = ["Quick", "Normal", "Slow", "Very Slow"]
        df["wait_category"] = np.select(conditions, choices, default="Normal")

    # 3. income_bracket
    if "Income" in df.columns:
        df["income_bracket"] = pd.cut(
            df["Income"], bins=[0, 30000, 60000, 100000, 150000, 200000],
            labels=["Low", "Lower-Mid", "Mid", "Upper-Mid", "High"],
        )

    # 4. age_group
    if "Age" in df.columns:
        df["age_group"] = pd.cut(
            df["Age"], bins=[0, 25, 35, 50, 70],
            labels=["Gen-Z", "Millennial", "Gen-X", "Boomer"],
        )

    return df


def main():
    print("=" * 60)
    print("  STEP 3: FEATURE ENGINEERING")
    print("=" * 60)

    # FoodHub
    df_fh = pd.read_csv(os.path.join(CLEAN_DIR, "foodhub_orders_clean.csv"))
    df_fh = engineer_foodhub(df_fh)
    df_fh.to_csv(os.path.join(CLEAN_DIR, "foodhub_orders_featured.csv"), index=False)
    print(f"  ✓ Saved: foodhub_orders_featured.csv ({len(df_fh)} rows, {len(df_fh.columns)} cols)")

    # Delivery Logistics
    df_dl = pd.read_csv(os.path.join(CLEAN_DIR, "delivery_logistics_clean.csv"))
    df_dl = engineer_delivery_logistics(df_dl)
    df_dl.to_csv(os.path.join(CLEAN_DIR, "delivery_logistics_featured.csv"), index=False)
    print(f"  ✓ Saved: delivery_logistics_featured.csv ({len(df_dl)} rows, {len(df_dl.columns)} cols)")

    # Customer Satisfaction
    df_cs = pd.read_csv(os.path.join(CLEAN_DIR, "customer_satisfaction_clean.csv"))
    df_cs = engineer_customer_satisfaction(df_cs)
    df_cs.to_csv(os.path.join(CLEAN_DIR, "customer_satisfaction_featured.csv"), index=False)
    print(f"  ✓ Saved: customer_satisfaction_featured.csv ({len(df_cs)} rows, {len(df_cs.columns)} cols)")

    # Print new columns summary
    print(f"\n{'='*60}")
    print("  NEW FEATURES CREATED:")
    print(f"{'='*60}")
    print("  FoodHub: delivery_delay, time_of_day, peak_hour_flag, "
          "traffic_level, delay_category, cost_bucket")
    print("  Delivery: distance_km, delivery_delay, time_of_day, "
          "peak_hour_flag, traffic_level, delay_category, speed_kmph")
    print("  Satisfaction: overall_satisfaction, wait_category, "
          "income_bracket, age_group")


if __name__ == "__main__":
    main()
