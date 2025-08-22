# pyspark_minio_eda.py
# This script demonstrates a full ETL-like process:
# 1. Initialize a Spark Session configured for MinIO.
# 2. Ensure the target S3 bucket exists.
# 3. Read a local CSV file into a Spark DataFrame.
# 4. Write the DataFrame to MinIO in Parquet format.
# 5. Read the data back from MinIO.
# 6. Perform and print basic EDA results.

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, dayofweek, avg, count, desc
import boto3
from botocore.client import Config

# --- Configuration ---
MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "tripdata"
LOCAL_CSV_PATH = "/home/jovyan/data/BEAD-Rebu_TripData.csv"
MINIO_PARQUET_PATH = f"s3a://{BUCKET_NAME}/BEAD-Rebu_TripData.parquet"


def initialize_spark_session():
    """Initializes and returns a Spark Session configured for MinIO."""
    print("Initializing Spark Session...")
    spark = (
        SparkSession.builder.appName("PySparkMinIOEDA")
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )
    print("Spark Session created successfully.")
    return spark


def ensure_bucket_exists():
    """Uses boto3 to create the MinIO bucket if it doesn't already exist."""
    print(f"Checking if bucket '{BUCKET_NAME}' exists...")
    s3 = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created successfully.")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{BUCKET_NAME}' already exists.")
    except Exception as e:
        print(f"An error occurred while creating bucket: {e}")
        raise


def perform_eda(df):
    """Performs and prints the results of several EDA queries on the DataFrame."""
    print("\n--- Starting Exploratory Data Analysis (EDA) ---")

    # --- Data Cleaning and Transformation ---
    df_transformed = df.withColumn("TripDate", to_date(col("Date"), 'd-MMM-yy'))

    # --- EDA Questions ---

    # 1. What is the total number of trips?
    total_trips = df_transformed.count()
    print(f"\n1. Total number of trips: {total_trips}")

    # 2. What is the average trip distance?
    avg_distance = df_transformed.select(avg("Distance Travelled")).first()[0]
    print(f"2. Average trip distance: {avg_distance:.2f} km")

    # 3. What are the top 5 most popular pickup districts?
    print("\n3. Top 5 most popular pickup districts:")
    popular_pickups = df_transformed.groupBy("Pickup District").agg(count("*").alias("trip_count")) \
        .orderBy(desc("trip_count"))
    popular_pickups.show(5)

    # 4. How many trips occur on each day of the week?
    print("4. Number of trips per day of the week (1=Sun, 2=Mon, ...):")
    trips_by_day = df_transformed.withColumn("DayOfWeek", dayofweek(col("TripDate"))) \
        .groupBy("DayOfWeek").agg(count("*").alias("trip_count")) \
        .orderBy("DayOfWeek")
    trips_by_day.show()

    # 5. What is the busiest hour of the day for trips?
    print("5. Busiest hour of the day:")
    trips_by_hour = df_transformed.groupBy("Hour of Day").agg(count("*").alias("trip_count")) \
        .orderBy(desc("trip_count"))
    trips_by_hour.show(1)

    print("--- EDA Finished ---")


def main():
    """Main function to run the ETL and EDA process."""
    spark = None
    try:
        spark = initialize_spark_session()
        ensure_bucket_exists()

        # Read local CSV
        print(f"Reading local CSV file from {LOCAL_CSV_PATH}...")
        df_local = spark.read.csv(LOCAL_CSV_PATH, header=True, inferSchema=True)
        print("Local CSV file read successfully.")
        df_local.show(5, truncate=False)

        # Write to MinIO
        print(f"Writing DataFrame to MinIO at {MINIO_PARQUET_PATH}...")
        df_local.write.mode("overwrite").parquet(MINIO_PARQUET_PATH)
        print("DataFrame successfully written to MinIO.")

        # Read back from MinIO
        print(f"Reading data back from MinIO...")
        df_minio = spark.read.parquet(MINIO_PARQUET_PATH)
        print("Data read back from MinIO successfully.")
        df_minio.printSchema()

        # Perform EDA
        perform_eda(df_minio)

    except Exception as e:
        print(f"An error occurred during the Spark job: {e}")
    finally:
        if spark:
            print("Stopping Spark Session.")
            spark.stop()


if __name__ == "__main__":
    main()
