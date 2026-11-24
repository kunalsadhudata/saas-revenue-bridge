import pandas as pd
import numpy as np
from pathlib import Path

# Simulation configuration
RANDOM_SEED = 42
START_MONTH = "2025-01"
END_MONTH = "2026-09"

NEW_CUSTOMERS_PER_MONTH = 40

CHURN_RATE = 0.035
UPGRADE_RATE = 0.04
DOWNGRADE_RATE = 0.02
REACTIVATION_RATE = 0.015

# Subscription plans
PLANS = ["Starter", "Growth", "Scale"]

PLAN_PRICES = {
    "Starter": 29,
    "Growth": 99,
    "Scale": 299
}

PLAN_PROBABILITIES = [0.60, 0.30, 0.10]

# Initialize random number generator
rng = np.random.default_rng(RANDOM_SEED)

# Generate calendar months
months = pd.period_range(
    start=START_MONTH,
    end=END_MONTH,
    freq="M"
)

# Verify configuration
print("Simulation configuration loaded.")
print("Start month:", months[0])
print("End month:", months[-1])
print("Total months:", len(months))
print("Random seed:", RANDOM_SEED)

# Initialize customer tracking
active_customers = {}
inactive_customers = {}

# Store monthly subscription records
records = []

# Initialize customer ID counter
next_customer_id = 1

# Verify initial state
print("\nCustomer tracking initialized.")
print("Active customers:", len(active_customers))
print("Inactive customers:", len(inactive_customers))
print("Monthly records:", len(records))
print("Next customer ID:", next_customer_id)

# Function to generate new customers
def add_new_customers():
    global next_customer_id

    for _ in range(NEW_CUSTOMERS_PER_MONTH):

        customer_id = f"C{next_customer_id:04d}"

        plan = rng.choice(
            PLANS,
            p=PLAN_PROBABILITIES
        )

        active_customers[customer_id] = str(plan)

        next_customer_id += 1

# Function to simulate existing customer movements
def simulate_existing_customers(month):

    for customer_id in list(active_customers):

        current_plan = active_customers[customer_id]
        plan_index = PLANS.index(current_plan)

        movement = rng.random()

        # Churn
        if movement < CHURN_RATE:
            inactive_customers[customer_id] = {
                "last_plan": current_plan,
                "churn_month": month
            }

            del active_customers[customer_id]

        # Upgrade
        elif movement < CHURN_RATE + UPGRADE_RATE:
            if plan_index < len(PLANS) - 1:
                active_customers[customer_id] = (
                    PLANS[plan_index + 1]
                )

        # Downgrade
        elif movement < (
            CHURN_RATE + UPGRADE_RATE + DOWNGRADE_RATE
        ):
            if plan_index > 0:
                active_customers[customer_id] = (
                    PLANS[plan_index - 1]
                )

# Function to simulate customer reactivation
def simulate_reactivation(month):

    for customer_id in list(inactive_customers):

        customer = inactive_customers[customer_id]

        months_inactive = (
            month.ordinal - customer["churn_month"].ordinal
        )

        if months_inactive >= 1:

            if rng.random() < REACTIVATION_RATE:

                active_customers[customer_id] = (
                    customer["last_plan"]
                )

                del inactive_customers[customer_id]


# Run the complete monthly simulation
for month in months:

    simulate_existing_customers(month)

    simulate_reactivation(month)

    add_new_customers()

    for customer_id, plan in active_customers.items():

        records.append({
            "month": str(month),
            "customer_id": customer_id,
            "plan": plan,
            "mrr": PLAN_PRICES[plan]
        })

    print(
        f"{month} | "
        f"Active: {len(active_customers)} | "
        f"Inactive: {len(inactive_customers)}"
    )

    # Convert records into a DataFrame
df = pd.DataFrame(records)

# Sort the dataset
df = df.sort_values(
    ["month", "customer_id"]
).reset_index(drop=True)

# Define the raw data output path
project_root = Path(__file__).resolve().parent.parent

output_path = (
    project_root / "data" / "raw" / "saas_billing.csv"
)

# Ensure the raw data directory exists
output_path.parent.mkdir(parents=True, exist_ok=True)

# Export without overwriting existing raw data
df.to_csv(output_path, index=False, mode="x")

# Display dataset summary
print("\n========== DATA GENERATION COMPLETE ==========")

print("Total rows:", len(df))
print("Unique customers:", df["customer_id"].nunique())
print("Total months:", df["month"].nunique())
print("Start month:", df["month"].min())
print("End month:", df["month"].max())

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset saved to:")
print(output_path)

