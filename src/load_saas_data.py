import sqlite3
import pandas as pd
from pathlib import Path

# Locate project directory
project_root = Path(__file__).resolve().parent.parent

csv_path = project_root / "data/raw/saas_billing.csv"
db_path = project_root / "data/processed/saas_revenue.db"

# Read raw CSV
df = pd.read_csv(csv_path)

# Verify database exists
if not db_path.is_file():
    raise FileNotFoundError(db_path)

# Connect to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("CSV records:", len(df))

# Check existing table records
cursor.execute("SELECT COUNT(*) FROM saas_billing;")
before_count = cursor.fetchone()[0]

print("Database rows before loading:", before_count)


# Prevent accidental duplicate loading
if before_count != 0:
    conn.close()
    raise RuntimeError("Billing table is not empty.")

# Prepare records for insertion
rows = list(
    df[["month", "customer_id", "plan", "mrr"]]
    .itertuples(index=False, name=None)
)

# Insert records and verify within a transaction
try:
    with conn:
        cursor.executemany("""
            INSERT INTO saas_billing
            (month, customer_id, plan, mrr)
            VALUES (?, ?, ?, ?);
        """, rows)

        cursor.execute("SELECT COUNT(*) FROM saas_billing;")
        after_count = cursor.fetchone()[0]

        if after_count != len(df):
            raise RuntimeError("Row count mismatch.")

    print("Data loaded successfully.")

finally:
    conn.close()

# Final loading summary
print("\n========== DATA LOADING SUMMARY ==========")

print("CSV records:", len(df))
print("Database rows before:", before_count)
print("Database rows after:", after_count)
print("Rows inserted:", after_count - before_count)
print("Row count difference:", len(df) - after_count)
print("Row count reconciliation:", len(df) == after_count)

