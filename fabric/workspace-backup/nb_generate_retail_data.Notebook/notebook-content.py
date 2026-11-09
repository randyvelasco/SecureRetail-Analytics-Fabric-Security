# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "c41b3337-6220-4296-afd2-5a57cf015e22",
# META       "default_lakehouse_name": "lh_secure_retail",
# META       "default_lakehouse_workspace_id": "7c133c6b-ccdd-439d-b354-f49c9c175a86",
# META       "known_lakehouses": [
# META         {
# META           "id": "c41b3337-6220-4296-afd2-5a57cf015e22"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# **Generate the Bronze data**

# CELL ********************


import os
import csv
import random
from datetime import date, timedelta

import pandas as pd

# ---------------------------------------------------------
# SecureRetail Analytics: Synthetic data generator
# ---------------------------------------------------------

random.seed(42)

BASE_PATH = "/lakehouse/default/Files/bronze"
os.makedirs(BASE_PATH, exist_ok=True)

def save_csv(filename, rows):
    """Save a list of dictionaries as a UTF-8 CSV file."""
    path = os.path.join(BASE_PATH, filename)
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")
    print(f"Created {path} | rows: {len(rows):,}")

# 1. Regions: 3 island groups, 3 branches each
region_specs = [
    ("Luzon", "Metro Manila", "Manila"),
    ("Luzon", "Rizal", "Cainta"),
    ("Luzon", "Pampanga", "Angeles"),
    ("Visayas", "Cebu", "Cebu City"),
    ("Visayas", "Iloilo", "Iloilo City"),
    ("Visayas", "Negros Occidental", "Bacolod"),
    ("Mindanao", "Davao del Sur", "Davao City"),
    ("Mindanao", "Misamis Oriental", "Cagayan de Oro"),
    ("Mindanao", "South Cotabato", "General Santos"),
]

regions = [
    {
        "RegionKey": i + 1,
        "IslandGroup": group,
        "Province": province,
        "Branch": branch
    }
    for i, (group, province, branch) in enumerate(region_specs)
]

# 2. Products
categories = {
    "Electronics": ["Audio", "Accessories", "Computing"],
    "Home": ["Kitchen", "Cleaning", "Furniture"],
    "Grocery": ["Beverages", "Snacks", "Pantry"],
    "Personal Care": ["Hair Care", "Skin Care", "Hygiene"],
}

products = []
for i in range(1, 101):
    category = random.choice(list(categories.keys()))
    cost = round(random.uniform(50, 5000), 2)
    margin_rate = random.uniform(0.10, 0.35)

    products.append({
        "ProductKey": i,
        "ProductName": f"{category} Product {i:03d}",
        "Category": category,
        "Subcategory": random.choice(categories[category]),
        "UnitCost": cost,
        "UnitPrice": round(cost * (1 + margin_rate), 2)
    })

# 3. Customers: synthetic identities only
first_names = [
    "Alex", "Jamie", "Morgan", "Taylor", "Casey",
    "Jordan", "Riley", "Avery", "Sam", "Cameron"
]
last_names = [
    "Santos", "Reyes", "Cruz", "Garcia", "Mendoza",
    "Ramos", "Flores", "Castillo", "Aquino", "Torres"
]

customers = []
for i in range(1, 1001):
    first = random.choice(first_names)
    last = random.choice(last_names)

    customers.append({
        "CustomerKey": i,
        "CustomerName": f"{first} {last}",
        "Email": f"customer{i:04d}@example.com",
        "Phone": f"09XX000{i:04d}",
        "CustomerSegment": random.choice(
            ["Consumer", "Small Business", "Corporate"]
        )
    })

# 4. Date dimension: 2 years
start_date = date(2024, 1, 1)
end_date = date(2025, 12, 31)

dates = []
current_date = start_date

while current_date <= end_date:
    dates.append({
        "DateKey": int(current_date.strftime("%Y%m%d")),
        "FullDate": current_date.isoformat(),
        "Year": current_date.year,
        "MonthNumber": current_date.month,
        "MonthName": current_date.strftime("%B"),
        "Quarter": f"Q{((current_date.month - 1) // 3) + 1}"
    })
    current_date += timedelta(days=1)

# 5. Sales facts: 20,000 transactions
sales = []

product_lookup = {p["ProductKey"]: p for p in products}

for i in range(1, 20001):
    product_key = random.randint(1, len(products))
    product = product_lookup[product_key]
    quantity = random.randint(1, 10)

    # Discount is a fraction between 0 and 0.20
    discount_rate = random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20])

    revenue = round(
        quantity * product["UnitPrice"] * (1 - discount_rate), 2
    )
    cost = round(quantity * product["UnitCost"], 2)

    transaction_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )

    sales.append({
        "SalesID": i,
        "DateKey": int(transaction_date.strftime("%Y%m%d")),
        "ProductKey": product_key,
        "CustomerKey": random.randint(1, len(customers)),
        "RegionKey": random.randint(1, len(regions)),
        "Quantity": quantity,
        "DiscountRate": discount_rate,
        "Revenue": revenue,
        "Cost": cost,
        "Profit": round(revenue - cost, 2)
    })

