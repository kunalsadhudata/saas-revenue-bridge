-- Step 02.12: Detect churn within the observation period

WITH observation_period AS (
    SELECT MAX(month) AS last_observed_month
    FROM saas_billing
)

SELECT
    strftime(
        '%Y-%m',
        date(b.month || '-01', '+1 month')
    ) AS churn_month,

    b.customer_id,
    b.plan AS previous_plan,
    b.mrr AS previous_mrr,
    0 AS current_mrr,
    'Churn' AS movement_type

FROM saas_billing AS b

CROSS JOIN observation_period AS o

WHERE b.month < o.last_observed_month

AND NOT EXISTS (
    SELECT 1
    FROM saas_billing AS n
    WHERE n.customer_id = b.customer_id
        AND n.month = strftime(
            '%Y-%m',
            date(b.month || '-01', '+1 month')
        )
)

ORDER BY churn_month DESC, customer_id
LIMIT 15;