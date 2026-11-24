import sqlite3
import pandas as pd
from pathlib import Path

# Locate project files
project_root = Path(__file__).resolve().parent.parent

db_path = project_root / "data/processed/saas_revenue.db"
sql_path = project_root / "sql/01_data_profiling.sql"

# Read SQL queries
sql_text = sql_path.read_text(encoding="utf-8")

queries = [
    query.strip()
    for query in sql_text.split(";")
    if query.strip()
]

# Connect in read-only mode
conn = sqlite3.connect(
    db_path.as_uri() + "?mode=ro",
    uri=True
)

# Execute each SQL query
try:
    for number, query in enumerate(queries, start=1):

        print(f"\n========== QUERY {number} ==========")

        result = pd.read_sql_query(query, conn)

        print(result.to_string(index=False))

finally:
    conn.close()