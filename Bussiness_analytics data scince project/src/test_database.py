import pandas as pd

from database import (
    initialize_db,
    load_data,
    get_total_sales,
    get_total_profit,
    get_sales_by_category,
    get_top_products
)

from cleaning import clean_data


df = pd.read_csv(
    "data/superstore.csv",
    encoding="latin1"
)

print("Original columns:")
print(df.columns.tolist())


# 2. Clean and standardize the data
df = clean_data(df)

print("\nCleaned columns:")
print(df.columns.tolist())


# 3. Initialize database
initialize_db()


# 4. Put cleaned data into SQLite
load_data(df)


# 5. Run SQL queries
print("\nTotal Sales:")
print(get_total_sales())

print("\nTotal Profit:")
print(get_total_profit())

print("\nSales by Category:")
print(get_sales_by_category())

print("\nTop 5 Products:")
print(get_top_products(5))