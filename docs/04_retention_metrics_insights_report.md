# Phase 04 — Retention Metrics and Insights

## 1. Objective

Evaluate the revenue retention, customer retention, growth efficiency, cohort performance and subscription plan performance of a fictional SaaS company.

All results are based on simulated billing data.

## 2. Analysis Scope

- Analysis period: January 2025 to September 2026
- Total months: 21
- Total unique customers: 840
- Customer acquisition cohorts: 21
- Subscription plans: Starter, Growth and Scale
- Latest analysis month: September 2026

## 3. Latest Month Performance

| Metric | Result |
|---|---:|
| Opening MRR | $64,181 |
| Closing MRR | $66,219 |
| Closing ARR | $794,628 |
| Net MRR movement | $2,038 |
| Monthly MRR growth | 3.18% |
| Net Revenue Retention | 96.69% |
| Gross Revenue Retention | 93.73% |
| SaaS Quick Ratio | 1.51x |
| Opening customers | 609 |
| Active customers | 621 |
| Churned customers | 28 |
| Customer churn rate | 4.60% |
| Customer retention rate | 95.40% |
| Revenue churn rate | 5.10% |

## 4. Revenue Retention Analysis

Net Revenue Retention of 96.69% indicates that the existing customer base experienced a net revenue decline of 3.31%.

Gross Revenue Retention of 93.73% indicates that contraction and churn reduced opening recurring revenue by approximately 6.27% before expansion.

The SaaS Quick Ratio of 1.51 indicates that revenue gains exceeded revenue losses during the latest month.

Existing customer revenue movement:

- Expansion MRR: +$1,900
- Contraction MRR: -$750
- Churn MRR: -$3,272
- Net existing customer movement: -$2,122

New customer MRR of $4,160 compensated for this decline, resulting in positive overall MRR growth.

## 5. Cohort Analysis

Customers were grouped according to their first active subscription month.

Customer retention measures the percentage of original cohort customers active in subsequent months.

Revenue retention measures subsequent cohort MRR relative to initial cohort MRR.

Validation results:

- Total cohorts: 21
- Customers per acquisition cohort: 40
- Customer cohort periods: 231
- Revenue cohort periods: 231
- Maximum cohort age: 20 months
- Month-zero retention: 100%
- Duplicate cohort periods: 0
- Revenue cohort periods above 100% retention: 110

Revenue retention can exceed 100% when expansion and returning customer revenue outweigh revenue losses relative to the initial cohort MRR.

Unobserved future cohort periods are treated as unavailable rather than zero.

## 6. Subscription Plan Analysis

| Plan | Customers | MRR | Revenue Share |
|---|---:|---:|---:|
| Starter | 278 | $8,062 | 12.17% |
| Growth | 222 | $21,978 | 33.19% |
| Scale | 121 | $36,179 | 54.64% |
| Total | 621 | $66,219 | 100% |

Scale contributes the largest share of recurring revenue despite representing only 19.48% of active customers.

The Growth plan recorded the highest latest-month customer churn rate at 5.43%.

Plan movement analysis covers 20 monthly transitions across three subscription plans.

## 7. Independent Validation

SQL results were independently reconciled using Python and pandas.

| Validation | Result |
|---|---|
| Months compared | 21 |
| Metrics compared per month | 15 |
| Total monthly values compared | 315 |
| Total mismatches | 0 |
| Customer cohort counts | PASS |
| Revenue cohort MRR | PASS |
| Plan customer counts | PASS |
| Plan MRR | PASS |

Overall retention reconciliation: PASS.

## 8. Exported Analytical Tables

| File | Rows |
|---|---:|
| monthly_retention_metrics.csv | 21 |
| customer_cohorts.csv | 840 |
| customer_retention_cohorts.csv | 231 |
| revenue_retention_cohorts.csv | 231 |
| plan_revenue_analysis.csv | 63 |
| plan_movement_analysis.csv | 60 |
| Total | 1,446 |

All six CSV files passed read-back validation.

These tables are available for subsequent Excel and Power BI reporting.

## 9. Business Recommendations

1. Prioritize existing customer retention to improve NRR.
2. Investigate cancellation reasons to reduce churn-related revenue losses.
3. Review Growth plan customer experience and retention opportunities.
4. Protect high-value Scale customer relationships to manage revenue concentration risk.
5. Test customer win-back campaigns to improve reactivation.
6. Monitor the SaaS Quick Ratio alongside revenue retention and acquisition performance.

## 10. Limitations

- All billing and customer records are synthetic.
- Simulation parameters do not represent verified real-world SaaS benchmarks.
- The actual latest-month MRR growth is 3.18%, compared with the originally intended scenario of approximately 4%.
- Undefined ratios are reported as unavailable rather than zero.
- Business recommendations are hypotheses derived from simulated findings, not proven intervention outcomes.

## 11. Conclusion

The company demonstrates positive overall recurring revenue growth but declining revenue from its existing customer base.

New customer acquisition compensates for losses caused by contraction and churn. Improving customer retention, reducing revenue leakage and protecting high-value subscription relationships should therefore be considered strategic priorities.

The analytical results have passed the documented validation checks and are ready for dashboard development.

**Phase 04 analytical validation status: PASS.**