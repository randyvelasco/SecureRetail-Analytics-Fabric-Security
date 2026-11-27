# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "79736691-2c22-4d76-9108-18a70332aab1",
# META       "default_lakehouse_name": "lh_secure_retail",
# META       "default_lakehouse_workspace_id": "b2e3a70e-8017-45b8-922f-bd42e316f776",
# META       "known_lakehouses": [
# META         {
# META           "id": "79736691-2c22-4d76-9108-18a70332aab1"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************


# =====================================================
# Microsoft Fabric
# Cross-Workspace Lakehouse Delta Table Copy
# Supports schema-organized Lakehouse tables
# =====================================================

from notebookutils import mssparkutils
from pyspark.sql.types import StructType, StructField, StringType

# SOURCE
source_workspace_id = "7c133c6b-ccdd-439d-b354-f49c9c175a86"
source_lakehouse_id = "c41b3337-6220-4296-afd2-5a57cf015e22"

# DESTINATION
destination_workspace_id = "b2e3a70e-8017-45b8-922f-bd42e316f776"
destination_lakehouse_id = "79736691-2c22-4d76-9108-18a70332aab1"

# ONELAKE PATHS
source_tables_path = (
    f"abfss://{source_workspace_id}"
    f"@onelake.dfs.fabric.microsoft.com/"
    f"{source_lakehouse_id}/Tables"
)

destination_tables_path = (
    f"abfss://{destination_workspace_id}"
    f"@onelake.dfs.fabric.microsoft.com/"
    f"{destination_lakehouse_id}/Tables"
)

# -----------------------------------------------------
# 1. RECURSIVELY DISCOVER DELTA TABLES
# -----------------------------------------------------

def discover_delta_tables(path):

    discovered = []

    for item in mssparkutils.fs.ls(path):

        current_path = item.path.rstrip("/")

        if not item.isDir:
            continue

        # Check whether this directory is a Delta table
        delta_log_path = current_path + "/_delta_log"

        if mssparkutils.fs.exists(delta_log_path):

            relative_path = current_path[len(source_tables_path):].strip("/")

            discovered.append(relative_path)

            print("Found Delta table:", relative_path)

        else:

            # Continue searching subdirectories
            discovered.extend(discover_delta_tables(current_path))

    return discovered


table_names = discover_delta_tables(source_tables_path)

print("\nTotal Delta tables found:", len(table_names))

# -----------------------------------------------------
# 2. COPY DELTA TABLES
# -----------------------------------------------------

results = []

for table_name in table_names:

    source_path = f"{source_tables_path}/{table_name}"
    destination_path = f"{destination_tables_path}/{table_name}"

    try:

        print(f"\nCopying: {table_name}")

        df = spark.read.format("delta").load(source_path)

        # Preserve schema directory structure
        df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(destination_path)

        print(f"SUCCESS: {table_name}")

        results.append((table_name, "SUCCESS", ""))

    except Exception as e:

        error_message = str(e)[:1000]

        print(f"FAILED: {table_name}")
        print(error_message)

        results.append((table_name, "FAILED", error_message))

# -----------------------------------------------------
# 3. COPY SUMMARY
# -----------------------------------------------------

schema = StructType([
    StructField("TableName", StringType(), False),
    StructField("Status", StringType(), False),
    StructField("ErrorMessage", StringType(), True)
])

if results:

    summary_df = spark.createDataFrame(results, schema)

    display(summary_df)

    successful = sum(1 for r in results if r[1] == "SUCCESS")
    failed = sum(1 for r in results if r[1] == "FAILED")

    print("\nCOPY SUMMARY")
    print("Discovered:", len(table_names))
    print("Successful:", successful)
    print("Failed:", failed)

