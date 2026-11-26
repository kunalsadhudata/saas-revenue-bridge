# Phase 03 — MRR Bridge and Tie-Out Validation

## 1. Objective

Build a monthly recurring revenue bridge that explains changes in MRR through New, Expansion, Contraction, Churn and Reactivation movements.

Determine whether revenue growth is driven by customer acquisition or growth within the existing customer base.

## 2. Dataset Scope

| Attribute | Value |
|---|---|
| Data source | Synthetic billing simulation |
| Start month | January 2025 |
| End month | September 2026 |
| Total months | 21 |
| Initial opening MRR | $0 |
| Currency | USD |

## 3. Methodology

The monthly MRR bridge was constructed using SQLite and independently reproduced using Python and pandas.

The process included:

- Creating a continuous monthly calendar.
- Aggregating monthly billing records.
- Calculating opening MRR using the SQL LAG function.
- Aggregating customer-level revenue movements.
- Calculating net MRR movement.
- Reconciling calculated closing MRR against billing-derived closing MRR.
- Calculating ARR and monthly growth rates.
- Measuring existing-base revenue growth.
- Comparing SQL and pandas results.

## 4. Revenue Formulas

```text
Net MRR Movement =
    New MRR
    + Expansion MRR
    + Contraction MRR
    + Churn MRR
    + Reactivation MRR

Calculated Closing MRR =
    Opening MRR + Net MRR Movement

ARR = MRR × 12

MRR Growth (%) =
    (Net MRR Movement / Opening MRR) × 100

Existing-Base Net MRR =
    Expansion MRR + Contraction MRR + Churn MRR

Existing-Base Growth (%) =
    (Existing-Base Net MRR / Opening MRR) × 100
```

Contraction and Churn are stored as negative values. Growth rates are undefined when opening MRR is zero.

## 5. Monthly Tie-Out Validation

| Validation metric | Result |
|---|---:|
| Total months | 21 |
| Matched months | 21 |
| Failed months | 0 |
| Maximum absolute MRR difference | 0 |
| Overall tie-out status | PASS |

Calculated closing MRR matches billing-derived closing MRR for every month.

## 6. SQL and Pandas Reconciliation

| Validation metric | Result |
|---|---:|
| Month coverage matches | True |
| Months compared | 21 |
| Metrics compared | 10 |
| Total values compared | 210 |
| Total mismatches | 0 |
| Maximum absolute difference | 0 |
| Overall reconciliation | PASS |

Both implementations produced identical results across all compared metrics.

## 7. Cumulative Revenue Movements

| Movement type | Signed MRR (USD) |
|---|---:|
| New | +68,780 |
| Expansion | +28,260 |
| Contraction | -7,600 |
| Churn | -25,325 |
| Reactivation | +2,104 |
| Net cumulative movement | +66,219 |

## 8. Latest-Month Revenue Bridge

Reporting month: September 2026.

| Metric | Value |
|---|---:|
| Active customers | 621 |
| Opening MRR | $64,181 |
| New MRR | +$4,160 |
| Expansion MRR | +$1,900 |
| Contraction MRR | -$750 |
| Churn MRR | -$3,272 |
| Reactivation MRR | $0 |
| Net MRR movement | +$2,038 |
| Closing MRR | $66,219 |
| Opening ARR | $770,172 |
| Closing ARR | $794,628 |
| Net ARR movement | +$24,456 |
| Monthly MRR growth | +3.18% |
| Existing-base net MRR | -$2,122 |
| Existing-base growth | -3.31% |

## 9. Key Business Findings

Overall MRR increased by 3.18% in September 2026. However, revenue from the existing customer base declined by 3.31%.

New customers contributed $4,160 in additional MRR, offsetting the $2,122 net revenue loss from existing customers.

Churn was the largest negative revenue movement, contributing a loss of $3,272.

Without new customer acquisition, MRR would have declined during the reporting month.

The business should investigate customer retention, cancellation drivers and downgrade patterns to improve sustainable recurring revenue growth.

## 10. Export Validation

| Validation metric | Result |
|---|---|
| Exported file | monthly_mrr_bridge.csv |
| Total rows | 21 |
| Unique months | 21 |
| Maximum absolute MRR difference | 0 |
| CSV read-back validation | PASS |

## 11. Deliverables

- `sql/03_monthly_mrr_bridge.sql`
- `src/run_mrr_bridge.py`
- `src/reconcile_mrr_bridge.py`
- `outputs/tables/monthly_mrr_bridge.csv`
- `docs/03_mrr_bridge_validation_report.md`

## 12. Limitations

- The dataset is simulated and does not represent a real company.
- The original business scenario assumed approximately 4% MRR growth, whereas the generated dataset produced 3.18%.
- ARR represents annualized recurring revenue, not realized annual revenue.
- Revenue movements are measured using monthly billing snapshots.
- Business recommendations are illustrative and require real customer data for implementation.

## 13. Conclusion

The monthly MRR bridge was successfully constructed and validated across all 21 months. SQL and pandas reconciliation produced zero mismatches across 210 compared values.

The latest-month analysis demonstrates that positive overall revenue growth can conceal declining revenue within the existing customer base.

**Phase 03 analytical validation status: PASS.**