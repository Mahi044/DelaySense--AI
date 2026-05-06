"""
Step 7: Advanced — Sentiment Analysis
======================================
Generate synthetic reviews, run sentiment analysis, and correlate with delivery delays.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
MODEL_DIR = os.path.join(BASE_DIR, "data", "modeled")


def generate_synthetic_reviews(df):
    """Generate realistic reviews based on delay category and rating."""
    np.random.seed(42)

    positive_templates = [
        "Great food and fast delivery!",
        "Arrived on time, very satisfied with the service.",
        "Excellent experience, the food was hot and fresh.",
        "Quick delivery, would order again!",
        "Very happy with the order. Prompt delivery.",
        "Food quality was amazing and delivery was super fast.",
        "One of the best delivery experiences I've had.",
        "Perfect! Hot food delivered ahead of schedule.",
    ]

    neutral_templates = [
        "Food was okay, delivery was average.",
        "Decent meal, nothing special about the delivery.",
        "It was fine, took a bit longer than expected.",
        "Average experience, food was lukewarm.",
        "Normal delivery, nothing to complain about.",
        "The food was good but delivery could be faster.",
        "Satisfactory experience overall.",
        "Not bad, but not great either.",
    ]

    negative_templates = [
        "Very late delivery, food was cold.",
        "Terrible experience, had to wait over an hour.",
        "Food arrived cold and soggy. Very disappointed.",
        "Extremely slow delivery, will not order again.",
        "Worst delivery experience ever. Food was inedible.",
        "Late delivery and wrong order. Very frustrated.",
        "The delivery took way too long. Unacceptable service.",
        "Food was bad quality and delivery was extremely delayed.",
    ]

    reviews = []
    for _, row in df.iterrows():
        delay_cat = row.get("delay_category", "On Time")
        rating = row.get("rating", 3.0)

        if delay_cat in ["Early", "On Time"] and rating >= 4:
            review = np.random.choice(positive_templates)
        elif delay_cat in ["Slightly Delayed"] or (2.5 <= rating < 4):
            review = np.random.choice(neutral_templates)
        else:
            review = np.random.choice(negative_templates)

        reviews.append(review)

    return reviews


def analyze_sentiment(reviews):
    """Analyze sentiment using a simple lexicon-based approach."""
    positive_words = {
        "great", "excellent", "fast", "perfect", "amazing", "best",
        "happy", "hot", "fresh", "satisfied", "quick", "prompt",
        "super", "ahead", "good", "wonderful",
    }
    negative_words = {
        "late", "terrible", "cold", "worst", "slow", "disappointed",
        "bad", "wrong", "frustrated", "inedible", "soggy",
        "extremely", "unacceptable", "never",
    }

    sentiments = []
    scores = []
    for review in reviews:
        words = set(review.lower().split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)

        if pos_count > neg_count:
            sentiments.append("Positive")
            scores.append(round(pos_count / (pos_count + neg_count + 1), 2))
        elif neg_count > pos_count:
            sentiments.append("Negative")
            scores.append(round(-neg_count / (pos_count + neg_count + 1), 2))
        else:
            sentiments.append("Neutral")
            scores.append(0.0)

    return sentiments, scores


def main():
    print("=" * 60)
    print("  STEP 7: ADVANCED — SENTIMENT ANALYSIS")
    print("=" * 60)

    # Load featured FoodHub data
    filepath = os.path.join(CLEAN_DIR, "foodhub_orders_featured.csv")
    if not os.path.exists(filepath):
        filepath = os.path.join(MODEL_DIR, "fact_orders.csv")

    df = pd.read_csv(filepath)
    print(f"\n  Loaded {len(df)} orders")

    # Generate synthetic reviews
    print("\n  Generating synthetic reviews...")
    df["review"] = generate_synthetic_reviews(df)

    # Analyze sentiment
    print("  Analyzing sentiment...")
    sentiments, scores = analyze_sentiment(df["review"].tolist())
    df["sentiment"] = sentiments
    df["sentiment_score"] = scores

    # Results
    print(f"\n{'='*60}")
    print("  SENTIMENT DISTRIBUTION:")
    print(f"{'='*60}")
    print(df["sentiment"].value_counts().to_string())

    print(f"\n{'='*60}")
    print("  SENTIMENT vs DELAY CATEGORY:")
    print(f"{'='*60}")
    cross = pd.crosstab(df["delay_category"], df["sentiment"], margins=True)
    print(cross.to_string())

    print(f"\n{'='*60}")
    print("  SENTIMENT SCORE vs DELIVERY DELAY:")
    print(f"{'='*60}")
    corr = df["sentiment_score"].corr(df["delivery_delay"])
    print(f"  Pearson Correlation: {corr:.4f}")

    # Group analysis
    sentiment_by_delay = df.groupby("delay_category").agg(
        avg_sentiment_score=("sentiment_score", "mean"),
        avg_rating=("rating", "mean"),
        avg_delay=("delivery_delay", "mean"),
        pct_negative=("sentiment", lambda x: (x == "Negative").mean() * 100),
        count=("sentiment", "count"),
    ).round(3)
    print(f"\n{sentiment_by_delay.to_string()}")

    # Save enriched data
    output_path = os.path.join(CLEAN_DIR, "foodhub_orders_with_sentiment.csv")
    df.to_csv(output_path, index=False)
    print(f"\n  ✓ Saved: {output_path}")


if __name__ == "__main__":
    main()
