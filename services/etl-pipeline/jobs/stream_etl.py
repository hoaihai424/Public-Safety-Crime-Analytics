from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, lower, trim, to_timestamp, monotonically_increasing_id, 
    year, month, quarter, dayofweek, date_format, hour, minute, second,
    concat, lpad, broadcast
)
import pandas as pd
from pyspark.sql.types import IntegerType, StringType, StructType, StructField, DateType, BooleanType, DoubleType
from pathlib import Path
import shutil
import clickhouse_connect
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_PORT", "8123")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "crime_analytics")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")

def createClickHouseClient():
    try:
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=int(CLICKHOUSE_PORT),
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DB
        )

        # Test connection
        version = client.server_version
        print(f"Connected to ClickHouse server version: {version}")
        return client
    except Exception as e:
        print(f"Error connecting to ClickHouse: {e}")
        raise e
    
def write_data(df, table_name, client):
    try:
        df = df.toPandas()
        client.insert_df(table_name, df)
        print(f"Data inserted into {table_name} successfully.")
    except Exception as e:
        print(f"Error inserting data into {table_name}: {e}")
        raise e
    
# Init spark streaming session and ClickHouse client
spark = SparkSession.builder \
    .appName("StreamETL") \
    .master("local[4]") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "16") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

client = createClickHouseClient()