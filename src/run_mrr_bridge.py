import sqlite3
from pathlib import Path

import pandas as pd


db_path = Path("data/processed/saas_revenue.db")

movement_sql = Path(
    "sql/02_movement_detail.sql"
).read_text(encoding="utf-8").strip().rstrip(";")

bridge_sql = Path(
    "sql/03_monthly_mrr_bridge.sql"
).read_text(encoding="utf-8")

with sqlite3.connect(db_path) as conn:

    conn.execute(
        f"CREATE TEMP VIEW movement_detail AS {movement_sql}"
    )

    df = pd.read_sql_query(bridge_sql, conn)

print("MONTHLY MRR BRIDGE")
print(df.to_string(index=False))

print("\nTotal months:", len(df))
print("Unique months:", df["month"].nunique())

print("\nMOVEMENT COLUMN TOTALS")

movement_columns = [
    "new_mrr",
    "expansion_mrr",
    "contraction_mrr",
    "churn_mrr",
    "reactivation_mrr"
]

print(df[movement_columns].sum().to_string())

print("\nMissing values:", df.isna().sum().sum())



print("\nCumulative net MRR movement:",
      df["net_mrr_movement"].sum())

print("Latest-month net MRR movement:",
      df.iloc[-1]["net_mrr_movement"])

print("Net movement calculation valid:",
      df["net_mrr_movement"].eq(
          df[movement_columns].sum(axis=1)
      ).all())

print("\nCLOSING MRR CALCULATION")

print(
    df[
        [
            "month",
            "opening_mrr",
            "net_mrr_movement",
            "calculated_closing_mrr"
        ]
    ].to_string(index=False)
)

print("\nLatest calculated closing MRR:",
      df.iloc[-1]["calculated_closing_mrr"])

print("Closing MRR formula valid:",
      df["calculated_closing_mrr"].eq(
          df["opening_mrr"] + df["net_mrr_movement"]
      ).all())

# Step 03.10: Monthly MRR reconciliation

df["mrr_difference"] = (
    df["calculated_closing_mrr"]
    - df["actual_closing_mrr"]
)

print("\nMONTHLY MRR RECONCILIATION")

print(
    df[
        [
            "month",
            "calculated_closing_mrr",
            "actual_closing_mrr",
            "mrr_difference"
        ]
    ].to_string(index=False)
)

print("\nLatest-month MRR difference:",
      df.iloc[-1]["mrr_difference"])

# Step 03.11: Automated monthly tie-out validation

total_months = len(df)

matched_months = df["mrr_difference"].eq(0).sum()

failed_months = total_months - matched_months

max_absolute_difference = df["mrr_difference"].abs().max()

tie_out_passed = (
    total_months == 21
    and df["month"].nunique() == 21
    and failed_months == 0
)

print("\nMONTHLY TIE-OUT VALIDATION")
print("-" * 40)

print("Total months:", total_months)
print("Matched months:", matched_months)
print("Failed months:", failed_months)
print("Maximum absolute difference:", max_absolute_difference)

print(
    "Overall tie-out status:",
    "PASS" if tie_out_passed else "FAIL"
)

if not tie_out_passed:
    raise ValueError("Monthly MRR tie-out validation failed.")      

# Step 03.12: Monthly MRR growth percentage

df["mrr_growth_pct"] = (
    df["net_mrr_movement"]
    .div(df["opening_mrr"].where(df["opening_mrr"] > 0))
    .mul(100)
)

print("\nMONTHLY MRR GROWTH")
print("-" * 40)

print(
    df[
        [
            "month",
            "opening_mrr",
            "actual_closing_mrr",
            "net_mrr_movement",
            "mrr_growth_pct"
        ]
    ].round(2).to_string(index=False)
)

print(
    "\nLatest-month MRR growth:",
    f"{df.iloc[-1]['mrr_growth_pct']:.2f}%"
)

print(
    "Months with undefined growth:",
    df["mrr_growth_pct"].isna().sum()
)    

# Step 03.13: Opening and closing ARR

