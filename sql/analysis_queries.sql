-- ============================================================
-- Food Delivery Delay & Customer Rating Analysis
-- SQL Queries for Star Schema
-- ============================================================

-- Q1: Correlation between delivery delay and customer ratings
SELECT
    delay_category,
    COUNT(*) AS order_count,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(delivery_delay), 2) AS avg_delay_min,
    ROUND(MIN(rating), 2) AS min_rating,
    ROUND(MAX(rating), 2) AS max_rating
FROM fact_orders
GROUP BY delay_category
ORDER BY avg_delay_min ASC;

-- Q2: Distance vs Customer Satisfaction
SELECT
    CASE
        WHEN distance_km <= 3 THEN '0-3 km'
        WHEN distance_km <= 6 THEN '3-6 km'
        WHEN distance_km <= 10 THEN '6-10 km'
        ELSE '10+ km'
    END AS distance_bucket,
    COUNT(*) AS order_count,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(delivery_time), 2) AS avg_delivery_time,
    ROUND(AVG(delivery_delay), 2) AS avg_delay
FROM fact_orders
GROUP BY distance_bucket
ORDER BY avg_delay ASC;

-- Q3: Restaurant Preparation Delay Impact on Ratings
SELECT
    r.restaurant_name,
    r.cuisine_type,
    COUNT(f.order_id) AS total_orders,
    ROUND(AVG(f.food_preparation_time), 2) AS avg_prep_time,
    ROUND(AVG(f.delivery_delay), 2) AS avg_delay,
    ROUND(AVG(f.rating), 2) AS avg_rating
FROM fact_orders f
JOIN dim_restaurant r ON f.restaurant_id = r.restaurant_id
GROUP BY r.restaurant_name, r.cuisine_type
HAVING total_orders >= 5
ORDER BY avg_prep_time DESC
LIMIT 15;

-- Q4: Traffic Level vs Delivery Time
SELECT
    traffic_level,
    COUNT(*) AS order_count,
    ROUND(AVG(delivery_time), 2) AS avg_delivery_time,
    ROUND(AVG(delivery_delay), 2) AS avg_delay,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(distance_km), 2) AS avg_distance
FROM fact_orders
GROUP BY traffic_level
ORDER BY avg_delivery_time ASC;

-- Q5: Peak Hour Delay Patterns
SELECT
    CASE WHEN peak_hour_flag = 1 THEN 'Peak Hour' ELSE 'Off-Peak' END AS period,
    time_of_day,
    COUNT(*) AS order_count,
    ROUND(AVG(delivery_time), 2) AS avg_delivery_time,
    ROUND(AVG(delivery_delay), 2) AS avg_delay,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(
        SUM(CASE WHEN delay_category IN ('Slightly Delayed', 'Heavily Delayed')
            THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS delay_pct
FROM fact_orders
GROUP BY peak_hour_flag, time_of_day
ORDER BY peak_hour_flag DESC, avg_delay DESC;
