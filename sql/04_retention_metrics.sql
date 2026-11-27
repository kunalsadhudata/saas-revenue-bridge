-- Phase 04: Retention Metrics and Insights
-- Source: Simulated SaaS billing data

WITH customer_balances AS (
    SELECT
        *,
        LAG(active_customers, 1, 0) OVER (
            ORDER BY month
        ) AS opening_customers
    FROM monthly_mrr_bridge
),

monthly_churn AS (
    SELECT
        month,
        COUNT(DISTINCT customer_id) AS churned_customers
    FROM movement_detail
    WHERE movement_type = 'Churn'
    GROUP BY month
)

SELECT
    b.month,
    b.opening_customers,
    b.active_customers,
    COALESCE(c.churned_customers, 0) AS churned_customers,

    b.opening_mrr,
    b.new_mrr,
    b.expansion_mrr,
    b.contraction_mrr,
    b.churn_mrr,
    b.reactivation_mrr,

    -- Net Revenue Retention
    100.0 * (
        b.opening_mrr
        + b.expansion_mrr
        + b.contraction_mrr
        + b.churn_mrr
    ) / NULLIF(b.opening_mrr, 0) AS nrr_pct,

    -- Gross Revenue Retention
    100.0 * (
        b.opening_mrr
        + b.contraction_mrr
        + b.churn_mrr
    ) / NULLIF(b.opening_mrr, 0) AS grr_pct,

    -- SaaS Quick Ratio
    1.0 * (
        b.new_mrr
        + b.expansion_mrr
        + b.reactivation_mrr
    ) / NULLIF(
        ABS(b.contraction_mrr) + ABS(b.churn_mrr),
        0
    ) AS quick_ratio,

    -- Customer Churn Rate
    100.0 * COALESCE(c.churned_customers, 0)
        / NULLIF(b.opening_customers, 0)
        AS customer_churn_rate_pct,

    -- Customer Retention Rate
    100.0 * (
        b.opening_customers
        - COALESCE(c.churned_customers, 0)
    ) / NULLIF(b.opening_customers, 0)
        AS customer_retention_rate_pct,

    -- Revenue Churn Rate
    100.0 * ABS(b.churn_mrr)
        / NULLIF(b.opening_mrr, 0)
        AS revenue_churn_rate_pct

FROM customer_balances AS b
LEFT JOIN monthly_churn AS c
    ON b.month = c.month

ORDER BY b.month;