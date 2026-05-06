const ML_DATA = {
  "model": {
    "coefficients": {
      "distance_km": 0.004305,
      "food_preparation_time": 0.999011,
      "order_hour": 0.008215,
      "peak_hour_flag": 0.113369,
      "cost": 0.003565,
      "traffic_encoded": 6.192273,
      "tod_encoded": -0.039324,
      "intercept": -36.349262
    },
    "r2": 0.9185,
    "rmse": 1.95,
    "mae": 1.62,
    "feature_order": [
      "distance_km",
      "food_preparation_time",
      "order_hour",
      "peak_hour_flag",
      "cost",
      "traffic_encoded",
      "tod_encoded"
    ]
  },
  "lookups": {
    "traffic": {
      "High": {
        "mean": 3.74,
        "std": 4.96
      },
      "Jam": {
        "mean": 9.29,
        "std": 5.2
      },
      "Low": {
        "mean": -8.86,
        "std": 4.75
      },
      "Medium": {
        "mean": -2.67,
        "std": 5.17
      }
    },
    "time_of_day": {
      "Afternoon": {
        "mean": -0.26,
        "std": 6.73
      },
      "Evening": {
        "mean": -0.77,
        "std": 6.87
      },
      "Morning": {
        "mean": -0.23,
        "std": 6.77
      },
      "Night": {
        "mean": -0.75,
        "std": 7.04
      }
    },
    "distance": {
      "0-3": {
        "mean": -0.71,
        "std": 6.99
      },
      "3-6": {
        "mean": -0.09,
        "std": 6.29
      },
      "6-10": {
        "mean": -0.37,
        "std": 7.23
      },
      "10+": {
        "mean": -0.7,
        "std": 6.79
      }
    }
  },
  "correlations": {
    "columns": [
      "cost",
      "rating",
      "food_preparation_time",
      "delivery_time",
      "delivery_delay",
      "distance_km",
      "order_hour",
      "peak_hour_flag"
    ],
    "matrix": [
      [
        1.0,
        0.002,
        0.042,
        -0.03,
        0.006,
        0.026,
        0.015,
        0.036
      ],
      [
        0.002,
        1.0,
        -0.005,
        -0.006,
        -0.008,
        -0.037,
        0.013,
        -0.007
      ],
      [
        0.042,
        -0.005,
        1.0,
        0.011,
        0.686,
        -0.004,
        -0.027,
        0.003
      ],
      [
        -0.03,
        -0.006,
        0.011,
        1.0,
        0.735,
        -0.008,
        -0.013,
        -0.004
      ],
      [
        0.006,
        -0.008,
        0.686,
        0.735,
        1.0,
        -0.009,
        -0.028,
        -0.0
      ],
      [
        0.026,
        -0.037,
        -0.004,
        -0.008,
        -0.009,
        1.0,
        -0.024,
        0.017
      ],
      [
        0.015,
        0.013,
        -0.027,
        -0.013,
        -0.028,
        -0.024,
        1.0,
        0.124
      ],
      [
        0.036,
        -0.007,
        0.003,
        -0.004,
        -0.0,
        0.017,
        0.124,
        1.0
      ]
    ]
  },
  "insights": [
    {
      "type": "warning",
      "title": "Slowest Cuisine",
      "text": "Italian has the highest avg delay (0.3 min)",
      "icon": "\u26a0\ufe0f"
    },
    {
      "type": "success",
      "title": "Fastest Cuisine",
      "text": "Korean has the lowest avg delay (-5.6 min)",
      "icon": "\u2705"
    },
    {
      "type": "info",
      "title": "Heavy Delay Rate",
      "text": "0.4% of orders are heavily delayed (>15 min)",
      "icon": "\ud83d\udcca"
    },
    {
      "type": "success",
      "title": "High Satisfaction",
      "text": "69.8% of orders received 4.5+ star ratings",
      "icon": "\u2b50"
    },
    {
      "type": "info",
      "title": "Delay-Rating Correlation",
      "text": "Pearson r = -0.008 \u2014 weak negative correlation",
      "icon": "\ud83d\udcc8"
    }
  ],
  "cuisine_delays": {
    "American": -0.38,
    "Chinese": -0.63,
    "French": 0.22,
    "Indian": -0.81,
    "Italian": 0.34,
    "Japanese": -0.36,
    "Korean": -5.62,
    "Mediterranean": -1.41,
    "Mexican": -0.88,
    "Middle Eastern": -1.24,
    "Southern": -0.59,
    "Spanish": -1.67,
    "Thai": -1.53,
    "Vietnamese": -0.14
  }
};