# 6. Security mapping for dynamic RLS
security_user_region = []

for email, region_keys in [
    ("luzon.manager@example.com", [1, 2, 3]),
    ("visayas.manager@example.com", [4, 5, 6]),
    ("mindanao.manager@example.com", [7, 8, 9]),
    ("analyst@example.com", [1, 2, 3]),
    ("executive@example.com", list(range(1, 10)))
]:
    for region_key in region_keys:
        security_user_region.append({
            "UserEmail": email,
            "RegionKey": region_key
        })

security_user_access = [
    {"UserEmail": "luzon.manager@example.com",
     "AccessLevel": "RegionalManager"},
    {"UserEmail": "visayas.manager@example.com",
     "AccessLevel": "RegionalManager"},
    {"UserEmail": "mindanao.manager@example.com",
     "AccessLevel": "RegionalManager"},
    {"UserEmail": "analyst@example.com",
     "AccessLevel": "SalesAnalyst"},
    {"UserEmail": "executive@example.com",
     "AccessLevel": "Executive"}
]

# 7. Write all source datasets
datasets = {
    "regions.csv": regions,
    "products.csv": products,
    "customers.csv": customers,
    "dates.csv": dates,
    "sales.csv": sales,
    "security_user_region.csv": security_user_region,
    "security_user_access.csv": security_user_access
}

for filename, rows in datasets.items():
    save_csv(filename, rows)

print("\nBronze data generation complete.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Verify the Bronze files**

# CELL ********************


import os

BASE_PATH = "/lakehouse/default/Files/bronze"
os.makedirs(BASE_PATH, exist_ok=True)

for filename in sorted(os.listdir(BASE_PATH)):
    path = os.path.join(BASE_PATH, filename)
    if filename.endswith(".csv"):
        print(f"{filename}: {os.path.getsize(path):,} bytes")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Transform Bronze into Silver tables**

# CELL ********************


from pyspark.sql import functions as F

BRONZE_PATH = (
    "abfss://7c133c6b-ccdd-439d-b354-f49c9c175a86"
    "@onelake.dfs.fabric.microsoft.com/"
    "c41b3337-6220-4296-afd2-5a57cf015e22/"
    "Files/bronze"
)

def read_bronze(filename):
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(f"{BRONZE_PATH}/{filename}")
    )

# Load Bronze CSV files
sales_df = read_bronze("sales.csv")
products_df = read_bronze("products.csv")
customers_df = read_bronze("customers.csv")
regions_df = read_bronze("regions.csv")
dates_df = read_bronze("dates.csv")
user_region_df = read_bronze("security_user_region.csv")
user_access_df = read_bronze("security_user_access.csv")

# Standardize column names
def clean_columns(df):
    for col_name in df.columns:
        df = df.withColumnRenamed(
            col_name, col_name.strip().replace(" ", "_")
        )
    return df

sales_df = clean_columns(sales_df)

# Cast sales columns to appropriate data types
sales_df = (
    sales_df
    .withColumn("SalesID", F.col("SalesID").cast("long"))
    .withColumn("DateKey", F.col("DateKey").cast("int"))
    .withColumn("ProductKey", F.col("ProductKey").cast("int"))
    .withColumn("CustomerKey", F.col("CustomerKey").cast("int"))
    .withColumn("RegionKey", F.col("RegionKey").cast("int"))
    .withColumn("Quantity", F.col("Quantity").cast("int"))
    .withColumn("DiscountRate", F.col("DiscountRate").cast("double"))
    .withColumn("Revenue", F.col("Revenue").cast("double"))
    .withColumn("Cost", F.col("Cost").cast("double"))
    .withColumn("Profit", F.col("Profit").cast("double"))
    .dropDuplicates(["SalesID"])
)

# Remove records with missing keys or invalid numeric values
sales_df = sales_df.filter(
    F.col("SalesID").isNotNull()
    & F.col("DateKey").isNotNull()
    & F.col("ProductKey").isNotNull()
    & F.col("CustomerKey").isNotNull()
    & F.col("RegionKey").isNotNull()
    & F.col("Quantity").isNotNull()
    & F.col("Revenue").isNotNull()
    & F.col("Cost").isNotNull()
    & F.col("Profit").isNotNull()
    & (F.col("Quantity") > 0)
    & (F.col("Revenue") >= 0)
    & (F.col("Cost") >= 0)
)

