import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

# Load original simulated billing data
billing = pd.read_csv("data/raw/saas_billing.csv")

months = sorted(billing["month"].unique())
seen_customers = set()
previous = pd.Series(dtype=float)
records = []

# Independently calculate monthly metrics
for month in months:

    current = (
        billing[billing["month"] == month]
        .set_index("customer_id")["mrr"]
    )

    opening_mrr = previous.sum()
    opening_customers = len(previous)

    retained = previous.index.intersection(current.index)
    churned = previous.index.difference(current.index)
    arrivals = current.index.difference(previous.index)

    new = [c for c in arrivals if c not in seen_customers]
    reactivated = [c for c in arrivals if c in seen_customers]

    changes = current.loc[retained] - previous.loc[retained]

    new_mrr = current.loc[new].sum()
    reactivation_mrr = current.loc[reactivated].sum()

    expansion_mrr = changes[changes > 0].sum()
    contraction_mrr = changes[changes < 0].sum()
    churn_mrr = -previous.loc[churned].sum()

    losses = abs(contraction_mrr) + abs(churn_mrr)

    def safe_divide(numerator, denominator):
        return numerator / denominator if denominator else np.nan

    records.append({
        "month": month,
        "opening_customers": opening_customers,
        "active_customers": len(current),
        "churned_customers": len(churned),
        "opening_mrr": opening_mrr,
        "new_mrr": new_mrr,
        "expansion_mrr": expansion_mrr,
        "contraction_mrr": contraction_mrr,
        "churn_mrr": churn_mrr,
        "reactivation_mrr": reactivation_mrr,

        "nrr_pct": 100 * safe_divide(
            opening_mrr + expansion_mrr
            + contraction_mrr + churn_mrr,
            opening_mrr
        ),

        "grr_pct": 100 * safe_divide(
            opening_mrr + contraction_mrr + churn_mrr,
            opening_mrr
        ),

        "quick_ratio": safe_divide(
            new_mrr + expansion_mrr + reactivation_mrr,
            losses
        ),

        "customer_churn_rate_pct": 100 * safe_divide(
            len(churned), opening_customers
        ),

        "customer_retention_rate_pct": 100 * safe_divide(
            len(retained), opening_customers
        ),

        "revenue_churn_rate_pct": 100 * safe_divide(
            abs(churn_mrr), opening_mrr
        )
    })

    seen_customers.update(current.index)
    previous = current.copy()

python_results = pd.DataFrame(records)

# Load SQL queries
movement_sql = Path(
    "sql/02_movement_detail.sql"
).read_text(encoding="utf-8").strip().rstrip(";")

bridge_sql = Path(
    "sql/03_monthly_mrr_bridge.sql"
).read_text(encoding="utf-8").strip().rstrip(";")

retention_sql = Path(
    "sql/04_retention_metrics.sql"
).read_text(encoding="utf-8")

# Execute SQL using the same connection
with sqlite3.connect("data/processed/saas_revenue.db") as conn:

    conn.execute(
        f"CREATE TEMP VIEW movement_detail AS {movement_sql}"
    )

    conn.execute(
        f"CREATE TEMP VIEW monthly_mrr_bridge AS {bridge_sql}"
    )

    sql_results = pd.read_sql_query(retention_sql, conn)

# Align results
python_results = python_results.set_index("month").sort_index()
sql_results = sql_results.set_index("month").sort_index()

assert python_results.index.equals(sql_results.index)

metrics = python_results.columns.tolist()

print("INDEPENDENT RETENTION METRICS VALIDATION")
print("-" * 60)

total_mismatches = 0

for metric in metrics:

    matches = np.isclose(
        python_results[metric],
        sql_results[metric],
        rtol=0,
        atol=1e-9,
        equal_nan=True
    )

    mismatches = int((~matches).sum())
    total_mismatches += mismatches

    status = "PASS" if mismatches == 0 else "FAIL"

    print(f"{metric:35} {status}")

print("\nVALIDATION SUMMARY")
print("Total months:", len(python_results))
print("Metrics compared:", len(metrics))
print("Total values compared:", len(metrics) * len(python_results))
print("Total mismatches:", total_mismatches)

print("\nLATEST MONTH - PANDAS RESULTS")
print(python_results.tail(1).T.round(2))

assert total_mismatches == 0, "Reconciliation failed"

print("\nOverall retention reconciliation: PASS")

# Independent cohort and plan validation

billing["cohort_month"] = (
    billing.groupby("customer_id")["month"]
    .transform("min")
)

billing["cohort_age"] = (
    pd.PeriodIndex(billing["month"], freq="M").asi8
    - pd.PeriodIndex(billing["cohort_month"], freq="M").asi8
)

cohort = (
    billing.groupby(["cohort_month", "cohort_age"])
    .agg(
        customers=("customer_id", "nunique"),
        revenue=("mrr", "sum")
    )
)

grid = pd.MultiIndex.from_tuples(
    [
        (month, age)
        for i, month in enumerate(months)
        for age in range(len(months) - i)
    ],
    names=["cohort_month", "cohort_age"]
)

cohort = cohort.reindex(grid, fill_value=0)

plan = (
    billing.groupby(["month", "plan"])
    .agg(
        active_customers=("customer_id", "nunique"),
        plan_mrr=("mrr", "sum")
    )
    .sort_index()
)

with sqlite3.connect("data/processed/saas_revenue.db") as conn:

    def load_sql(filename):
        query = Path("sql", filename).read_text(
            encoding="utf-8"
        )
        return pd.read_sql_query(query, conn)

    customer_sql = load_sql(
        "04_customer_retention_cohorts.sql"
    ).set_index(["cohort_month", "cohort_age"]).sort_index()

    revenue_sql = load_sql(
        "04_revenue_retention_cohorts.sql"
    ).set_index(["cohort_month", "cohort_age"]).sort_index()

    plan_sql = load_sql(
        "04_plan_revenue_analysis.sql"
    ).set_index(["month", "plan"]).sort_index()

assert cohort.index.equals(customer_sql.index)
assert cohort.index.equals(revenue_sql.index)
assert plan.index.equals(plan_sql.index)

np.testing.assert_allclose(
    cohort["customers"],
    customer_sql["active_customers"]
)

np.testing.assert_allclose(
    cohort["revenue"],
    revenue_sql["current_cohort_mrr"]
)

np.testing.assert_allclose(
    plan["active_customers"],
    plan_sql["active_customers"]
)

np.testing.assert_allclose(
    plan["plan_mrr"],
    plan_sql["plan_mrr"]
)

print("\nCOHORT AND PLAN VALIDATION")
print("-" * 50)
print("Customer cohort periods:", len(cohort))
print("Revenue cohort periods:", len(cohort))
print("Plan-month records:", len(plan))
print("Customer cohort counts: PASS")
print("Revenue cohort MRR: PASS")
print("Plan customer counts: PASS")
print("Plan MRR: PASS")

