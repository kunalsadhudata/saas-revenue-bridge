# Phase 02 — Customer Movement Classification

## 1. Objective

Classify customer-level monthly recurring revenue (MRR) movements using SQLite and independently validate the results using Python and pandas.

This phase establishes the foundation for monthly MRR and ARR revenue bridge analysis.

## 2. Dataset

- Data source: Simulated SaaS billing dataset
- Observation period: January 2025 to September 2026
- Total observation months: 21
- Original billing records: 7,623
- Subscription plans:
  - Starter: $29/month
  - Growth: $99/month
  - Scale: $299/month
- Currency: USD

The dataset is simulated for educational and portfolio purposes and does not represent an actual SaaS company.

## 3. Customer Movement Definitions

| Movement | Business definition |
|---|---|
| New | Customer becomes active for the first time |
| Expansion | Active customer increases MRR compared with the previous calendar month |
| Contraction | Active customer decreases MRR compared with the previous calendar month |
| Churn | Previously active customer becomes inactive |
| Reactivation | Previously churned customer becomes active again |
| Unchanged | Customer remains active with no MRR change |

## 4. SQL Methodology

The SQLite implementation uses:

- Common Table Expressions (CTEs)
- Calendar month indexing
- ROW_NUMBER() window function
- LAG() window function
- Calendar month gap detection
- CASE expressions for movement classification
- NOT EXISTS for churn detection
- UNION ALL for combining movement records
- Aggregate functions for movement summaries

Calendar month gaps distinguish continuous subscriptions from returning customers.

Churn events are generated for the first inactive month following an active month. Events beyond the final observation month are excluded to prevent false churn.

## 5. Signed MRR Calculation

Signed MRR is calculated as:

Signed MRR = Current MRR - Previous MRR

Positive values represent revenue gains, negative values represent revenue losses, and zero represents unchanged recurring revenue.

For New and Reactivation events, previous calendar-month MRR is zero.

For Churn events, current calendar-month MRR is zero.

## 6. Customer Movement Results

| Movement | Event count | Previous MRR ($) | Current MRR ($) | Signed MRR ($) |
|---|---:|---:|---:|---:|
| New | 840 | 0 | 68,780 | 68,780 |
| Expansion | 244 | 13,096 | 41,356 | 28,260 |
| Contraction | 64 | 11,136 | 3,536 | -7,600 |
| Churn | 235 | 25,325 | 0 | -25,325 |
| Reactivation | 16 | 0 | 2,104 | 2,104 |
| Unchanged | 6,459 | 632,451 | 632,451 | 0 |
| Total | 7,858 | 682,008 | 748,227 | 66,219 |

These results represent cumulative movements across the complete observation period, not a single month's revenue bridge.

Event counts represent customer-month events rather than necessarily distinct customers.

## 7. Data Quality Validation

| Validation check | Result |
|---|---:|
| Original billing records | 7,623 |
| Generated churn events | 235 |
| Combined movement records | 7,858 |
| Unique customer-month records | 7,858 |
| Duplicate customer-month records | 0 |
| Invalid classifications | 0 |
| Revenue-condition rule violations | 0 |
| Out-of-period events | 0 |

Validation status: PASSED.

## 8. Independent Python Reconciliation

An independent Python implementation was developed using pandas.

The Python methodology:

1. Creates a complete monthly calendar.
2. Constructs a customer-month MRR matrix.
3. Represents inactive customer months using zero MRR.
4. Tracks historical customer activity.
5. Independently classifies customer movements.
6. Calculates signed MRR amounts.
7. Compares results against SQLite.

### Reconciliation Results

- Category-level reconciliation: PASSED
- Customer-month row-level reconciliation: PASSED
- Matched movement records: 7,858
- Row-level discrepancies: 0
- Net MRR movement: $66,219

All exported records were independently reconciled before export.

## 9. Preliminary Business Insights

### Revenue gains

- New MRR: $68,780
- Expansion MRR: $28,260
- Reactivation MRR: $2,104
- Total positive MRR movements: $99,144

### Revenue losses

- Contraction MRR: $7,600
- Churn MRR: $25,325
- Total negative MRR movements: $32,925

### Net MRR movement

$99,144 - $32,925 = $66,219

### Existing customer base movement

Existing base movement excludes New and Reactivation MRR.

$28,260 - $7,600 - $25,325 = -$4,665

Across the observation period, expansion revenue was insufficient to offset contraction and churn losses.

New customer acquisition and reactivation compensated for the negative cumulative movement from the existing customer base.

Monthly analysis is required before drawing conclusions about the latest month's performance.

## 10. Generated Files

### SQL

- sql/02_customer_movement_classification.sql
- sql/02_churn_detection.sql
- sql/02_combined_movements.sql
- sql/02_movement_validation.sql
- sql/02_movement_detail.sql

### Python

- src/run_movement_classification.py
- src/reconcile_movements.py

### Output datasets

- outputs/tables/customer_movements.csv
- outputs/tables/movement_summary.csv

Both CSV files passed read-back validation.

## 11. Reproducibility

Run the following commands from the project root:

```bash
python src/run_movement_classification.py
python src/reconcile_movements.py
```

## 12. Assumptions and Limitations

- The billing dataset is simulated.
- Missing customer-month billing records represent inactive subscriptions.
- The observation period is assumed to begin before existing subscription history.
- Churn is measured using monthly subscription snapshots.
- No churn events are inferred beyond the observation period.
- Results are cumulative across 21 months.
- Monthly revenue bridge reconciliation and retention metrics are not yet calculated.

## 13. Phase Completion Status

- Customer movement classification: Completed
- Signed MRR calculations: Completed
- SQL validation: Passed
- Independent Python reconciliation: Passed
- Row-level reconciliation: Passed
- CSV export and read-back validation: Passed

Phase 02 analytical work is complete.

The validated movement datasets are ready for monthly MRR and ARR revenue bridge calculations in Phase 03.