# Clean dimension and security tables
products_df = clean_columns(products_df).dropDuplicates()
customers_df = clean_columns(customers_df).dropDuplicates()
regions_df = clean_columns(regions_df).dropDuplicates()
dates_df = clean_columns(dates_df).dropDuplicates()
user_region_df = clean_columns(user_region_df).dropDuplicates()
user_access_df = clean_columns(user_access_df).dropDuplicates()

# Write Silver Delta tables
tables = {
    "silver_sales": sales_df,
    "silver_products": products_df,
    "silver_customers": customers_df,
    "silver_regions": regions_df,
    "silver_dates": dates_df,
    "silver_user_region": user_region_df,
    "silver_user_access": user_access_df
}

for table_name, df in tables.items():
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(table_name)
    )
    print(f"Saved {table_name}: {df.count()} rows")

print("Silver transformation completed.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Validate the Silver tables**

# CELL ********************


expected_tables = [
    "silver_sales",
    "silver_products",
    "silver_customers",
    "silver_regions",
    "silver_dates",
    "silver_user_region",
    "silver_user_access"
]

for table_name in expected_tables:
    count = spark.table(table_name).count()
    print(f"{table_name}: {count:,} rows")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Validate Silver data quality**

# CELL ********************


from pyspark.sql import functions as F

tables = [
    "silver_sales",
    "silver_products",
    "silver_customers",
    "silver_regions",
    "silver_dates",
    "silver_user_region",
    "silver_user_access"
]

# 1. Confirm row counts
for table in tables:
    df = spark.read.table(table)
    print(f"{table}: {df.count():,} rows")

# 2. Inspect the sales schema and sample records
sales = spark.read.table("silver_sales")

sales.printSchema()
display(sales.limit(10))


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Validate the security mappings**

# CELL ********************


user_region = spark.read.table("silver_user_region")
regions = spark.read.table("silver_regions")

display(
    user_region
    .join(regions, on="RegionKey", how="left")
    .orderBy("UserEmail", "RegionKey")
)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Inspect the Silver tables before creating Gold**

# CELL ********************


tables_to_inspect = [
    "silver_sales",
    "silver_products",
    "silver_customers",
    "silver_regions",
    "silver_dates",
    "silver_user_region",
    "silver_user_access"
]

for table_name in tables_to_inspect:
    print(f"\n{'=' * 60}")
    print(f"TABLE: {table_name}")
    print("=" * 60)

    df = spark.read.table(table_name)
    df.printSchema()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Run the corrected security validation**

# CELL ********************


from pyspark.sql import functions as F

user_region = spark.read.table("silver_user_region")
user_access = spark.read.table("silver_user_access")
regions = spark.read.table("silver_regions")

# Expected access assignments
expected_counts = {
    "analyst@example.com": 3,
    "executive@example.com": 9,
    "luzon.manager@example.com": 3,
    "visayas.manager@example.com": 3,
    "mindanao.manager@example.com": 3
}

# 1. Validate assignment counts
total_rows = user_region.count()
distinct_rows = user_region.select(
    "UserEmail", "RegionKey"
).distinct().count()

duplicates = (
    user_region.groupBy("UserEmail", "RegionKey")
    .count()
    .filter(F.col("count") > 1)
)

print("=== ASSIGNMENT INTEGRITY ===")
print(f"Total assignments: {total_rows}")
print(f"Distinct assignments: {distinct_rows}")
print(f"Duplicate assignments: {duplicates.count()}")

# 2. Validate region keys
invalid_regions = (
    user_region.select("RegionKey").distinct()
    .join(
        regions.select("RegionKey").distinct(),
        on="RegionKey",
        how="left_anti"
    )
)

print(f"Invalid region keys: {invalid_regions.count()}")

# 3. Validate user assignment counts
print("\n=== EXPECTED ACCESS COUNTS ===")

actual_counts = {
    row["UserEmail"]: row["count"]
    for row in user_region.groupBy("UserEmail").count().collect()
}

for email, expected in expected_counts.items():
    actual = actual_counts.get(email, 0)
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status}: {email} | expected={expected}, actual={actual}")

unexpected_users = sorted(set(actual_counts) - set(expected_counts))
missing_users = sorted(set(expected_counts) - set(actual_counts))

print("Unexpected users:", unexpected_users)
print("Missing users:", missing_users)

# 4. Validate access-table coverage
region_users = set(actual_counts)
access_users = {
    row["UserEmail"]
    for row in user_access.select("UserEmail").distinct().collect()
}

print("\n=== USER ACCESS TABLE ===")
print("Access table rows:", user_access.count())
print("Users without access records:", sorted(region_users - access_users))
print("Access records without region mappings:",
      sorted(access_users - region_users))

# 5. Inspect role assignments
print("\n=== ACCESS LEVELS ===")
display(user_access.orderBy("UserEmail"))

