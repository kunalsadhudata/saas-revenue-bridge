-- Step 02.13: Combine all customer movement events

WITH billing_indexed AS (
    SELECT
        month,
        customer_id,
        plan,
        mrr,

        CAST(strftime('%Y', month || '-01') AS INTEGER) * 12
        + CAST(strftime('%m', month || '-01') AS INTEGER)
            AS month_index

    FROM saas_billing
),

billing_history AS (
    SELECT
        *,

        LAG(mrr) OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS previous_observed_mrr,

        LAG(month_index) OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS previous_month_index

    FROM billing_indexed
),

active_movements AS (
    SELECT
        month,
        customer_id,

        CASE
            WHEN previous_month_index IS NULL
                THEN 0
            WHEN month_index - previous_month_index > 1
                THEN 0
            ELSE previous_observed_mrr
        END AS previous_mrr,

        mrr AS current_mrr,

        CASE
            WHEN previous_month_index IS NULL
                THEN 'New'

            WHEN month_index - previous_month_index > 1
                THEN 'Reactivation'

            WHEN month_index - previous_month_index = 1
                AND mrr > previous_observed_mrr
                THEN 'Expansion'

            WHEN month_index - previous_month_index = 1
                AND mrr < previous_observed_mrr
                THEN 'Contraction'

            WHEN month_index - previous_month_index = 1
                AND mrr = previous_observed_mrr
                THEN 'Unchanged'

            ELSE 'Invalid'
        END AS movement_type

    FROM billing_history
),

churn_movements AS (
    SELECT
        strftime(
            '%Y-%m',
            date(b.month || '-01', '+1 month')
        ) AS month,

        b.customer_id,
        b.mrr AS previous_mrr,
        0 AS current_mrr,
        'Churn' AS movement_type

    FROM saas_billing AS b

    WHERE b.month < (
        SELECT MAX(month)
        FROM saas_billing
    )

    AND NOT EXISTS (
        SELECT 1
        FROM saas_billing AS n
        WHERE n.customer_id = b.customer_id
            AND n.month = strftime(
                '%Y-%m',
                date(b.month || '-01', '+1 month')
            )
    )
),

combined_movements AS (
    SELECT * FROM active_movements

    UNION ALL

    SELECT * FROM churn_movements
)

SELECT
    COUNT(*) AS total_records,

    COUNT(DISTINCT customer_id || '|' || month)
        AS unique_customer_months,

    SUM(CASE
        WHEN movement_type = 'Invalid'
        THEN 1 ELSE 0
    END) AS invalid_classifications,

    SUM(CASE
        WHEN movement_type = 'New'
            AND NOT (previous_mrr = 0 AND current_mrr > 0)
        THEN 1

        WHEN movement_type = 'Expansion'
            AND NOT (current_mrr > previous_mrr AND previous_mrr > 0)
        THEN 1

        WHEN movement_type = 'Contraction'
            AND NOT (previous_mrr > current_mrr AND current_mrr > 0)
        THEN 1

        WHEN movement_type = 'Churn'
            AND NOT (previous_mrr > 0 AND current_mrr = 0)
        THEN 1

        WHEN movement_type = 'Reactivation'
            AND NOT (previous_mrr = 0 AND current_mrr > 0)
        THEN 1

        WHEN movement_type = 'Unchanged'
            AND NOT (previous_mrr = current_mrr AND current_mrr > 0)
        THEN 1

        ELSE 0
    END) AS rule_violations,

    SUM(CASE
        WHEN month > (SELECT MAX(month) FROM saas_billing)
            OR month < (SELECT MIN(month) FROM saas_billing)
        THEN 1 ELSE 0
    END) AS out_of_period_events,

    SUM(current_mrr - previous_mrr) AS net_mrr

FROM combined_movements;