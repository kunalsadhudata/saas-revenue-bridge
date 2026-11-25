import sqlite3
from pathlib import Path

import pandas as pd


# Load the original billing dataset
billing = pd.read_csv("data/raw/saas_billing.csv")

billing["month"] = pd.PeriodIndex(
    billing["month"], freq="M"
)

# Create a complete monthly calendar
months = pd.period_range(
    billing["month"].min(),
    billing["month"].max(),
    freq="M"
)

# Create customer-month MRR matrix
mrr_matrix = billing.pivot(
    index="customer_id",
    columns="month",
    values="mrr"
).reindex(columns=months).fillna(0)

# Independently classify customer movements
records = []

for customer_id, row in mrr_matrix.iterrows():

    previous_mrr = 0
    previously_active = False

    for month, current_mrr in row.items():

        if previous_mrr == 0 and current_mrr == 0:
            continue

        if previous_mrr == 0 and current_mrr > 0:
            movement = (
                "Reactivation"
                if previously_active
                else "New"
            )

        elif previous_mrr > 0 and current_mrr == 0:
            movement = "Churn"

        elif current_mrr > previous_mrr:
            movement = "Expansion"

        elif current_mrr < previous_mrr:
            movement = "Contraction"

        else:
            movement = "Unchanged"

        records.append({
            "month": str(month),
            "customer_id": customer_id,
            "movement_type": movement,
            "previous_mrr": previous_mrr,
            "current_mrr": current_mrr,
            "signed_mrr": current_mrr - previous_mrr
        })

        if current_mrr > 0:
            previously_active = True

        previous_mrr = current_mrr


# Convert movement records into a DataFrame
movements = pd.DataFrame(records)

# Aggregate Python results
python_summary = movements.groupby(
    "movement_type"
).agg(
    event_count=("customer_id", "count"),
    total_previous_mrr=("previous_mrr", "sum"),
    total_current_mrr=("current_mrr", "sum"),
    signed_mrr=("signed_mrr", "sum")
).reset_index()

# Load SQL results
sql_query = Path(
    "sql/02_combined_movements.sql"
).read_text(encoding="utf-8")

with sqlite3.connect(
    "data/processed/saas_revenue.db"
) as conn:
    sql_summary = pd.read_sql_query(sql_query, conn)

# Sort results consistently
python_summary = python_summary.sort_values(
    "movement_type"
).reset_index(drop=True)

sql_summary = sql_summary.sort_values(
    "movement_type"
).reset_index(drop=True)

print("\n========== PYTHON MOVEMENT SUMMARY ==========")
print(python_summary.to_string(index=False))

print("\n========== SQL MOVEMENT SUMMARY ==========")
print(sql_summary.to_string(index=False))

# Compare SQL and Python results
pd.testing.assert_frame_equal(
    python_summary,
    sql_summary,
    check_dtype=False
)

print("\n========== RECONCILIATION ==========")
print("SQL and Python reconciliation: PASSED")
print(f"Total movement records: {len(movements):,}")
print(f"Net MRR movement: ${movements['signed_mrr'].sum():,.0f}")


# Reconcile individual customer-month records
detail_query = Path(
    "sql/02_movement_detail.sql"
).read_text(encoding="utf-8")

with sqlite3.connect(
    "data/processed/saas_revenue.db"
) as conn:
    sql_detail = pd.read_sql_query(detail_query, conn)

python_detail = movements.sort_values(
    ["customer_id", "month"]
).reset_index(drop=True)

sql_detail = sql_detail.sort_values(
    ["customer_id", "month"]
).reset_index(drop=True)

pd.testing.assert_frame_equal(
    python_detail,
    sql_detail,
    check_dtype=False,
    check_exact=True
)

print("\n========== ROW-LEVEL RECONCILIATION ==========")
print("Customer-month reconciliation: PASSED")
print(f"Matched records: {len(sql_detail):,}")


# Export validated datasets
output_dir = Path("outputs/tables")
output_dir.mkdir(parents=True, exist_ok=True)

detail_path = output_dir / "customer_movements.csv"
summary_path = output_dir / "movement_summary.csv"

sql_detail.to_csv(detail_path, index=False)
sql_summary.to_csv(summary_path, index=False)

# Verify exported files
exported_detail = pd.read_csv(detail_path)
exported_summary = pd.read_csv(summary_path)

pd.testing.assert_frame_equal(
    sql_detail,
    exported_detail,
    check_dtype=False,
    check_exact=True
)

pd.testing.assert_frame_equal(
    sql_summary,
    exported_summary,
    check_dtype=False,
    check_exact=True
)

print("\n========== EXPORT VALIDATION ==========")
print(f"Created: {detail_path}")
print(f"Created: {summary_path}")
print(f"Movement records: {len(exported_detail):,}")
print(f"Summary records: {len(exported_summary):,}")
print("CSV read-back validation: PASSED")