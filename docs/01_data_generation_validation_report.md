# Phase 1 — Data Generation and Validation Report

## 1. Objective

Generate a reproducible synthetic SaaS subscription dataset, validate its quality, load it into SQLite, and independently reconcile SQL and pandas results.

## 2. Dataset Overview

| Attribute | Value |
|---|---|
| Data source | Synthetic simulation |
| Random seed | 42 |
| Start month | January 2025 |
| End month | September 2026 |
| Total months | 21 |
| Total billing records | 7,623 |
| Unique customers | 840 |
| Total columns | 4 |
| Currency | USD |
| Granularity | One active customer per month |

## 3. Simulation Parameters

| Parameter | Configured target |
|---|---|
| New customers per month | 40 |
| Monthly churn probability | 3.5% |
| Monthly upgrade probability | 4% |
| Monthly downgrade probability | 2% |
| Monthly reactivation probability | 1–2% |

Observed movement rates may differ from configured probabilities because of randomness and plan eligibility.

### Subscription Plans

| Plan | Monthly price |
|---|---:|
| Starter | $29 |
| Growth | $99 |
| Scale | $299 |

## 4. Data Dictionary

| Column | Data type | Description |
|---|---|---|
| month | Text | Billing month in YYYY-MM format |
| customer_id | Text | Unique customer identifier |
| plan | Text | Active subscription plan |
| mrr | Integer | Monthly recurring revenue in USD |

The combination of month and customer_id uniquely identifies each billing record.

## 5. Data Quality Validation

| Validation check | Result | Status |
|---|---:|---|
| Missing values | 0 | PASS |
| Exact duplicate rows | 0 | PASS |
| Duplicate customer-month records | 0 | PASS |
| Invalid subscription plans | 0 | PASS |
| MRR price mismatches | 0 | PASS |
| Non-positive MRR | 0 | PASS |
| Invalid customer IDs | 0 | PASS |
| Missing calendar months | 0 | PASS |
| Unexpected calendar months | 0 | PASS |

### Row Count Audit

| Stage | Records |
|---|---:|
| Original dataset | 7,623 |
| Rows removed | 0 |
| Final validated dataset | 7,623 |

No cleaning or deletion was required based on the validation checks performed. The raw dataset was preserved.

## 6. Customer Movement Verification

| Movement | Event count |
|---|---:|
| New | 840 |
| Expansion | 244 |
| Contraction | 64 |
| Churn | 235 |
| Reactivation | 16 |
| Unchanged | 6,459 |

All five required revenue movement categories are present.

### Customer Reconciliation

Final active customers:

840 - 235 + 16 = 621

Active customer-month records:

840 + 244 + 64 + 16 + 6,459 = 7,623

Both reconciliation checks passed.

Movement counts represent events rather than revenue amounts or distinct customers within each category.

## 7. SQLite Database

- SQLite version: 3.50.4
- Database: `data/processed/saas_revenue.db`
- Table: `saas_billing`
- Composite primary key: month, customer_id
- NOT NULL constraints on all columns
- CHECK constraint for valid plan-price combinations
- Transactional data insertion

### Loading Results

| Metric | Result |
|---|---:|
| CSV records | 7,623 |
| Database rows before loading | 0 |
| Database rows after loading | 7,623 |
| Rows inserted | 7,623 |
| Row count difference | 0 |

Database loading and row count reconciliation passed.

## 8. Subscription Plan Profiling

| Plan | Billing records | Unique customers | Cumulative recurring revenue |
|---|---:|---:|---:|
| Scale | 1,247 | 183 | $372,853 |
| Growth | 2,721 | 415 | $269,379 |
| Starter | 3,655 | 523 | $105,995 |
| Total | 7,623 | 840 distinct | $748,227 |

Unique customer counts across plans are not additive because customers can change subscription plans.

Cumulative recurring revenue represents the sum of monthly recurring revenue across the observation period, not a single month's MRR.

## 9. Preliminary Business Results

| Metric | Verified result |
|---|---:|
| August 2026 active customers | 609 |
| September 2026 active customers | 621 |
| August 2026 MRR | $64,181 |
| September 2026 MRR | $66,219 |
| September 2026 ARR | $794,628 |
| Net monthly MRR increase | $2,038 |
| Final-month MRR growth | 3.18% |

The original approximately 4% growth figure was a target scenario. The actual simulated growth was 3.18%.

The dataset was not adjusted to force the target result.

## 10. SQL and Pandas Reconciliation

| Validation | Result |
|---|---|
| Monthly coverage | 21 months |
| Active customer differences | All zero |
| Monthly MRR differences | All zero |
| ARR differences | All zero |
| Individual billing records match | True |
| Overall reconciliation | PASS |

SQL and pandas independently produced identical monthly metrics.

All 7,623 individual billing records matched between the original CSV and SQLite database.

## 11. Reproducibility

The following files support reproducible data generation, validation and profiling:

- `src/generate_saas_data.py`
- `src/validate_saas_data.py`
- `src/create_database.py`
- `src/load_saas_data.py`
- `src/run_sql_profiling.py`
- `src/reconcile_sql_pandas.py`
- `sql/01_data_profiling.sql`
- `data/raw/saas_billing.csv`
- `assumptions.md`

## 12. Limitations

- All customer records are synthetic.
- Results do not represent an actual SaaS company.
- Subscription prices represent monthly-equivalent recurring revenue.
- Annual invoices, one-time fees and usage overages are not simulated separately.
- Observed movement rates may differ from configured probabilities.
- Churn after September 2026 cannot be observed.
- Revenue movement amounts and retention metrics have not yet been calculated.
- ARR represents annualized recurring revenue, not guaranteed future revenue.

## 13. Conclusion

The synthetic billing dataset passed structural validation, business-rule validation, movement verification, database loading checks, and independent SQL and pandas reconciliation.

The dataset is ready for Phase 2: SQL Revenue Movement Classification.