import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

DB_PATH = ROOT / "data/processed/saas_revenue.db"
SQL_DIR = ROOT / "sql"

movement_sql = (
    SQL_DIR / "02_movement_detail.sql"
).read_text(encoding="utf-8")

bridge_sql = (
    SQL_DIR / "03_monthly_mrr_bridge.sql"
).read_text(encoding="utf-8").strip().rstrip(";")

retention_sql = (
    SQL_DIR / "04_retention_metrics.sql"
).read_text(encoding="utf-8")

with sqlite3.connect(DB_PATH) as conn:

    conn.execute(
        f"CREATE TEMP VIEW movement_detail AS {movement_sql}"
    )

    conn.execute(
        "CREATE TEMP VIEW monthly_mrr_bridge AS "
        + bridge_sql
    )

    retention = pd.read_sql_query(
        retention_sql, conn
    )

print("\nMONTHLY RETENTION METRICS")
print("-" * 70)

print(retention.round(2).to_string(index=False))

print("\nTotal months:", len(retention))

print("\nLATEST MONTH")
print(retention.tail(1).round(2).to_string(index=False))

