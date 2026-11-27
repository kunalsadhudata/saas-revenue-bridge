from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("data/processed/saas_revenue.db")
SQL_DIR = Path("sql")
OUTPUT_DIR = Path("outputs/tables")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

exports = {
    "04_retention_metrics.sql": "monthly_retention_metrics.csv",
    "04_customer_cohorts.sql": "customer_cohorts.csv",
    "04_customer_retention_cohorts.sql": "customer_retention_cohorts.csv",
    "04_revenue_retention_cohorts.sql": "revenue_retention_cohorts.csv",
    "04_plan_revenue_analysis.sql": "plan_revenue_analysis.csv",
    "04_plan_movement_analysis.sql": "plan_movement_analysis.csv"
}

with sqlite3.connect(DB_PATH) as conn:

    movement_sql = (
        SQL_DIR / "02_movement_detail.sql"
    ).read_text(encoding="utf-8")

    bridge_sql = (
        SQL_DIR / "03_monthly_mrr_bridge.sql"
    ).read_text(encoding="utf-8")

    conn.execute(
        f"CREATE TEMP VIEW movement_detail AS {movement_sql}"
    )

    conn.execute(
        f"CREATE TEMP VIEW monthly_mrr_bridge AS {bridge_sql}"
    )

    print("PHASE 04 - CSV EXPORT VALIDATION")
    print("-" * 60)

    for sql_file, csv_file in exports.items():

        query = (SQL_DIR / sql_file).read_text(
            encoding="utf-8"
        )

        df = pd.read_sql_query(query, conn)

        output_path = OUTPUT_DIR / csv_file

        df.to_csv(output_path, index=False)

        exported = pd.read_csv(output_path)

        pd.testing.assert_frame_equal(
            df.reset_index(drop=True),
            exported,
            check_dtype=False
        )

        print(f"{csv_file}: {len(df)} rows - PASS")

print("\nAll six CSV exports validated successfully.")