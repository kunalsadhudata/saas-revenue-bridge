-- Phase 04: Retention Metrics and Insights
-- Step 04.09: Plan-Level Movement Analysis
-- Source: Simulated SaaS billing data

WITH opening_customers AS (
    SELECT
        STRFTIME(
            '%Y-%m',
            DATE(month || '-01', '+1 month')
        ) AS month,
        customer_id,
        plan,
        mrr AS previous_mrr
    FROM saas_billing
    WHERE month < (
        SELECT MAX(month)
        FROM saas_billing
    )
),

customer_movements AS (
    SELECT
        o.month,
        o.customer_id,
        o.plan,
        o.previous_mrr,
        COALESCE(b.mrr, 0) AS current_mrr,

        CASE
            WHEN b.customer_id IS NULL
                THEN 'Churn'
            WHEN b.mrr > o.previous_mrr
                THEN 'Expansion'
            WHEN b.mrr < o.previous_mrr
                THEN 'Contraction'
            ELSE 'Unchanged'
        END AS movement_type

    FROM opening_customers AS o

    LEFT JOIN saas_billing AS b
        ON o.customer_id = b.customer_id
        AND o.month = b.month
)

SELECT
    month,
    plan,

    COUNT(*) AS opening_customers,
    SUM(previous_mrr) AS opening_mrr,

    SUM(CASE WHEN movement_type = 'Churn'
        THEN 1 ELSE 0 END)
        AS churned_customers,

    SUM(CASE WHEN movement_type = 'Expansion'
        THEN 1 ELSE 0 END)
        AS upgraded_customers,

    SUM(CASE WHEN movement_type = 'Contraction'
        THEN 1 ELSE 0 END)
        AS downgraded_customers,

    SUM(CASE WHEN movement_type = 'Churn'
        THEN -previous_mrr ELSE 0 END)
        AS churn_mrr,

    SUM(CASE WHEN movement_type = 'Expansion'
        THEN current_mrr - previous_mrr
        ELSE 0 END)
        AS expansion_mrr,

    SUM(CASE WHEN movement_type = 'Contraction'
        THEN current_mrr - previous_mrr
        ELSE 0 END)
        AS contraction_mrr,

    100.0 * SUM(
        CASE WHEN movement_type = 'Churn'
            THEN 1 ELSE 0 END
    ) / NULLIF(COUNT(*), 0)
        AS customer_churn_rate_pct

FROM customer_movements

GROUP BY month, plan
ORDER BY month, plan;