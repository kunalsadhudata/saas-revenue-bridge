import sqlite3
from pathlib import Path

# Locate project directory
project_root = Path(__file__).resolve().parent.parent

# Define database location
db_path = (
    project_root / "data" / "processed" / "saas_revenue.db"
)

# Ensure directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect(db_path)

# Create cursor
cursor = conn.cursor()

# Verify SQLite connection
cursor.execute("SELECT sqlite_version();")

print("SQLite version:", cursor.fetchone()[0])
print("Database created successfully.")
print("Database location:", db_path)

# Create billing table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS saas_billing (
        month TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        plan TEXT NOT NULL,
        mrr INTEGER NOT NULL,

        PRIMARY KEY (month, customer_id),

        CHECK (
            (plan = 'Starter' AND mrr = 29)
            OR (plan = 'Growth' AND mrr = 99)
            OR (plan = 'Scale' AND mrr = 299)
        )
    );
""")

conn.commit()

print("Billing table created successfully.")

# Close database connection
conn.close()

