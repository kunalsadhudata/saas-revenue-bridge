-- Phase 04: Retention Metrics and Insights
-- Step 04.05: Customer Cohort Assignment
-- Source: Simulated SaaS billing data

SELECT
    customer_id,
    MIN(month) AS cohort_month
FROM saas_billing
GROUP BY customer_id
ORDER BY cohort_month, customer_id;

