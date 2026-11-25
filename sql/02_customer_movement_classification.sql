-- Step 02.07: Detect calendar gaps

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

        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS customer_row_number,

        LAG(month) OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS previous_observed_month,

        LAG(mrr) OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS previous_observed_mrr,

        LAG(month_index) OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS previous_month_index

    FROM billing_indexed
)

SELECT
    *,
    month_index - previous_month_index AS month_gap,

    CASE
        WHEN previous_observed_month IS NULL
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

ORDER BY month_gap DESC, customer_id, month
LIMIT 25;