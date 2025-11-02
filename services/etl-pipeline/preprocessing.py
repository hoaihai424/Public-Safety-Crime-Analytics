from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc, when, lower, trim, to_timestamp, monotonically_increasing_id, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType, StringType, StructType, StructField, FloatType, DateType
import pandas as pd
import os
from pathlib import Path
from math import radians, cos, sin, asin, sqrt

# Initialize Spark session
spark = (
    SparkSession.builder
    .appName("CrimeDataPreprocessing")
    .master("local[4]") 
    .config("spark.executor.memory", "2g")  
    .config("spark.driver.memory", "2g")    
    .config("spark.sql.shuffle.partitions", "8")  
    .getOrCreate()
)

# Get environment variables
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = os.getenv("CASSANDRA_PORT", "9042")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "public_safety")   
CASSANDRA_DATABASE = os.getenv("CASSANDRA_DATABASE", "public_safety")


# Get root directory
root_dir = Path(__file__).parent.parent.parent
data_dir = root_dir/ "data"

# Load the dataset
df = spark.read.csv(f"{data_dir}/raw/crime_data.csv", header=True, inferSchema=True)


# Reduce data size by selecting relevant columns
df = df.select(
    col("ID").alias("id"),
    col("Case Number").alias("case_number"),
    col("Date").alias("date"),
    col("Block").alias("block"),
    col("IUCR").alias("iucr"),
    col("Primary Type").alias("primary_type"),
    col("Description").alias("description"),
    col("Location Description").alias("location_description"),
    col("Arrest").alias("arrest"),
    col("Domestic").alias("domestic"),
    col("Beat").alias("beat"),
    col("District").alias("district"),
    col("Ward").alias("ward"),
    col("Community Area").alias("community_area"),
    col("FBI Code").alias("fbi_code"),
    col("Latitude").alias("latitude"),
    col("Longitude").alias("longitude"),
    col("Location").alias("location")
)

# Data type conversions and cleaning
df = df.withColumn("arrest", col("arrest").cast("boolean"))
df = df.withColumn(
    "arrest", 
    when(lower(trim(col("arrest"))) == "true", True)
    .when(lower(trim(col("arrest"))) == "false", False)
    .otherwise(None)
)

df = df.withColumn("domestic", col("domestic").cast("boolean"))
df = df.withColumn(
    "domestic", 
    when(lower(trim(col("domestic"))) == "true", True)
    .when(lower(trim(col("domestic"))) == "false", False)
    .otherwise(None)
)

df = df.withColumn(
    "date",
    to_timestamp(col("date"), "MM/dd/yyyy hh:mm:ss a")
)

# Handle nulls and missing values
df = df.withColumn("longitude", when(col("longitude").isNull(), 0.0).otherwise(col("longitude")))\
         .withColumn("latitude", when(col("latitude").isNull(), 0.0).otherwise(col("latitude")))\
            .withColumn("location", when(col("location").isNull(), "(0.0, 0.0)").otherwise(col("location")))\
                .withColumn("location_description", when(col("location_description").isNull(), "Unknown").otherwise(col("location_description")))\
                    .withColumn("district", when(col("district").isNull(), -1).otherwise(col("district")))\
                        .withColumn("ward", when(col("ward").isNull(), -1).otherwise(col("ward")))\
                            .withColumn("community_area", when(col("community_area").isNull(), -1).otherwise(col("community_area")))

df.cache()

# Normalize and enrich data 
# Create primary type table
primary_types_df = df.select("primary_type").distinct().\
                    withColumn("id", monotonically_increasing_id() + 1).withColumnRenamed("primary_type", "name")
primary_types_df = primary_types_df.select("id", "name")


# Create crime table
crime_df = df.select("iucr", "fbi_code", "primary_type", "description").distinct().\
            withColumn("id", monotonically_increasing_id() + 1)
