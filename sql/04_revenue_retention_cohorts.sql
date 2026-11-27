-- Phase 04: Retention Metrics and Insights
-- Step 04.07: Revenue Retention Cohort Analysis
-- Source: Simulated SaaS billing data

WITH customer_cohorts AS (
    SELECT
        customer_id,
        MIN(month) AS cohort_month
    FROM saas_billing
    GROUP BY customer_id
),

cohort_revenue AS (
    SELECT
        c.cohort_month,
        b.month AS activity_month,
        SUM(b.mrr) AS cohort_mrr
    FROM saas_billing AS b
    JOIN customer_cohorts AS c
        ON b.customer_id = c.customer_id
    GROUP BY c.cohort_month, b.month
),

cohort_baseline AS (
    SELECT
        cohort_month,
        cohort_mrr AS initial_cohort_mrr
    FROM cohort_revenue
    WHERE activity_month = cohort_month
),

calendar AS (
    SELECT DISTINCT month
    FROM saas_billing
),

cohort_periods AS (
    SELECT
        c.cohort_month,
        m.month AS activity_month,
        c.initial_cohort_mrr
    FROM cohort_baseline AS c
    CROSS JOIN calendar AS m
    WHERE m.month >= c.cohort_month
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

    p.initial_cohort_mrr,

    COALESCE(r.cohort_mrr, 0) AS current_cohort_mrr,

    100.0 * COALESCE(r.cohort_mrr, 0)
        / NULLIF(p.initial_cohort_mrr, 0)
        AS revenue_retention_pct

FROM cohort_periods AS p
LEFT JOIN cohort_revenue AS r
    ON p.cohort_month = r.cohort_month
    AND p.activity_month = r.activity_month

ORDER BY p.cohort_month, cohort_age;