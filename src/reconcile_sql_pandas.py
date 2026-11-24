import sqlite3
import pandas as pd
from pathlib import Path

# Locate project files
project_root = Path(__file__).resolve().parent.parent

csv_path = project_root / "data/raw/saas_billing.csv"
db_path = project_root / "data/processed/saas_revenue.db"

# Read raw dataset
df = pd.read_csv(csv_path)

# Calculate monthly metrics independently
pandas_monthly = (
    df.groupby("month")
    .agg(
        active_customers=("customer_id", "nunique"),
        monthly_mrr=("mrr", "sum")
    )
    .reset_index()
)

pandas_monthly["arr"] = pandas_monthly["monthly_mrr"] * 12

print("========== PANDAS MONTHLY PROFILE ==========")
print(pandas_monthly.to_string(index=False))

# Connect to SQLite in read-only mode
conn = sqlite3.connect(
    db_path.as_uri() + "?mode=ro",
    uri=True
)

try:
    sql_monthly = pd.read_sql_query("""
        SELECT
            month,
            COUNT(DISTINCT customer_id) AS active_customers,
            SUM(mrr) AS monthly_mrr,
            SUM(mrr) * 12 AS arr
        FROM saas_billing
        GROUP BY month
        ORDER BY month;
    """, conn)

    sql_raw = pd.read_sql_query("""
        SELECT month, customer_id, plan, mrr
        FROM saas_billing;
    """, conn)

finally:
    conn.close()

 # Compare monthly results
comparison = pandas_monthly.merge(
    sql_monthly,
    on="month",
    how="outer",
    suffixes=("_pandas", "_sql"),
    validate="one_to_one",
    indicator=True
)

metrics = ["active_customers", "monthly_mrr", "arr"]

for metric in metrics:
    comparison[f"{metric}_difference"] = (
        comparison[f"{metric}_pandas"]
        - comparison[f"{metric}_sql"]
    )

difference_columns = [
    f"{metric}_difference"
    for metric in metrics
]

print("\n========== MONTHLY RECONCILIATION ==========")

print(
    comparison[["month"] + difference_columns]
    .to_string(index=False)
)

all_match = (
    len(comparison) == 21
    and comparison["_merge"].eq("both").all()
    and comparison[difference_columns].eq(0).all().all()
)

print("\nAll monthly metrics match:", all_match)

# Compare complete CSV and SQLite records
keys = ["month", "customer_id"]

csv_sorted = df.sort_values(keys).reset_index(drop=True)
sql_sorted = sql_raw.sort_values(keys).reset_index(drop=True)

raw_match = csv_sorted.equals(sql_sorted)

print("\n========== RECORD-LEVEL RECONCILIATION ==========")

print("CSV records:", len(csv_sorted))
print("SQLite records:", len(sql_sorted))
print("All individual records match:", raw_match)

print("\n========== FINAL VALIDATION ==========")
print("Overall reconciliation passed:", all_match and raw_match)