crime_df = crime_df.alias("c").join(
                primary_types_df.alias("pt"),
                col("c.primary_type") == col("pt.name"),
                how="left"   
            ).select(
                col("c.id"),
                col("c.iucr").alias("iucr"),
                col("pt.id").alias("primary_type"),
                col("c.description").alias("description"),
                col("c.fbi_code").alias("fbi_code")
            ).orderBy("id")


# Create location table
locations = df.select("location_description", "block", "latitude", "longitude", "location").distinct().withColumn("id", monotonically_increasing_id()+1)
locations = locations.select("id", "location_description", "block", "latitude", "longitude", "location")


# Create patrol unit table
patrol_units = df.select("beat", "district", "ward", "community_area").distinct().withColumn("id", monotonically_increasing_id()+1)
patrol_units = patrol_units.select("id", "beat", "district", "ward", "community_area").withColumn("beat", col("beat").cast(IntegerType()))\
    .withColumn("district", col("district").cast(IntegerType()))\
    .withColumn("ward", col("ward").cast(IntegerType()))\
    .withColumn("community_area", col("community_area").cast(IntegerType()))\
    .withColumnRenamed("Community Area", "community_area").sort("id")


# Create case table
joined_crime_df = crime_df.alias("c").join(
    primary_types_df.alias("pt"),
    col("c.primary_type") == col("pt.id"),
    how="left"
).select(
    col("c.id"),
    col("iucr"),
    col("pt.name").alias("primary_type"),
    col("description"),
    col("fbi_code")
).orderBy("id")

case_df = df.alias("df").join(
    joined_crime_df.alias("c"),
    (col("df.iucr") == col("c.iucr")) &
    (col("df.primary_type") == col("c.primary_type")) &
    (col("df.description") == col("c.description")) &
    (col("df.fbi_code") == col("c.fbi_code")),
    how="left"
).join(
    locations.alias("l"),
    (col("df.location_description") == col("l.location_description")) &
    (col("df.block") == col("l.block")) &
    (col("df.latitude") == col("l.latitude")) &
    (col("df.longitude") == col("l.longitude")) &
    (col("df.location") == col("l.location")),
    how="left"
).join(
    patrol_units.alias("p"),
    (col("df.beat") == col("p.beat")) &
    (col("df.district") == col("p.district")) &
    (col("df.ward") == col("p.ward")) &
    (col("df.community_area") == col("p.community_area")),
    how="left"
)
case_df = case_df.select(
    col("df.id").alias("id"),
    col("df.case_number").alias("case_number"),
    col("df.date").alias("date"),
    col("c.id").alias("crime_id"),
    col("l.id").alias("location_id"),
    col("p.id").alias("patrol_unit_id"),
    col("df.arrest").alias("arrest"),
    col("df.domestic").alias("domestic")
).orderBy("id")
case_df.show(10)
print(f"Total records in case table: {case_df.count()}")

# Export processed data to CSV
primary_types_df.coalesce(1).write.csv(f"{data_dir}/processed/primary_type", header=True, mode="overwrite")
crime_df.coalesce(1).write.csv(f"{data_dir}/processed/crime", header=True, mode="overwrite")
locations.coalesce(1).write.csv(f"{data_dir}/processed/location", header=True, mode="overwrite")
patrol_units.coalesce(1).write.csv(f"{data_dir}/processed/patrol_unit", header=True, mode="overwrite")
case_df.coalesce(1).write.csv(f"{data_dir}/processed/case", header=True, mode="overwrite")  

# Load into Cassandra db
def import_data_to_db(df, keyspace, table):
    try:
        df.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table=table, keyspace=keyspace) \
            .mode("append") \
            .save()
    except Exception as e:
        print(f"Error importing data to {keyspace}.{table}: {e}")

import_data_to_db(primary_types_df, CASSANDRA_KEYSPACE, "primary_type")
import_data_to_db(crime_df, CASSANDRA_KEYSPACE, "crime")
import_data_to_db(locations, CASSANDRA_KEYSPACE, "location")
import_data_to_db(patrol_units, CASSANDRA_KEYSPACE, "patrol_unit")
import_data_to_db(case_df, CASSANDRA_KEYSPACE, "case")

spark.stop()