import sqlite3
from pathlib import Path

DB_PATH = Path("data/processed/saas_revenue.db")

with sqlite3.connect(
    DB_PATH.resolve().as_uri() + "?mode=ro",
    uri=True
) as conn:

    print("========== TABLE STRUCTURE ==========")

    for row in conn.execute("PRAGMA table_info(saas_billing)"):
        print(row)

    print("\n========== TOTAL RECORDS ==========")

    count = conn.execute(
        "SELECT COUNT(*) FROM saas_billing"
    ).fetchone()[0]

    print(f"Total billing records: {count:,}")

    print("\n========== SAMPLE RECORDS ==========")

    for row in conn.execute("""
        SELECT *
        FROM saas_billing
        ORDER BY customer_id, month
        LIMIT 10
    """):
        print(row)

 
    print("\n========== CALENDAR MONTH INDEX ==========")

    sql_path = Path("sql/02_customer_movement_classification.sql")

    query = sql_path.read_text(encoding="utf-8")

    for row in conn.execute(query):
        print(row)       



    print("\n========== POTENTIAL CHURN EVENTS ==========")

    churn_sql_path = Path("sql/02_churn_detection.sql")

    churn_query = churn_sql_path.read_text(encoding="utf-8")

    for row in conn.execute(churn_query):
        print(row)


    print("\n========== MOVEMENT COUNTS AND SIGNED MRR ==========")

    combined_sql_path = Path("sql/02_combined_movements.sql")

    combined_query = combined_sql_path.read_text(encoding="utf-8")

    for row in conn.execute(combined_query):
        print(row)


    print("\n========== MOVEMENT VALIDATION ==========")

    validation_sql_path = Path("sql/02_movement_validation.sql")

    validation_query = validation_sql_path.read_text(encoding="utf-8")

    for row in conn.execute(validation_query):
        print(row)    