"""
Run this from your project root (same folder as app.py) with:

    python diagnose_sql.py

It reproduces app.py's exact column-standardization steps on
Superstore.csv and calls src.database.initialize_db / load_data
directly, WITHOUT the try/except that app.py wraps this in — so
the real traceback prints instead of being hidden in the sidebar.
"""

import sys
import traceback

import pandas as pd

try:
    from src.database import initialize_db, load_data, get_total_sales
except ImportError as e:
    print("Could not import src.database:", e)
    print("Make sure you're running this from the same folder as app.py,")
    print("and that a src/__init__.py file exists (empty file is fine).")
    sys.exit(1)


CSV_PATH = "Superstore.csv"  # change if your file lives elsewhere

print(f"Reading {CSV_PATH} ...")
df = pd.read_csv(CSV_PATH, encoding="latin1")
print("Raw columns:", df.columns.tolist())

work_df = df.copy()
work_df["date"] = pd.to_datetime(work_df["Order Date"], errors="coerce")
work_df["product"] = work_df["Product Name"].astype(str).str.strip()
work_df["sales"] = pd.to_numeric(work_df["Sales"], errors="coerce")
work_df["profit"] = pd.to_numeric(work_df["Profit"], errors="coerce")
work_df["quantity"] = pd.to_numeric(work_df["Quantity"], errors="coerce")
work_df["category"] = work_df["Category"].astype(str).str.strip()
work_df["region"] = work_df["Region"].astype(str).str.strip()
work_df["discount"] = pd.to_numeric(work_df["Discount"], errors="coerce")

print("work_df columns:", work_df.columns.tolist())

print("\nCalling initialize_db() ...")
try:
    initialize_db()
    print("OK")
except Exception:
    print("initialize_db() FAILED:")
    traceback.print_exc()
    sys.exit(1)

print("\nCalling load_data(work_df) ...")
try:
    load_data(work_df)
    print("OK")
except Exception:
    print("load_data() FAILED — this is your real error:")
    traceback.print_exc()
    sys.exit(1)

print("\nCalling get_total_sales() ...")
try:
    print("Total sales:", get_total_sales())
except Exception:
    print("get_total_sales() FAILED:")
    traceback.print_exc()
    sys.exit(1)

print("\nAll steps succeeded.")