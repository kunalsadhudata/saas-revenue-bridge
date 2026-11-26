-- Phase 03: Monthly MRR Bridge
-- Step 03.09: Calculated closing MRR

WITH RECURSIVE calendar AS (
    SELECT '2025-01-01' AS month_date

    UNION ALL

    SELECT DATE(month_date, '+1 month')
    FROM calendar
    WHERE month_date < '2026-09-01'
),

monthly_billing AS (
    SELECT
        month,
        COUNT(DISTINCT customer_id) AS active_customers,
        SUM(mrr) AS actual_closing_mrr
    FROM saas_billing
    GROUP BY month
),

monthly_snapshots AS (
    SELECT
        STRFTIME('%Y-%m', c.month_date) AS month,
        COALESCE(b.active_customers, 0) AS active_customers,
        COALESCE(b.actual_closing_mrr, 0) AS actual_closing_mrr
    FROM calendar AS c
    LEFT JOIN monthly_billing AS b
        ON STRFTIME('%Y-%m', c.month_date) = b.month
),

opening_balances AS (
    SELECT
        month,
        active_customers,
        LAG(actual_closing_mrr, 1, 0) OVER (
            ORDER BY month
        ) AS opening_mrr,
        actual_closing_mrr
    FROM monthly_snapshots
),

movement_pivot AS (
    SELECT
        month,

        SUM(CASE WHEN movement_type = 'New'
            THEN signed_mrr ELSE 0 END) AS new_mrr,

        SUM(CASE WHEN movement_type = 'Expansion'
            THEN signed_mrr ELSE 0 END) AS expansion_mrr,

        SUM(CASE WHEN movement_type = 'Contraction'
            THEN signed_mrr ELSE 0 END) AS contraction_mrr,

        SUM(CASE WHEN movement_type = 'Churn'
            THEN signed_mrr ELSE 0 END) AS churn_mrr,

        SUM(CASE WHEN movement_type = 'Reactivation'
            THEN signed_mrr ELSE 0 END) AS reactivation_mrr

    FROM movement_detail
    GROUP BY month
),

bridge_movements AS (
    SELECT
        b.month,
        b.active_customers,
        b.opening_mrr,
        COALESCE(m.new_mrr, 0) AS new_mrr,
        COALESCE(m.expansion_mrr, 0) AS expansion_mrr,
        COALESCE(m.contraction_mrr, 0) AS contraction_mrr,
        COALESCE(m.churn_mrr, 0) AS churn_mrr,
        COALESCE(m.reactivation_mrr, 0) AS reactivation_mrr,

        COALESCE(m.new_mrr, 0)
        + COALESCE(m.expansion_mrr, 0)
        + COALESCE(m.contraction_mrr, 0)
        + COALESCE(m.churn_mrr, 0)
        + COALESCE(m.reactivation_mrr, 0)
            AS net_mrr_movement,

        b.actual_closing_mrr

    FROM opening_balances AS b
    LEFT JOIN movement_pivot AS m
        ON b.month = m.month
)

SELECT
    month,
    active_customers,
    opening_mrr,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churn_mrr,
    reactivation_mrr,
    net_mrr_movement,

    opening_mrr + net_mrr_movement
        AS calculated_closing_mrr,

    actual_closing_mrr

FROM bridge_movements
ORDER BY month;