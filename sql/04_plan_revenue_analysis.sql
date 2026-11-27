-- Phase 04: Retention Metrics and Insights
-- Step 04.08: Plan-Level Revenue Analysis
-- Source: Simulated SaaS billing data

WITH plans AS (
    SELECT 'Starter' AS plan
    UNION ALL
    SELECT 'Growth'
    UNION ALL
    SELECT 'Scale'
),

calendar AS (
    SELECT DISTINCT month
    FROM saas_billing
),

plan_periods AS (
    SELECT
        c.month,
        p.plan
    FROM calendar AS c
    CROSS JOIN plans AS p
),

plan_revenue AS (
    SELECT
        month,
        plan,
        COUNT(DISTINCT customer_id) AS active_customers,
        SUM(mrr) AS plan_mrr
    FROM saas_billing
    GROUP BY month, plan
),

monthly_totals AS (
    SELECT
        month,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(mrr) AS total_mrr
    FROM saas_billing
    GROUP BY month
)

SELECT
    p.month,
    p.plan,

    COALESCE(r.active_customers, 0)
        AS active_customers,

    COALESCE(r.plan_mrr, 0)
        AS plan_mrr,

    COALESCE(r.plan_mrr, 0) * 12
        AS plan_arr,

    100.0 * COALESCE(r.active_customers, 0)
        / NULLIF(t.total_customers, 0)
        AS customer_share_pct,

    100.0 * COALESCE(r.plan_mrr, 0)
        / NULLIF(t.total_mrr, 0)
        AS revenue_share_pct,

    1.0 * COALESCE(r.plan_mrr, 0)
        / NULLIF(r.active_customers, 0)
        AS arpu

FROM plan_periods AS p

LEFT JOIN plan_revenue AS r
    ON p.month = r.month
    AND p.plan = r.plan

JOIN monthly_totals AS t
    ON p.month = t.month

ORDER BY
    p.month,
    CASE p.plan
        WHEN 'Starter' THEN 1
        WHEN 'Growth' THEN 2
        WHEN 'Scale' THEN 3
    END;