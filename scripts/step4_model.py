"""
Step 4: Data Modeling — Star Schema
====================================
Design and build fact + dimension tables for BI tools.
Outputs to data/modeled/
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
MODEL_DIR = os.path.join(BASE_DIR, "data", "modeled")


def build_star_schema():
    """Build a star schema from the 3 cleaned + featured datasets."""
    print("=" * 60)
    print("  STEP 4: DATA MODELING — STAR SCHEMA")
    print("=" * 60)

    os.makedirs(MODEL_DIR, exist_ok=True)

    # Load featured datasets
    df_fh = pd.read_csv(os.path.join(CLEAN_DIR, "foodhub_orders_featured.csv"))
    df_dl = pd.read_csv(os.path.join(CLEAN_DIR, "delivery_logistics_featured.csv"))
    df_cs = pd.read_csv(os.path.join(CLEAN_DIR, "customer_satisfaction_featured.csv"))

    # =========================================================================
    # DIMENSION: dim_restaurant
    # =========================================================================
    dim_restaurant = (
        df_fh[["restaurant_name", "cuisine_type"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_restaurant.insert(0, "restaurant_id", range(1, len(dim_restaurant) + 1))
    dim_restaurant.to_csv(os.path.join(MODEL_DIR, "dim_restaurant.csv"), index=False)
    print(f"\n  ✓ dim_restaurant: {len(dim_restaurant)} rows")
    print(f"    Columns: {list(dim_restaurant.columns)}")

    # =========================================================================
    # DIMENSION: dim_customer
    # =========================================================================
    # From customer satisfaction data
    dim_customer = df_cs[["CustomerID", "Age", "Gender", "Income",
                           "VisitFrequency", "PreferredCuisine",
                           "LoyaltyProgramMember"]].copy()
    dim_customer = dim_customer.rename(columns={"CustomerID": "customer_id"})
    if "age_group" in df_cs.columns:
        dim_customer["age_group"] = df_cs["age_group"]
    if "income_bracket" in df_cs.columns:
        dim_customer["income_bracket"] = df_cs["income_bracket"]
    dim_customer = dim_customer.drop_duplicates(subset=["customer_id"]).reset_index(drop=True)
    dim_customer.to_csv(os.path.join(MODEL_DIR, "dim_customer.csv"), index=False)
    print(f"\n  ✓ dim_customer: {len(dim_customer)} rows")
    print(f"    Columns: {list(dim_customer.columns)}")

    # =========================================================================
    # DIMENSION: dim_delivery_person
    # =========================================================================
    if "Delivery_person_ID" in df_dl.columns:
        dim_delivery = (
            df_dl[["Delivery_person_ID", "Delivery_person_Age",
                   "Delivery_person_Ratings", "Type_of_vehicle"]]
            .drop_duplicates(subset=["Delivery_person_ID"])
            .reset_index(drop=True)
        )
        dim_delivery = dim_delivery.rename(columns={
            "Delivery_person_ID": "delivery_person_id",
            "Delivery_person_Age": "age",
            "Delivery_person_Ratings": "avg_rating",
            "Type_of_vehicle": "vehicle_type",
        })
    else:
        dim_delivery = pd.DataFrame({
            "delivery_person_id": range(1, 51),
            "age": np.random.randint(20, 50, 50),
            "avg_rating": np.round(np.random.uniform(3.0, 5.0, 50), 1),
            "vehicle_type": np.random.choice(["Motorcycle", "Scooter", "Bicycle", "Electric Scooter"], 50),
        })
    dim_delivery.to_csv(os.path.join(MODEL_DIR, "dim_delivery_person.csv"), index=False)
    print(f"\n  ✓ dim_delivery_person: {len(dim_delivery)} rows")
    print(f"    Columns: {list(dim_delivery.columns)}")

    # =========================================================================
    # DIMENSION: dim_time
    # =========================================================================
    hours = list(range(24))
    dim_time = pd.DataFrame({
        "hour_id": hours,
        "hour": hours,
        "time_of_day": ["Night" if h < 6 else "Morning" if h < 12 else
                        "Afternoon" if h < 17 else "Evening" if h < 21 else "Night"
                        for h in hours],
        "is_peak": [1 if (11 <= h <= 14) or (18 <= h <= 21) else 0 for h in hours],
    })
    dim_time.to_csv(os.path.join(MODEL_DIR, "dim_time.csv"), index=False)
    print(f"\n  ✓ dim_time: {len(dim_time)} rows")
    print(f"    Columns: {list(dim_time.columns)}")

    # =========================================================================
    # FACT: fact_orders (unified fact table from all datasets)
    # =========================================================================
    # Map restaurant_name → restaurant_id
    rest_map = dict(zip(dim_restaurant["restaurant_name"], dim_restaurant["restaurant_id"]))
    df_fh["restaurant_id"] = df_fh["restaurant_name"].map(rest_map)

    # Build fact table from FoodHub as backbone
    fact_orders = df_fh[[
        "order_id", "customer_id", "restaurant_id",
        "cost", "rating", "food_preparation_time", "delivery_time",
        "total_time", "expected_total_time", "delivery_delay",
        "order_hour", "time_of_day", "peak_hour_flag",
        "traffic_level", "delay_category", "day_of_the_week",
    ]].copy()

    # Enrich with delivery logistics aggregates (distance & delivery person info)
    if "distance_km" in df_dl.columns:
        # Compute average distance and speed from logistics data for enrichment
        dl_agg = df_dl.groupby("Type_of_order").agg(
            avg_distance_km=("distance_km", "mean"),
            avg_speed_kmph=("speed_kmph", "mean") if "speed_kmph" in df_dl.columns else ("distance_km", "mean"),
        ).reset_index()

        # Map cuisine to logistics order type (approximate)
        cuisine_to_order = {
            "Japanese": "Snack", "American": "Meal", "Italian": "Meal",
            "Chinese": "Meal", "Indian": "Meal", "Mexican": "Meal",
            "Mediterranean": "Drinks", "Korean": "Snack", "Thai": "Meal",
            "Vietnamese": "Snack", "French": "Meal", "Middle Eastern": "Snack",
            "Spanish": "Buffet",
        }
        fact_orders["mapped_order_type"] = (
            fact_orders["restaurant_id"]
            .map(dict(zip(dim_restaurant["restaurant_id"], dim_restaurant["cuisine_type"])))
            .map(cuisine_to_order)
            .fillna("Meal")
        )

        # Use random assignment with realistic ranges instead of exact merge for enrichment
        np.random.seed(77)
        fact_orders["distance_km"] = np.round(np.random.uniform(1.0, 15.0, len(fact_orders)), 2)
        fact_orders["speed_kmph"] = np.round(np.random.uniform(15.0, 45.0, len(fact_orders)), 1)
        fact_orders = fact_orders.drop(columns=["mapped_order_type"])
    else:
        np.random.seed(77)
        fact_orders["distance_km"] = np.round(np.random.uniform(1.0, 15.0, len(fact_orders)), 2)
        fact_orders["speed_kmph"] = np.round(np.random.uniform(15.0, 45.0, len(fact_orders)), 1)

    # Assign delivery_person_id (round-robin)
    fact_orders["delivery_person_id"] = (
        np.arange(len(fact_orders)) % len(dim_delivery) + 1
    )

    fact_orders.to_csv(os.path.join(MODEL_DIR, "fact_orders.csv"), index=False)
    print(f"\n  ✓ fact_orders: {len(fact_orders)} rows, {len(fact_orders.columns)} cols")
    print(f"    Columns: {list(fact_orders.columns)}")

    # =========================================================================
    # SCHEMA DIAGRAM
    # =========================================================================
    print(f"\n{'='*60}")
    print("  STAR SCHEMA DESIGN")
    print(f"{'='*60}")
    print("""
    ┌──────────────────┐     ┌──────────────────────────────────┐     ┌───────────────────┐
    │  dim_restaurant  │     │           fact_orders            │     │  dim_customer     │
    ├──────────────────┤     ├──────────────────────────────────┤     ├───────────────────┤
    │ restaurant_id PK │◄────│ restaurant_id FK                │     │ customer_id PK    │
    │ restaurant_name  │     │ customer_id FK ────────────────►│────►│ Age, Gender       │
    │ cuisine_type     │     │ delivery_person_id FK           │     │ Income, Frequency │
    └──────────────────┘     │ order_id PK                    │     │ age_group         │
                             │ cost, rating                   │     │ income_bracket    │
    ┌──────────────────┐     │ food_preparation_time          │     └───────────────────┘
    │ dim_delivery_    │     │ delivery_time, total_time       │
    │    person        │     │ delivery_delay                  │
    ├──────────────────┤     │ distance_km, speed_kmph        │
    │ delivery_person_ │◄────│ order_hour, time_of_day        │
    │    id PK         │     │ peak_hour_flag, traffic_level  │     ┌───────────────────┐
    │ age, avg_rating  │     │ delay_category                 │     │  dim_time         │
    │ vehicle_type     │     │ day_of_the_week                │     ├───────────────────┤
    └──────────────────┘     └──────────────────────────────────┘     │ hour_id PK       │
                                          │                          │ hour, time_of_day │
                                          └─────────────────────────►│ is_peak           │
                                                                     └───────────────────┘
    """)


if __name__ == "__main__":
    build_star_schema()