else:

    print("No Delta tables discovered. Nothing was copied.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# =====================================================
# Microsoft Fabric
# Cross-Workspace Lakehouse FILES Copy
# Recursive copy with folder structure preservation
# =====================================================

from notebookutils import mssparkutils
from pyspark.sql.types import StructType, StructField, StringType

# SOURCE
source_workspace_id = "7c133c6b-ccdd-439d-b354-f49c9c175a86"
source_lakehouse_id = "c41b3337-6220-4296-afd2-5a57cf015e22"

# DESTINATION
destination_workspace_id = "b2e3a70e-8017-45b8-922f-bd42e316f776"
destination_lakehouse_id = "79736691-2c22-4d76-9108-18a70332aab1"

# ONELAKE FILE PATHS
source_files_path = (
    f"abfss://{source_workspace_id}"
    f"@onelake.dfs.fabric.microsoft.com/"
    f"{source_lakehouse_id}/Files"
)

destination_files_path = (
    f"abfss://{destination_workspace_id}"
    f"@onelake.dfs.fabric.microsoft.com/"
    f"{destination_lakehouse_id}/Files"
)

# -----------------------------------------------------
# 1. RECURSIVELY DISCOVER FILES
# -----------------------------------------------------

def discover_files(path):

    discovered = []

    for item in mssparkutils.fs.ls(path):

        current_path = item.path.rstrip("/")

        if item.isDir:

            # Preserve folder structure, including empty folders
            relative_path = current_path[len(source_files_path):].strip("/")

            discovered.append(("DIRECTORY", relative_path))

            discovered.extend(discover_files(current_path))

        else:

            relative_path = current_path[len(source_files_path):].strip("/")

            discovered.append(("FILE", relative_path))

    return discovered


items = discover_files(source_files_path)

files = [x for x in items if x[0] == "FILE"]
folders = [x for x in items if x[0] == "DIRECTORY"]

print("Folders discovered:", len(folders))
print("Files discovered:", len(files))

# -----------------------------------------------------
# 2. CREATE DESTINATION FOLDERS
# -----------------------------------------------------

mssparkutils.fs.mkdirs(destination_files_path)

for item_type, relative_path in folders:

    destination_path = (
        f"{destination_files_path}/{relative_path}"
    )

    mssparkutils.fs.mkdirs(destination_path)

# -----------------------------------------------------
# 3. COPY FILES
# -----------------------------------------------------

results = []

for item_type, relative_path in files:

    source_path = f"{source_files_path}/{relative_path}"
    destination_path = f"{destination_files_path}/{relative_path}"

    try:

        print(f"Copying: {relative_path}")

        # Create destination parent folder
        parent_path = destination_path.rsplit("/", 1)[0]

        mssparkutils.fs.mkdirs(parent_path)

        # Remove existing destination file for overwrite
        if mssparkutils.fs.exists(destination_path):
            mssparkutils.fs.rm(destination_path)

        # Copy individual file
        success = mssparkutils.fs.cp(
            source_path,
            destination_path
        )

        if success:
            print(f"SUCCESS: {relative_path}")
            results.append((relative_path, "SUCCESS", ""))
        else:
            raise Exception("Copy operation returned False")

    except Exception as e:

        error_message = str(e)[:1000]

        print(f"FAILED: {relative_path}")
        print(error_message)

        results.append(
            (relative_path, "FAILED", error_message)
        )

# -----------------------------------------------------
# 4. COPY SUMMARY
# -----------------------------------------------------

schema = StructType([
    StructField("FilePath", StringType(), False),
    StructField("Status", StringType(), False),
    StructField("ErrorMessage", StringType(), True)
])

if results:

    summary_df = spark.createDataFrame(results, schema)

    display(summary_df)

    successful = sum(1 for r in results if r[1] == "SUCCESS")
    failed = sum(1 for r in results if r[1] == "FAILED")

    print("\nFILE COPY SUMMARY")
    print("Folders discovered:", len(folders))
    print("Files discovered:", len(files))
    print("Successful:", successful)
    print("Failed:", failed)

else:

    print("No files found to copy.")

print("\nLakehouse Files copy operation completed.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
