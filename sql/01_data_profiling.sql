-- Query 1: Dataset overview

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT month) AS total_months,
    MIN(month) AS start_month,
    MAX(month) AS end_month
FROM saas_billing;


-- Query 2: Subscription plan distribution

SELECT
    plan,
    COUNT(*) AS billing_records,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(mrr) AS total_recurring_revenue
FROM saas_billing
GROUP BY plan
ORDER BY total_recurring_revenue DESC;


-- Query 3: Monthly revenue overview

SELECT
    month,
    COUNT(DISTINCT customer_id) AS active_customers,
    SUM(mrr) AS monthly_mrr,
    SUM(mrr) * 12 AS arr
FROM saas_billing
GROUP BY month
ORDER BY month;

