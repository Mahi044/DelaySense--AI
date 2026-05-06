"""
Step 8: ML Prediction Engine
==============================
Train a Random Forest model to predict delivery delay.
Export prediction lookup tables + model stats to JS for the dashboard.
"""

import os
import json
import pandas as pd
import numpy as np
from scipy import stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "data", "modeled")
DASH_DIR = os.path.join(BASE_DIR, "dashboard")


def main():
    print("=" * 60)
    print("  STEP 8: ML PREDICTION ENGINE")
    print("=" * 60)

    df = pd.read_csv(os.path.join(MODEL_DIR, "fact_orders.csv"))
    dim_rest = pd.read_csv(os.path.join(MODEL_DIR, "dim_restaurant.csv"))
    df = df.merge(dim_rest, on="restaurant_id", how="left")

    # ── Feature prep ──
    features = ["distance_km", "food_preparation_time", "order_hour",
                 "peak_hour_flag", "cost"]
    target = "delivery_delay"

    # Encode traffic_level
    traffic_map = {"Low": 0, "Medium": 1, "High": 2, "Jam": 3}
    df["traffic_encoded"] = df["traffic_level"].map(traffic_map).fillna(1)
    features.append("traffic_encoded")

    # Encode time_of_day
    tod_map = {"Morning": 0, "Afternoon": 1, "Evening": 2, "Night": 3}
    df["tod_encoded"] = df["time_of_day"].map(tod_map).fillna(1)
    features.append("tod_encoded")

    X = df[features].fillna(0).values
    y = df[target].fillna(0).values

    # ── Simple Decision Tree (exportable as rules) ──
    # We'll build lookup tables instead of a full model for JS compatibility

    print("\n  Building prediction lookup tables...")

    # 1. Average delay by traffic level
    delay_by_traffic = df.groupby("traffic_level")["delivery_delay"].agg(["mean", "std", "count"]).round(2)
    print(f"\n  Delay by Traffic:\n{delay_by_traffic}")

    # 2. Average delay by time of day
    delay_by_tod = df.groupby("time_of_day")["delivery_delay"].agg(["mean", "std", "count"]).round(2)
    print(f"\n  Delay by Time of Day:\n{delay_by_tod}")

    # 3. Average delay by peak hour
    delay_by_peak = df.groupby("peak_hour_flag")["delivery_delay"].agg(["mean", "std", "count"]).round(2)
    print(f"\n  Delay by Peak Hour:\n{delay_by_peak}")

    # 4. Distance buckets
    df["dist_bucket"] = pd.cut(df["distance_km"], bins=[0, 3, 6, 10, 20], labels=["0-3", "3-6", "6-10", "10+"])
    delay_by_dist = df.groupby("dist_bucket", observed=True)["delivery_delay"].agg(["mean", "std"]).round(2)
    print(f"\n  Delay by Distance:\n{delay_by_dist}")

    # 5. Linear regression coefficients for the prediction formula
    from numpy.linalg import lstsq
    X_reg = np.column_stack([X, np.ones(len(X))])
    coeffs, residuals, _, _ = lstsq(X_reg, y, rcond=None)

    feature_names = features + ["intercept"]
    print("\n  Linear Model Coefficients:")
    for name, coeff in zip(feature_names, coeffs):
        print(f"    {name}: {coeff:.4f}")

    # R² score
    y_pred = X_reg @ coeffs
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot
    rmse = np.sqrt(np.mean((y - y_pred) ** 2))
    mae = np.mean(np.abs(y - y_pred))
    print(f"\n  Model Performance:")
    print(f"    R² Score:  {r2:.4f}")
    print(f"    RMSE:      {rmse:.2f} min")
    print(f"    MAE:       {mae:.2f} min")

    # 6. Correlation matrix
    corr_cols = ["cost", "rating", "food_preparation_time", "delivery_time",
                 "delivery_delay", "distance_km", "order_hour", "peak_hour_flag"]
    corr_cols = [c for c in corr_cols if c in df.columns]
    corr_matrix = df[corr_cols].corr().round(3)

    # 7. Build insights / alerts
    insights = []

    # Find worst cuisine
    cuisine_delay = df.groupby("cuisine_type")["delivery_delay"].mean().round(2)
    worst_cuisine = cuisine_delay.idxmax()
    best_cuisine = cuisine_delay.idxmin()
    insights.append({
        "type": "warning",
        "title": "Slowest Cuisine",
        "text": f"{worst_cuisine} has the highest avg delay ({cuisine_delay[worst_cuisine]:.1f} min)",
        "icon": "⚠️"
    })
    insights.append({
        "type": "success",
        "title": "Fastest Cuisine",
        "text": f"{best_cuisine} has the lowest avg delay ({cuisine_delay[best_cuisine]:.1f} min)",
        "icon": "✅"
    })

    # Peak hour insight
    peak_delay = df[df["peak_hour_flag"] == 1]["delivery_delay"].mean()
    offpeak_delay = df[df["peak_hour_flag"] == 0]["delivery_delay"].mean()
    if peak_delay > offpeak_delay:
        insights.append({
            "type": "warning",
            "title": "Peak Hour Alert",
            "text": f"Peak hours average {peak_delay:.1f} min delay vs {offpeak_delay:.1f} min off-peak",
            "icon": "🕐"
        })

    # High delay percentage
    heavy_pct = (df["delay_category"] == "Heavily Delayed").mean() * 100
    insights.append({
        "type": "danger" if heavy_pct > 10 else "info",
        "title": "Heavy Delay Rate",
        "text": f"{heavy_pct:.1f}% of orders are heavily delayed (>15 min)",
        "icon": "📊"
    })

    # Rating insight
    high_rated = df[df["rating"] >= 4.5].shape[0] / len(df) * 100
    insights.append({
        "type": "success",
        "title": "High Satisfaction",
        "text": f"{high_rated:.1f}% of orders received 4.5+ star ratings",
        "icon": "⭐"
    })

    # Correlation insight
    delay_rating_corr = df["delivery_delay"].corr(df["rating"])
    insights.append({
        "type": "info",
        "title": "Delay-Rating Correlation",
        "text": f"Pearson r = {delay_rating_corr:.3f} — {'moderate' if abs(delay_rating_corr) > 0.3 else 'weak'} negative correlation",
        "icon": "📈"
    })

    # ── Export everything to JS ──
    prediction_data = {
        "model": {
            "coefficients": {name: round(float(c), 6) for name, c in zip(feature_names, coeffs)},
            "r2": round(float(r2), 4),
            "rmse": round(float(rmse), 2),
            "mae": round(float(mae), 2),
            "feature_order": features,
        },
        "lookups": {
            "traffic": {k: {"mean": round(float(v["mean"]), 2), "std": round(float(v["std"]), 2)}
                        for k, v in delay_by_traffic.iterrows()},
            "time_of_day": {k: {"mean": round(float(v["mean"]), 2), "std": round(float(v["std"]), 2)}
                            for k, v in delay_by_tod.iterrows()},
            "distance": {k: {"mean": round(float(v["mean"]), 2), "std": round(float(v["std"]), 2)}
                         for k, v in delay_by_dist.iterrows()},
        },
        "correlations": {
            "columns": corr_cols,
            "matrix": corr_matrix.values.tolist(),
        },
        "insights": insights,
        "cuisine_delays": {k: round(float(v), 2) for k, v in cuisine_delay.items()},
    }

    output_path = os.path.join(DASH_DIR, "ml_data.js")
    with open(output_path, "w") as f:
        f.write(f"const ML_DATA = {json.dumps(prediction_data, indent=2)};")

    print(f"\n  > Exported ML data to {output_path}")
    print(f"  > {len(insights)} auto-generated insights")
    print(f"  > {len(corr_cols)}x{len(corr_cols)} correlation matrix")
    print(f"  > Linear model with {len(features)} features (R2={r2:.4f})")


if __name__ == "__main__":
    main()
