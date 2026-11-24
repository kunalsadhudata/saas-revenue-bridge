import pandas as pd
from pathlib import Path

# Locate the raw dataset
project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root / "data" / "raw" / "saas_billing.csv"
)

# Read the raw dataset
df = pd.read_csv(file_path)

print("========== DATA QUALITY VALIDATION ==========")

print("\nTotal rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:")
print(df.duplicated().sum())

print("\nDuplicate customer-month records:")
print(df.duplicated(
    subset=["month", "customer_id"]
).sum())

# Business rules validation
print("\n========== BUSINESS RULES VALIDATION ==========")

valid_prices = {
    "Starter": 29,
    "Growth": 99,
    "Scale": 299
}

invalid_plans = (~df["plan"].isin(valid_prices)).sum()

expected_mrr = df["plan"].map(valid_prices)

price_mismatches = (df["mrr"] != expected_mrr).sum()

non_positive_mrr = (df["mrr"] <= 0).sum()

invalid_ids = (
    ~df["customer_id"].str.fullmatch(r"C\d{4}", na=False)
).sum()

print("Invalid plans:", invalid_plans)
print("MRR price mismatches:", price_mismatches)
print("Non-positive MRR:", non_positive_mrr)
print("Invalid customer IDs:", invalid_ids)

# Calendar coverage validation
print("\n========== CALENDAR VALIDATION ==========")

expected_months = set(
    pd.period_range(
        "2025-01",
        "2026-09",
        freq="M"
    ).astype(str)
)

actual_months = set(df["month"])

missing_months = expected_months - actual_months
unexpected_months = actual_months - expected_months

print("Unique customers:", df["customer_id"].nunique())
print("Total months:", len(actual_months))
print("Start month:", df["month"].min())
print("End month:", df["month"].max())
print("Missing months:", sorted(missing_months))
print("Unexpected months:", sorted(unexpected_months))

print("\n========== ROW COUNT AUDIT ==========")

print("Original rows:", len(df))
print("Rows removed: 0")
print("Final rows:", len(df))

# Customer movement verification
print("\n========== MOVEMENT VERIFICATION ==========")

movement_counts = {
    "New": 0,
    "Expansion": 0,
    "Contraction": 0,
    "Churn": 0,
    "Reactivation": 0,
    "Unchanged": 0
}

previous = {}
ever_paid = set()

for month in sorted(df["month"].unique()):

    monthly_data = df[df["month"] == month]

    current = dict(zip(
        monthly_data["customer_id"],
        monthly_data["mrr"]
    ))

    for cid, mrr in current.items():

        if cid not in ever_paid:
            movement_counts["New"] += 1

        elif cid not in previous:
            movement_counts["Reactivation"] += 1

        elif mrr > previous[cid]:
            movement_counts["Expansion"] += 1

        elif mrr < previous[cid]:
            movement_counts["Contraction"] += 1

        else:
            movement_counts["Unchanged"] += 1

    for cid in previous:
        if cid not in current:
            movement_counts["Churn"] += 1

    ever_paid.update(current.keys())
    previous = current

for movement, count in movement_counts.items():
    print(f"{movement}: {count}")

# Verify all required movement categories exist
required_movements = [
    "New",
    "Expansion",
    "Contraction",
    "Churn",
    "Reactivation"
]

all_movements_present = all(
    movement_counts[movement] > 0
    for movement in required_movements
)

print("\n========== MOVEMENT VALIDATION ==========")

print("All five movements present:", all_movements_present)

print(
    "New customer reconciliation:",
    movement_counts["New"] == df["customer_id"].nunique()
)

print(
    "Active record reconciliation:",
    sum(
        count
        for movement, count in movement_counts.items()
        if movement != "Churn"
    ) == len(df)
)