# 6. Show readable region mappings
print("\n=== REGION MAPPINGS ===")
display(
    user_region.join(regions, on="RegionKey", how="left")
    .select(
        "UserEmail",
        "RegionKey",
        "IslandGroup",
        "Province",
        "Branch"
    )
    .orderBy("UserEmail", "RegionKey")
)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Check whether the Gold tables already exist**

# CELL ********************

for table_name in [
    "gold_fact_sales",
    "gold_dim_date",
    "gold_dim_product",
    "gold_dim_customer",
    "gold_dim_region"
]:
    exists = spark.catalog.tableExists(table_name)
    print(f"{table_name}: {'EXISTS' if exists else 'NOT CREATED'}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Create the Gold dimensional model**

# CELL ********************


from pyspark.sql import functions as F

# Read validated Silver tables
sales = spark.read.table("silver_sales")
dates = spark.read.table("silver_dates")
products = spark.read.table("silver_products")
customers = spark.read.table("silver_customers")
regions = spark.read.table("silver_regions")

# 1. Gold fact table
gold_fact_sales = sales.select(
    "SalesID",
    "DateKey",
    "ProductKey",
    "CustomerKey",
    "RegionKey",
    "Quantity",
    "DiscountRate",
    "Revenue",
    "Cost",
    "Profit"
)

# 2. Gold dimensions
gold_dim_date = dates.select(
    "DateKey",
    "FullDate",
    "Year",
    "MonthNumber",
    "MonthName",
    "Quarter"
)

gold_dim_product = products.select(
    "ProductKey",
    "ProductName",
    "Category",
    "Subcategory",
    "UnitCost",
    "UnitPrice"
)

gold_dim_customer = customers.select(
    "CustomerKey",
    "CustomerName",
    "Email",
    "Phone",
    "CustomerSegment"
)

gold_dim_region = regions.select(
    "RegionKey",
    "IslandGroup",
    "Province",
    "Branch"
)

# Write Gold Delta tables
gold_fact_sales.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_fact_sales"
)

gold_dim_date.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_dim_date"
)

gold_dim_product.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_dim_product"
)

gold_dim_customer.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_dim_customer"
)

gold_dim_region.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_dim_region"
)

print("Gold dimensional model created successfully.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Verify the Gold tables**

# CELL ********************


gold_tables = [
    "gold_fact_sales",
    "gold_dim_date",
    "gold_dim_product",
    "gold_dim_customer",
    "gold_dim_region"
]

for table_name in gold_tables:
    df = spark.read.table(table_name)
    print(f"{table_name}: {df.count():,} rows")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Validate Gold data integrity**

# CELL ********************


from pyspark.sql import functions as F

# Load Gold tables
fact = spark.read.table("gold_fact_sales")

dimensions = {
    "DateKey": spark.read.table("gold_dim_date"),
    "ProductKey": spark.read.table("gold_dim_product"),
    "CustomerKey": spark.read.table("gold_dim_customer"),
    "RegionKey": spark.read.table("gold_dim_region")
}

results = []

# Check dimension keys for nulls and duplicates
print("=== DIMENSION KEY VALIDATION ===")

for key, dim in dimensions.items():
    null_keys = dim.filter(F.col(key).isNull()).count()

    duplicate_keys = (
        dim.groupBy(key)
        .count()
        .filter(F.col(key).isNull() | (F.col("count") > 1))
        .count()
    )

    results.append((f"{key} null keys", null_keys))
    results.append((f"{key} duplicate-key groups", duplicate_keys))

    print(
        f"{key}: null keys={null_keys}, "
        f"duplicate-key groups={duplicate_keys}"
    )

# Check fact table keys and orphan references
print("\n=== FACT TABLE VALIDATION ===")

for key, dim in dimensions.items():
    null_fact_keys = fact.filter(F.col(key).isNull()).count()

    orphan_rows = (
        fact.filter(F.col(key).isNotNull())
        .select(key)
        .join(
            dim.select(key).distinct(),
            on=key,
            how="left_anti"
        )
        .count()
    )

    results.append((f"Fact {key} nulls", null_fact_keys))
    results.append((f"Fact {key} orphan rows", orphan_rows))

    print(
        f"{key}: null fact keys={null_fact_keys}, "
        f"orphan fact rows={orphan_rows}"
    )

# Check SalesID uniqueness
sales_id_nulls = fact.filter(F.col("SalesID").isNull()).count()

sales_id_duplicates = (
    fact.groupBy("SalesID")
    .count()
    .filter(F.col("SalesID").isNull() | (F.col("count") > 1))
    .count()
)

print("\n=== SALES ID VALIDATION ===")
print("Null SalesID values:", sales_id_nulls)
print("Duplicate SalesID groups:", sales_id_duplicates)

print("\nValidation cell completed.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
