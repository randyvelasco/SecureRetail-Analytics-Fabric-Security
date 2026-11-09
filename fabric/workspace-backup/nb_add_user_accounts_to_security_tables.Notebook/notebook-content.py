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

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

table_name = "silver_user_region"
test_email = "fabrictrial1@pece555outlook.onmicrosoft.com"
test_region_key = 2

existing = spark.table(table_name)

already_exists = existing.filter(
    (F.lower(F.col("UserEmail")) == test_email.lower()) &
    (F.col("RegionKey") == test_region_key)
).limit(1).count() > 0

if not already_exists:
    schema = StructType([
        StructField("UserEmail", StringType(), True),
        StructField("RegionKey", IntegerType(), True)
    ])

    new_row = spark.createDataFrame(
        [(test_email, test_region_key)],
        schema=schema
    )

    new_row.write.format("delta").mode("append").saveAsTable(table_name)

display(
    spark.table(table_name)
    .filter(F.lower(F.col("UserEmail")) == test_email.lower())
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType
)

test_email = "fabrictrial1@pece555outlook.onmicrosoft.com"

region_table = "silver_user_region"

# 2. Add the access-level mapping
access_table = "silver_user_access"
access_level = "SalesAnalyst"

access_schema = StructType([
    StructField("UserEmail", StringType(), True),
    StructField("AccessLevel", StringType(), True)
])

existing_access = spark.table(access_table)

access_exists = existing_access.filter(
    F.lower(F.col("UserEmail")) == test_email.lower()
).limit(1).count() > 0

if not access_exists:
    spark.createDataFrame(
        [(test_email, access_level)],
        schema=access_schema
    ).write.format("delta").mode("append").saveAsTable(access_table)

# 3. Verify the entries
print("Region mapping:")
display(
    spark.table(region_table)
    .filter(F.lower(F.col("UserEmail")) == test_email.lower())
)

