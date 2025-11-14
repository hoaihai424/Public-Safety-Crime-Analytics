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
import os
from dotenv import load_dotenv

# Initialize Spark session and load environment variables
spark = (
    SparkSession.builder
    .appName("CrimeDataPreprocessing")
    .master("local[4]") 
    .config("spark.executor.memory", "2g")  
    .config("spark.driver.memory", "2g")    
    .config("spark.sql.shuffle.partitions", "16")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.autoBroadcastJoinThreshold", "10485760")
    .getOrCreate()
)

def write_single_csv(df, output_path):
    """Write DataFrame to a single CSV file with specific name."""
    import shutil
    temp_dir = f"{output_path}_temp"
    
    try:
        # Remove existing temp directory if it exists
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        
        # Write to temporary directory
        df.coalesce(1).write.mode("overwrite").option("header", "true").csv(temp_dir)
        
        # Find the CSV file (Spark creates part-*.csv files)
        csv_file = None
        for file in Path(temp_dir).iterdir():
            if file.suffix == '.csv' and file.name.startswith('part-'):
                csv_file = file
                break
        
        if csv_file:
            # Remove existing output file if it exists
            if Path(output_path).exists():
                Path(output_path).unlink()
            
            # Move and rename the file
            shutil.move(str(csv_file), output_path)
            print(f"✓ Wrote to: {output_path}")
        else:
            raise FileNotFoundError("No CSV file generated")
            
    finally:
        # Clean up temporary directory
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

