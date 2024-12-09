import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import (
    col,
    regexp_replace,
    trim,
    current_timestamp
)
from pyspark.sql.types import StringType

# -----------------------------------
print("1. Retrieve Job Arguments")
# -----------------------------------
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    's3_input_path',
    'dynamodb_table',
    'region',
    'opensearch_domain'
])

print(f"JOB_NAME: {args['JOB_NAME']}")
print(f"s3_input_path: {args['s3_input_path']}")
print(f"dynamodb_table: {args['dynamodb_table']}")
print(f"region: {args['region']}")
print(f"opensearch_domain: {args['opensearch_domain']}")
print("")

# -----------------------------------
print("2. Initialize Spark and Glue Contexts")
# -----------------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# -----------------------------------
print("3. Read Data Directly from S3 with Proper CSV Options")
# -----------------------------------
# Read all columns as strings to simplify cleaning
datasource = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "false") \
    .option("multiLine", "true") \
    .option("ignoreLeadingWhiteSpace", "true") \
    .option("ignoreTrailingWhiteSpace", "true") \
    .load(args['s3_input_path'])

df = datasource

# Strip whitespace and newline characters from column names
df = df.toDF(*[c.strip() for c in df.columns])

# Drop the '_c0' column if present
if "_c0" in df.columns:
    df = df.drop("_c0")

# -----------------------------------
print("4. Data Cleaning")
# -----------------------------------
# Remove extra quotes and trim whitespace from all string columns
string_cols = [f.name for f in df.schema.fields if f.dataType == StringType()]

for c in string_cols:
    # Remove double quotes and trim
    df = df.withColumn(c, trim(regexp_replace(col(c), '"', '')))

# Add an 'id' column from 'SAM Number' for DynamoDB key
if "SAM Number" not in df.columns:
    raise ValueError("SAM Number column is missing. Cannot set key for DynamoDB.")

df = df.withColumn("id", col("SAM Number"))

# -----------------------------------
print("5. Data Deduplication and Validation")
# -----------------------------------
total_records_before = df.count()
print(f"Total records before deduplication: {total_records_before}")

# Filter out records with null or empty 'id'
df = df.filter(col("id").isNotNull() & (trim(col("id")) != ""))

# Drop duplicates based on 'id'
df = df.dropDuplicates(['id'])

total_records_after = df.count()
print(f"Total records after deduplication: {total_records_after}")

duplicates_removed = total_records_before - total_records_after
print(f"Number of duplicate records removed: {duplicates_removed}")

# -----------------------------------
print("6. Write Cleaned Data to DynamoDB")
# -----------------------------------
dynamodb_frame = DynamicFrame.fromDF(df, glueContext, "dynamodb_frame")

glueContext.write_dynamic_frame.from_options(
    frame=dynamodb_frame,
    connection_type="dynamodb",
    connection_options={
        "dynamodb.output.tableName": args['dynamodb_table'],
        "dynamodb.throughput.write.percent": "0.5",
        "dynamodb.region": args['region']
    }
)

# -----------------------------------
print("7. Commit the Job")
# -----------------------------------
job.commit()

print("Data load completed successfully.")