print("Access-level mapping:")
display(
    spark.table(access_table)
    .filter(F.lower(F.col("UserEmail")) == test_email.lower())
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F

test_email = "fabrictrial1@pece555outlook.onmicrosoft.com"

print("Region mapping:")
display(
    spark.table("silver_user_region")
    .filter(F.lower(F.col("UserEmail")) == test_email.lower())
)

print("Access mapping:")
display(
    spark.table("silver_user_access")
    .filter(F.lower(F.col("UserEmail")) == test_email.lower())
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark.sql("""
SELECT UserEmail, RegionKey
FROM silver_user_region
WHERE LOWER(UserEmail) =
      'fabrictrial1@pece555outlook.onmicrosoft.com'
""").show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Inspect region assignments before updating security mappings**

# CELL ********************


# Inspect region assignments before updating security mappings
regions = (
    spark.table("gold_dim_region")
    .select("RegionKey", "IslandGroup", "Province", "Branch")
    .orderBy("IslandGroup", "RegionKey")
)

regions.show(20, truncate=False)

print("Island-group counts:")
regions.groupBy("IslandGroup").count().orderBy("IslandGroup").show()

print("Current access mappings:")
spark.table("silver_user_access").orderBy("UserEmail").show(
    50, truncate=False
)

print("Current regional mappings:")
spark.table("silver_user_region").orderBy(
    "UserEmail", "RegionKey"
).show(50, truncate=False)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Add the region manager and executive accounts**

# CELL ********************


from pyspark.sql import functions as F

# New account-to-role mappings
new_access = [
    ("regionmanager1@pece555outlook.onmicrosoft.com", "RegionalManager"),
    ("regionmanager2@pece555outlook.onmicrosoft.com", "RegionalManager"),
    ("regionmanager3@pece555outlook.onmicrosoft.com", "RegionalManager"),
    ("exec1@pece555outlook.onmicrosoft.com", "Executive"),
]

access_schema = "UserEmail string, AccessLevel string"
new_access_df = spark.createDataFrame(new_access, access_schema)

# New account-to-region mappings
new_region_mappings = [
    ("regionmanager1@pece555outlook.onmicrosoft.com", 1),
    ("regionmanager1@pece555outlook.onmicrosoft.com", 2),
    ("regionmanager1@pece555outlook.onmicrosoft.com", 3),

    ("regionmanager2@pece555outlook.onmicrosoft.com", 4),
    ("regionmanager2@pece555outlook.onmicrosoft.com", 5),
    ("regionmanager2@pece555outlook.onmicrosoft.com", 6),

    ("regionmanager3@pece555outlook.onmicrosoft.com", 7),
    ("regionmanager3@pece555outlook.onmicrosoft.com", 8),
    ("regionmanager3@pece555outlook.onmicrosoft.com", 9),

    ("exec1@pece555outlook.onmicrosoft.com", 1),
    ("exec1@pece555outlook.onmicrosoft.com", 2),
    ("exec1@pece555outlook.onmicrosoft.com", 3),
    ("exec1@pece555outlook.onmicrosoft.com", 4),
    ("exec1@pece555outlook.onmicrosoft.com", 5),
    ("exec1@pece555outlook.onmicrosoft.com", 6),
    ("exec1@pece555outlook.onmicrosoft.com", 7),
    ("exec1@pece555outlook.onmicrosoft.com", 8),
    ("exec1@pece555outlook.onmicrosoft.com", 9),
]

region_schema = "UserEmail string, RegionKey int"
new_regions_df = spark.createDataFrame(
    new_region_mappings, region_schema
)

# Validate that the new region keys exist
valid_keys = {
    row["RegionKey"]
    for row in spark.table("gold_dim_region")
        .select("RegionKey").distinct().collect()
}
requested_keys = {r[1] for r in new_region_mappings}

assert requested_keys.issubset(valid_keys), (
    f"Unknown RegionKeys: {requested_keys - valid_keys}"
)

# Preserve existing rows and add only missing mappings
access_table = spark.table("silver_user_access")
region_table = spark.table("silver_user_region")

missing_access = new_access_df.join(
    access_table.select("UserEmail").distinct(),
    on="UserEmail",
    how="left_anti"
)

missing_regions = new_regions_df.join(
    region_table.select("UserEmail", "RegionKey").distinct(),
    on=["UserEmail", "RegionKey"],
    how="left_anti"
)

# Append only missing rows
if missing_access.count() > 0:
    missing_access.write.mode("append").saveAsTable(
        "silver_user_access"
    )

if missing_regions.count() > 0:
    missing_regions.write.mode("append").saveAsTable(
        "silver_user_region"
    )

print("Security mapping update completed.")
print("New access records added:", missing_access.count())
print("New regional records added:", missing_regions.count())


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Verify the additions**

# CELL ********************


print("Updated account roles:")
spark.table("silver_user_access").filter(
    F.col("UserEmail").isin([
        "regionmanager1@pece555outlook.onmicrosoft.com",
        "regionmanager2@pece555outlook.onmicrosoft.com",
        "regionmanager3@pece555outlook.onmicrosoft.com",
        "exec1@pece555outlook.onmicrosoft.com",
    ])
).orderBy("UserEmail").show(truncate=False)

print("Updated regional assignments:")
spark.table("silver_user_region").filter(
    F.col("UserEmail").isin([
        "regionmanager1@pece555outlook.onmicrosoft.com",
        "regionmanager2@pece555outlook.onmicrosoft.com",
        "regionmanager3@pece555outlook.onmicrosoft.com",
        "exec1@pece555outlook.onmicrosoft.com",
    ])
).groupBy("UserEmail").agg(
    F.countDistinct("RegionKey").alias("RegionCount"),
    F.sort_array(F.collect_set("RegionKey")).alias("RegionKeys")
).orderBy("UserEmail").show(truncate=False)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Add the analyst account**

# CELL ********************


from pyspark.sql import functions as F

email = "analyst1@pece555outlook.onmicrosoft.com"

# Check whether this account already exists
existing = (
    spark.table("silver_user_access")
    .filter(F.lower(F.col("UserEmail")) == email.lower())
    .count()
)

if existing == 0:
    new_user = spark.createDataFrame(
        [(email, "SalesAnalyst")],
        "UserEmail string, AccessLevel string"
    )
    new_user.write.mode("append").saveAsTable(
        "silver_user_access"
    )
    print("Added analyst account.")
else:
    print("Account already exists; no new row inserted.")

# Verify the role
spark.table("silver_user_access").filter(
    F.lower(F.col("UserEmail")) == email.lower()
).show(truncate=False)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Assign the analyst's regional access**

# CELL ********************


email = "analyst1@pece555outlook.onmicrosoft.com"

new_regions = spark.createDataFrame(
    [(email, 1), (email, 2), (email, 3)],
    "UserEmail string, RegionKey int"
)

existing_regions = spark.table("silver_user_region").select(
    "UserEmail", "RegionKey"
).distinct()

missing_regions = new_regions.join(
    existing_regions,
    on=["UserEmail", "RegionKey"],
    how="left_anti"
)

if missing_regions.count() > 0:
    missing_regions.write.mode("append").saveAsTable(
        "silver_user_region"
    )

print("Verified analyst regional mappings:")
spark.table("silver_user_region").filter(
    F.lower(F.col("UserEmail")) == email.lower()
).orderBy("RegionKey").show(truncate=False)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Remove fabrictrail1 account**

# CELL ********************


from pyspark.sql import functions as F

email_to_remove = "fabrictrial1@pece555outlook.onmicrosoft.com"

# Check the records before deletion
print("Records to be removed from silver_user_access:")
spark.table("silver_user_access").filter(
    F.lower(F.col("UserEmail")) == email_to_remove.lower()
).show(truncate=False)

print("Records to be removed from silver_user_region:")
spark.table("silver_user_region").filter(
    F.lower(F.col("UserEmail")) == email_to_remove.lower()
).show(truncate=False)

# Remove only this account from the two security tables
for table_name in ["silver_user_access", "silver_user_region"]:
    df = spark.table(table_name)
    remaining = df.filter(
        F.lower(F.col("UserEmail")) != email_to_remove.lower()
    )

    (remaining.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "false")
        .saveAsTable(table_name))

# Verify the account is gone
for table_name in ["silver_user_access", "silver_user_region"]:
    count = spark.table(table_name).filter(
        F.lower(F.col("UserEmail")) == email_to_remove.lower()
    ).count()
    print(f"{table_name}: remaining matching records = {count}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


from pyspark.sql import functions as F

# Remove placeholder-domain accounts from both security tables
for table_name in ["silver_user_access", "silver_user_region"]:
    df = spark.table(table_name)

    # Show affected rows before removal
    print(f"Rows to remove from {table_name}:")
    df.filter(
        F.lower(F.trim(F.col("UserEmail"))).endswith("@example.com")
    ).show(truncate=False)

    # Keep all other accounts
    remaining = df.filter(
        ~F.lower(F.trim(F.col("UserEmail"))).endswith("@example.com")
    )

    (remaining.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "false")
        .saveAsTable(table_name))

# Verify that no placeholder accounts remain
for table_name in ["silver_user_access", "silver_user_region"]:
    count = spark.table(table_name).filter(
        F.lower(F.trim(F.col("UserEmail"))).endswith("@example.com")
    ).count()

    print(f"{table_name}: remaining @example.com records = {count}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
