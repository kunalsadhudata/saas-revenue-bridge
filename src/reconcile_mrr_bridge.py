import pandas as pd
from pathlib import Path

# Step 03.15: Independent pandas calculation

ROOT = Path(__file__).resolve().parents[1]

billing = pd.read_csv(
    ROOT / "data/raw/saas_billing.csv"
)

movements = pd.read_csv(
    ROOT / "outputs/tables/customer_movements.csv"
)

# Calculate monthly billing balances
monthly = (
    billing.groupby("month")
    .agg(
        active_customers=("customer_id", "nunique"),
        actual_closing_mrr=("mrr", "sum")
    )
    .sort_index()
)

monthly["opening_mrr"] = (
    monthly["actual_closing_mrr"]
    .shift(1, fill_value=0)
)

# Aggregate customer movements
movement_types = [
    "New",
    "Expansion",
    "Contraction",
    "Churn",
    "Reactivation"
]

movement_pivot = movements.pivot_table(
    index="month",
    columns="movement_type",
    values="signed_mrr",
    aggfunc="sum",
    fill_value=0
)

movement_pivot = movement_pivot.reindex(
    columns=movement_types,
    fill_value=0
)

movement_pivot.columns = [
    name.lower() + "_mrr"
    for name in movement_types
]

# Combine billing balances and movements
bridge = monthly.join(movement_pivot)

movement_columns = movement_pivot.columns.tolist()

bridge[movement_columns] = (
    bridge[movement_columns].fillna(0)
)

bridge["net_mrr_movement"] = (
    bridge[movement_columns].sum(axis=1)
)

bridge["calculated_closing_mrr"] = (
    bridge["opening_mrr"]
    + bridge["net_mrr_movement"]
)

bridge["mrr_difference"] = (
    bridge["calculated_closing_mrr"]
    - bridge["actual_closing_mrr"]
)

bridge = bridge.reset_index()

print("\nINDEPENDENT PANDAS MRR BRIDGE")
print("-" * 50)

print(bridge.to_string(index=False))

print("\nTotal months:", len(bridge))

print(
    "Latest closing MRR:",
    bridge.iloc[-1]["calculated_closing_mrr"]
)

print(
    "Latest net MRR movement:",
    bridge.iloc[-1]["net_mrr_movement"]
)

print(
    "Maximum absolute difference:",
    bridge["mrr_difference"].abs().max()
)

print(
    "Pandas tie-out valid:",
    bridge["mrr_difference"].eq(0).all()
)


# Step 03.16: SQL and pandas reconciliation

import sqlite3

# Load SQL bridge results

movement_sql = (
    ROOT / "sql/02_movement_detail.sql"
).read_text(encoding="utf-8").strip().rstrip(";")

with sqlite3.connect(
    ROOT / "data/processed/saas_revenue.db"
) as conn:

    conn.execute(
        f"CREATE TEMP VIEW movement_detail AS {movement_sql}"
    )

    sql_query = (
        ROOT / "sql/03_monthly_mrr_bridge.sql"
    ).read_text(encoding="utf-8")

    sql_bridge = pd.read_sql_query(sql_query, conn)
    
# Metrics to compare
compare_columns = [
    "active_customers",
    "opening_mrr",
    "new_mrr",
    "expansion_mrr",
    "contraction_mrr",
    "churn_mrr",
    "reactivation_mrr",
    "net_mrr_movement",
    "actual_closing_mrr",
    "calculated_closing_mrr"
]

sql_bridge["calculated_closing_mrr"] = (
    sql_bridge["opening_mrr"]
    + sql_bridge["net_mrr_movement"]
)

# Align both results by month
sql_check = (
    sql_bridge.set_index("month")
    .sort_index()[compare_columns]
)

pandas_check = (
    bridge.set_index("month")
    .sort_index()[compare_columns]
)

# Validate month coverage
months_match = (
    sql_check.index.is_unique
    and pandas_check.index.is_unique
    and sql_check.index.equals(pandas_check.index)
    and len(sql_check) == 21
)

if not months_match:
    raise ValueError("Month coverage mismatch.")

# Compare all metric values
differences = sql_check - pandas_check

mismatch_count = int(differences.ne(0).sum().sum())

max_difference = differences.abs().max().max()

reconciliation_passed = (
    months_match
    and mismatch_count == 0
)

print("\nSQL VS PANDAS RECONCILIATION")
print("-" * 50)

print("Month coverage matches:", months_match)
print("Months compared:", len(sql_check))
print("Metrics compared:", len(compare_columns))
print("Total values compared:", differences.size)

print("\nMaximum difference by metric:")
print(differences.abs().max().to_string())

print("\nTotal mismatches:", mismatch_count)
print("Maximum absolute difference:", max_difference)

print(
    "Overall reconciliation:",
    "PASS" if reconciliation_passed else "FAIL"
)

if not reconciliation_passed:
    raise ValueError("SQL and pandas reconciliation failed.")