try:
    # Get root directory
    root_dir = Path(__file__).parent.parent.parent.parent
    data_dir = root_dir/ "data"
    print(f"Data directory: {data_dir}")

    # Load the dataset
    df = spark.read.csv(f"{data_dir}/raw/crime_data.csv", header=True, inferSchema=True)


    # Reduce data size and cleaning values
    df = df.select(
        col("ID").alias("id"),
        col("Case Number").alias("case_number"),
        to_timestamp(col("Date"), "MM/dd/yyyy hh:mm:ss a").alias("datetime"),
        col("Block").alias("block"),
        col("IUCR").alias("iucr"),
        col("Primary Type").alias("primary_type"),
        col("Description").alias("description"),
        when(col("Location Description").isNull(), "Unknown").otherwise(col("Location Description")).alias("location_description"),
        when(lower(trim(col("Arrest"))) == "true", 1).otherwise(0).cast(IntegerType()).alias("arrest"),
        when(lower(trim(col("Domestic"))) == "true", 1).otherwise(0).cast(IntegerType()).alias("domestic"),
        when(col("Beat").isNull(), -1).otherwise(col("Beat").cast(IntegerType())).alias("beat"),
        when(col("District").isNull(), -1).otherwise(col("District").cast(IntegerType())).alias("district"),
        when(col("Ward").isNull(), -1).otherwise(col("Ward").cast(IntegerType())).alias("ward"),
        when(col("Community Area").isNull(), -1).otherwise(col("Community Area").cast(IntegerType())).alias("community_area"),
        col("FBI Code").alias("fbi_code"),
        when(col("Latitude").isNull(), 0.0).otherwise(col("Latitude").cast(DoubleType())).alias("latitude"),
        when(col("Longitude").isNull(), 0.0).otherwise(col("Longitude").cast(DoubleType())).alias("longitude"),
        when(col("Location").isNull(), "(0.0, 0.0)").otherwise(col("Location")).alias("location")
    )

    df = df.withColumn("date", col("datetime").cast("date")) \
        .withColumn("time", date_format(col("datetime"), "HH:mm:ss")) \
        .drop("datetime") 


    # Normalize and enrich data 
    # Create dim date 
    date_schema = StructType([
        StructField("id", StringType(), True),
        StructField("date", DateType(), True),
        StructField("month", IntegerType(), True),
        StructField("quarter", IntegerType(), True),
        StructField("year", IntegerType(), True),
        StructField("day_of_week", StringType(), True),
        StructField("is_weekend", BooleanType(), True)
    ])

    date_data = []
    start_date = pd.to_datetime("2001-01-01")
    end_date = pd.to_datetime("2025-12-31")
    date_range = pd.date_range(start=start_date, end=end_date)
    for single_date in date_range:
        date_id = single_date.strftime("%Y%m%d")
        month = single_date.month
        quarter = (single_date.month - 1) // 3 + 1
        year = single_date.year
        day_of_week = single_date.strftime("%A")
        is_weekend = day_of_week in ["Saturday", "Sunday"]
        
        date_data.append((date_id, single_date.date(), month, quarter, year, day_of_week, is_weekend))

    date_df = spark.createDataFrame(date_data, schema=date_schema)

    write_single_csv(date_df, f"{data_dir}/processed/dim_date.csv")
    date_df.unpersist()


    # Create dim time
    time_schema = StructType([
        StructField("id", StringType(), True),
        StructField("hour", IntegerType(), True),
        StructField("minute", IntegerType(), True),
        StructField("second", IntegerType(), True)
    ])

    time_data = []
    for hour in range(24):
        for minute in range(60):
            for second in range(60):
                time_id = f"{hour:02}{minute:02}{second:02}"
                time_data.append((time_id, hour, minute, second))

    time_df = spark.createDataFrame(time_data, schema=time_schema)

    write_single_csv(time_df, f"{data_dir}/processed/dim_time.csv")
    time_df.unpersist()


    # Create dim primary type table
    primary_types_df = df.select("primary_type").distinct().\
                        withColumn("id", monotonically_increasing_id() + 1).withColumnRenamed("primary_type", "name")
    primary_types_df = primary_types_df.select("id", "name")

    write_single_csv(primary_types_df, f"{data_dir}/processed/dim_primary_type.csv")
    primary_types_df.unpersist()


    # Create dim crime table
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

    write_single_csv(crime_df, f"{data_dir}/processed/dim_crime.csv")
    crime_df.unpersist()


    # Create dim location table
    locations = df.select("location_description", "block", "latitude", "longitude", "location").distinct().withColumn("id", monotonically_increasing_id()+1)
    locations = locations.select("id", "location_description", "block", "latitude", "longitude", "location")

    write_single_csv(locations, f"{data_dir}/processed/dim_location.csv")
    locations.unpersist()


    # Create dim patrol unit table
    patrol_units = df.select("beat", "district", "ward", "community_area").distinct().withColumn("id", monotonically_increasing_id()+1)
    patrol_units = patrol_units.select("id", "beat", "district", "ward", "community_area").withColumn("beat", col("beat").cast(IntegerType()))\
        .withColumn("district", col("district").cast(IntegerType()))\
        .withColumn("ward", col("ward").cast(IntegerType()))\
        .withColumn("community_area", col("community_area").cast(IntegerType()))\
        .withColumnRenamed("Community Area", "community_area").sort("id")

    write_single_csv(patrol_units, f"{data_dir}/processed/dim_patrol_unit.csv")
    patrol_units.unpersist()


    # Create fact case table
    joined_crime_df = crime_df.alias("c").join(
        broadcast(primary_types_df.alias("pt")),
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
        broadcast(joined_crime_df.alias("c")),
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
    ).join(
        date_df.alias("d"),
        col("df.date") == col("d.date"),
        how="left"
    ).join(
        time_df.alias("t"),
        concat(
            lpad(date_format(col("df.time"), "HH"), 2, "0"),
            lpad(date_format(col("df.time"), "mm"), 2, "0"),
            lpad(date_format(col("df.time"), "ss"), 2, "0")
        ) == col("t.id"),
        how="left"
    )


    case_df = case_df.select(
        col("df.id").alias("id"),
        col("df.case_number").alias("case_number"),
        col("d.id").alias("date_id"),
        col("t.id").alias("time_id"),
        col("c.id").alias("crime_id"),
        col("l.id").alias("location_id"),
        col("p.id").alias("patrol_unit_id"),
        col("df.arrest").alias("arrest"),
        col("df.domestic").alias("domestic")
    ).orderBy("id")

    write_single_csv(case_df, f"{data_dir}/processed/fact_case.csv")

    # Clean up memory
    case_df.unpersist()
except Exception as e:
    print(f"An error occurred during ETL process: {e}")
finally:
    spark.stop()