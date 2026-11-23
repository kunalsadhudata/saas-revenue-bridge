
# SaaS Revenue Bridge — Business Rules and Assumptions

## 1. Project Context

This project analyzes a fictional subscription software company.

All customer and billing records will be SIMULATED.
No real customer or company data is used.

Business question:
Why did MRR grow by approximately 4% last month?
How much came from new customers, upgrades, downgrades,
cancellations, and returning customers?

## 2. Subscription Plans

| Plan | Monthly Price |
|---|---:|
| Starter | $29 |
| Growth | $99 |
| Scale | $299 |

Annual contracts contribute their contract price / 12
to monthly recurring revenue.

One-time fees and usage overages are excluded from MRR.

## 3. Revenue Definitions

MRR = Sum of monthly recurring revenue from active subscriptions.

ARR = MRR × 12.

New = First month ever paying.

Expansion = Existing customer pays more than last month.

Contraction = Existing customer pays less but remains active.

Churn = Customer paid last month but pays nothing now.

Reactivation = Customer paid previously, became inactive,
and returned in a later month.

## 4. Monthly MRR Bridge

Ending MRR =
Starting MRR
+ New MRR
+ Expansion MRR
+ Reactivation MRR
- Contraction MRR
- Churn MRR

The bridge must reconcile exactly every month.

## 5. Monthly SaaS Metrics

Monthly NRR =
(Start + Expansion - Contraction - Churn) / Start

Monthly GRR =
(Start - Contraction - Churn) / Start

Monthly Quick Ratio =
(New + Expansion + Reactivation) / (Contraction + Churn)

Undefined ratios will be reported as N/A,
not silently replaced with zero.

## 6. Simulation Assumptions

Duration: 21 months.

Approximately 40 new customers per month.

Monthly churn probability: approximately 3.5%.

Monthly upgrade probability: approximately 4%.

Monthly downgrade probability: approximately 2%.

Returning-customer probability: approximately 1–2%
per month among previously churned customers.

These are simulation parameters, not observed results.

The final month is intended to illustrate approximately
4% MRR growth, but actual simulated results must be
verified before reporting that figure as a finding.

## 7. Data Structure

Columns:
- month
- customer_id
- plan
- mrr

Each row represents one active customer subscription
in a particular month.

Inactive customer-months will not appear in the
active subscription dataset.

## 8. Data Quality and Validation Rules

1. Never modify raw data after generation.
2. Record row counts before and after cleaning.
3. Do not silently delete records.
4. Detect missing months using a numeric month index.
5. SQLite LAG() returns the previous row, not
   necessarily the previous calendar month.
6. Reactivation must never be classified as New.
7. Use SQLite-compatible date functions.
8. Independently verify the MRR bridge using
   SQLite SQL and Python pandas.
9. Monthly bridge differences must equal zero.
10. Document all assumptions and limitations.

## 9. Important Limitations

This dataset is simulated for educational purposes.

Results do not represent an actual SaaS business.

Simulation assumptions may influence observed
growth, churn, retention, and expansion.

All findings must be labeled as simulated.