df["opening_arr"] = df["opening_mrr"] * 12

df["closing_arr"] = df["actual_closing_mrr"] * 12

df["net_arr_movement"] = df["net_mrr_movement"] * 12

print("\nMONTHLY ARR SUMMARY")
print("-" * 40)

print(
    df[
        [
            "month",
            "opening_arr",
            "closing_arr",
            "net_arr_movement"
        ]
    ].to_string(index=False)
)

print("\nLatest opening ARR:",
      df.iloc[-1]["opening_arr"])

print("Latest closing ARR:",
      df.iloc[-1]["closing_arr"])

print("Latest net ARR movement:",
      df.iloc[-1]["net_arr_movement"])

print("ARR tie-out valid:",
      df["closing_arr"].eq(
          df["opening_arr"] + df["net_arr_movement"]
      ).all())



# Step 03.14: Existing-base net movement

df["existing_base_net_mrr"] = (
    df["expansion_mrr"]
    + df["contraction_mrr"]
    + df["churn_mrr"]
)

df["existing_base_growth_pct"] = (
    df["existing_base_net_mrr"]
    .div(df["opening_mrr"].where(df["opening_mrr"] > 0))
    .mul(100)
)

print("\nEXISTING-BASE REVENUE PERFORMANCE")
print("-" * 40)

print(
    df[
        [
            "month",
            "opening_mrr",
            "existing_base_net_mrr",
            "existing_base_growth_pct"
        ]
    ].round(2).to_string(index=False)
)

print(
    "\nLatest existing-base net MRR:",
    df.iloc[-1]["existing_base_net_mrr"]
)

print(
    "Latest existing-base growth:",
    f"{df.iloc[-1]['existing_base_growth_pct']:.2f}%"
)

print(
    "Movement decomposition valid:",
    df["net_mrr_movement"].eq(
        df["existing_base_net_mrr"]
        + df["new_mrr"]
        + df["reactivation_mrr"]
    ).all()
)



# Step 03.17: Latest-month business findings

latest = df.sort_values("month").iloc[-1]

print("\nLATEST-MONTH BUSINESS FINDINGS")
print("-" * 50)

print("Month:", latest["month"])
print("Active customers:", latest["active_customers"])
print("Opening MRR:", latest["opening_mrr"])
print("New MRR:", latest["new_mrr"])
print("Expansion MRR:", latest["expansion_mrr"])
print("Contraction MRR:", latest["contraction_mrr"])
print("Churn MRR:", latest["churn_mrr"])
print("Reactivation MRR:", latest["reactivation_mrr"])
print("Net MRR movement:", latest["net_mrr_movement"])
print("Closing MRR:", latest["actual_closing_mrr"])
print("Closing ARR:", latest["closing_arr"])

print(f"MRR growth: {latest['mrr_growth_pct']:.2f}%")

print("Existing-base net MRR:",
      latest["existing_base_net_mrr"])

if latest["existing_base_net_mrr"] < 0:
    print("Existing customer base: SHRINKING")
elif latest["existing_base_net_mrr"] > 0:
    print("Existing customer base: GROWING")
else:
    print("Existing customer base: STABLE")


    # Step 03.18: Export and validate monthly MRR bridge

from pathlib import Path

output_path = Path("outputs/tables/monthly_mrr_bridge.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

# Read back exported file
exported = pd.read_csv(output_path)

# Validate exported data
pd.testing.assert_frame_equal(
    df.reset_index(drop=True),
    exported,
    check_dtype=False
)

print("\nCSV EXPORT VALIDATION")
print("-" * 50)

print("File saved:", output_path)
print("Total rows:", len(exported))
print("Unique months:", exported["month"].nunique())
print("Latest closing MRR:",
      exported.iloc[-1]["actual_closing_mrr"])
print("Latest closing ARR:",
      exported.iloc[-1]["closing_arr"])
print("Maximum absolute MRR difference:",
      exported["mrr_difference"].abs().max())

print("CSV read-back validation: PASS")