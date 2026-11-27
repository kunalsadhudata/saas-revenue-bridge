-- Phase 04: Retention Metrics and Insights
-- Step 04.06: Customer Retention Cohort Analysis
-- Source: Simulated SaaS billing data

WITH customer_cohorts AS (
    SELECT
        customer_id,
        MIN(month) AS cohort_month
    FROM saas_billing
    GROUP BY customer_id
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),

calendar AS (
    SELECT DISTINCT month
    FROM saas_billing
),

cohort_periods AS (
    SELECT
        c.cohort_month,
        m.month AS activity_month,
        c.cohort_size
    FROM cohort_sizes AS c
    CROSS JOIN calendar AS m
    WHERE m.month >= c.cohort_month
),

cohort_activity AS (
    SELECT
        c.cohort_month,
        b.month AS activity_month,
        COUNT(DISTINCT b.customer_id)
            AS active_customers
    FROM saas_billing AS b
    JOIN customer_cohorts AS c
        ON b.customer_id = c.customer_id
    GROUP BY c.cohort_month, b.month
)

SELECT
    p.cohort_month,
    p.activity_month,

    (
        CAST(SUBSTR(p.activity_month, 1, 4) AS INTEGER)
        - CAST(SUBSTR(p.cohort_month, 1, 4) AS INTEGER)
    ) * 12
    + CAST(SUBSTR(p.activity_month, 6, 2) AS INTEGER)
    - CAST(SUBSTR(p.cohort_month, 6, 2) AS INTEGER)
        AS cohort_age,

    p.cohort_size,

    COALESCE(a.active_customers, 0)
        AS active_customers,

    100.0 * COALESCE(a.active_customers, 0)
        / NULLIF(p.cohort_size, 0)
        AS customer_retention_pct

FROM cohort_periods AS p
LEFT JOIN cohort_activity AS a
    ON p.cohort_month = a.cohort_month
    AND p.activity_month = a.activity_month

ORDER BY p.cohort_month, cohort_age;