from pyspark.sql import SparkSession
import clickhouse_connect
from datetime import datetime, date, timedelta
import json

# Define topic to table mapping
TOPIC_TABLE_MAP = {
    "cdc.public.primary_type": "dim_primary_type",
    "cdc.public.crime": "dim_crime",
    "cdc.public.location": "dim_location",
    "cdc.public.patrol_unit": "dim_patrol_unit",
    "cdc.public.case_report": "fact_case",
}

def convert_date(date_input):
    """Handle both int and string dates, return String ID for ClickHouse"""
    try:
        if isinstance(date_input, int):
            d = date(1970, 1, 1) + timedelta(days=date_input)
        elif isinstance(date_input, str):
            if 'T' in date_input:
                dt = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
                d = dt.date()
            else:
                dt = datetime.strptime(date_input, "%Y-%m-%d")
                d = dt.date()
        else:
            # Default fallback
            d = date(1970, 1, 1)

        id_str = d.strftime("%Y%m%d") 
        
        month = d.month
        quarter = (d.month - 1) // 3 + 1
        year = d.year
        day_of_week = d.isoweekday()
        is_weekend = 1 if day_of_week >= 6 else 0

        return {
            "id": id_str,  
            "date": d.strftime("%Y-%m-%d"),
            "month": month,
            "quarter": quarter,
            "year": year,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend
        }
    except Exception as e:
        print(f"[ERROR] Date conversion failed: {e}", flush=True)
        return {
            "id": "19700101", 
            "date": "1970-01-01", 
            "month": 1, "quarter": 1, "year": 1970, "day_of_week": 1, "is_weekend": 0
        }

def convert_time(time_input):
    """Handle time, return String ID for ClickHouse"""
    try:
        if isinstance(time_input, int):
            seconds_total = time_input // 1000000
            m, s = divmod(seconds_total, 60)
            h, m = divmod(m, 60)
        else:
            h, m, s = str(time_input).split(":")
            h, m, s = int(h), int(m), int(s)

        id_str = f"{h:02d}{m:02d}{s:02d}"

        return {
            "id": id_str, 
            "hour": h,
            "minute": m,
            "second": s
        }
    except Exception as e:
        print(f"[ERROR] Time conversion failed: {e}", flush=True)
        return {"id": "000000", "hour": 0, "minute": 0, "second": 0} 

def map_case_report(data):
    date_dim = convert_date(data.get("date"))
    time_dim = convert_time(data.get("time"))

    arrest_val = 1 if data.get("arrest") else 0
    domestic_val = 1 if data.get("domestic") else 0

    return {
        "fact": {
            "id": int(data["id"]),
            "case_number": str(data["case_number"]),
            "date_id": str(date_dim["id"]), 
            "time_id": str(time_dim["id"]), 
            "crime_id": int(data["crime_id"]) if data.get("crime_id") else None,
            "location_id": int(data["location_id"]) if data.get("location_id") else None,
            "patrol_unit_id": int(data["patrol_unit_id"]) if data.get("patrol_unit_id") else None,
            "arrest": arrest_val,
            "domestic": domestic_val,
        },
        "dim_date": date_dim,
        "dim_time": time_dim
    }

def map_primary_type(data):
    return {
        "id": int(data["id"]),
        "name": str(data["name"])
    }

def map_crime(data):
    return {
        "id": int(data["id"]),
        "iucr": str(data["iucr"]),
        "primary_type": int(data["primary_type"]),
        "description": str(data["description"]),
        "fbi_code": str(data["fbi_code"]),
    }

def map_location(data):
    return {
        "id": int(data["id"]),
        "location_description": str(data["location_description"]),
        "block": str(data["block"]),
        "location": str(data["location"]),
    }

def map_patrol_unit(data):
    return {
        "id": int(data["id"]),
        "beat": int(data["beat"]),
        "district": int(data["district"]),
        "ward": int(data["ward"]),
        "community_area": int(data["community_area"]),
    }

def write_data(table, rows, client):
    try:
        if len(rows) == 0:
            print(f"[WARN] No rows to insert for table {table}", flush=True)
            return

        print(f"[INFO] Writing {len(rows)} rows to {table}", flush=True)
        
        # Define column order and types for each table
        table_schemas = {
            "dim_primary_type": {
                "columns": ["id", "name"],
                "types": ["Int32", "String"]
            },
            "dim_crime": {
                "columns": ["id", "iucr", "primary_type", "description", "fbi_code"],
                "types": ["Int32", "String", "Int32", "String", "String"]
            },
            "dim_location": {
                "columns": ["id", "location_description", "block", "location"],
                "types": ["Int32", "String", "String", "String"]
            },
            "dim_patrol_unit": {
                "columns": ["id", "beat", "district", "ward", "community_area"],
                "types": ["Int32", "Int32", "Int32", "Int32", "Int32"]
            },
            "dim_date": {
                "columns": ["id", "date", "month", "quarter", "year", "day_of_week", "is_weekend"],
                "types": ["String", "String", "Int8", "Int8", "Int16", "Int8", "Int8"]
            },
            "dim_time": {
                "columns": ["id", "hour", "minute", "second"],
                "types": ["String", "Int8", "Int8", "Int8"]
            },
            "fact_case": {
                "columns": ["id", "case_number", "date_id", "time_id", "crime_id", "location_id", "patrol_unit_id", "arrest", "domestic"],
                "types": ["Int32", "String", "String", "String", "Int32", "Int32", "Int32", "Int8", "Int8"]
            }
        }
        
        if table not in table_schemas:
            print(f"[ERROR] Unknown table: {table}", flush=True)
            return
        
        schema = table_schemas[table]
        columns = schema["columns"]
        
        # Convert to list of tuples in correct column order
        data_tuples = []
        for row in rows:
            data_tuples.append(tuple(row[col] for col in columns))
        
        # Insert with column_type_names to force correct types
        client.insert(
            table=f"crime_analytics.{table}",
            data=data_tuples,
            column_names=columns,
            column_type_names=schema["types"]  
        )
        
        print(f"[SUCCESS] ✓ Inserted {len(rows)} rows into {table}", flush=True)
        
    except Exception as e:
        print(f"[ERROR] Failed to write to {table}: {e}", flush=True)
        print(f"[ERROR] Sample row: {rows[0] if rows else 'N/A'}", flush=True)
        print(f"[DEBUG] Columns: {list(rows[0].keys()) if rows else 'N/A'}", flush=True)
        import traceback
        traceback.print_exc()

def process_message(topic, value):
    try:
        event = json.loads(value)
        
        if event.get("after") is None:
            print(f"[INFO] Skipping delete operation for topic {topic}", flush=True)
            return []
            
        payload = event.get("after", {})

        if topic not in TOPIC_TABLE_MAP:
            print(f"[WARN] Unknown topic {topic}", flush=True)
            return []

        target = TOPIC_TABLE_MAP[topic]

        # Map per topic
        if topic == "cdc.public.primary_type":
            return [(target, map_primary_type(payload))]

        if topic == "cdc.public.crime":
            return [(target, map_crime(payload))]

        if topic == "cdc.public.location":
            return [(target, map_location(payload))]

        if topic == "cdc.public.patrol_unit":
            return [(target, map_patrol_unit(payload))]

        if topic == "cdc.public.case_report":
            mapped = map_case_report(payload)
            return [
                ("dim_date", mapped["dim_date"]),
                ("dim_time", mapped["dim_time"]),
                ("fact_case", mapped["fact"])
            ]

        return []

    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}", flush=True)
        print(f"[ERROR] Topic: {topic}", flush=True)
        print(f"[ERROR] Value preview: {value[:200]}...", flush=True)
        import traceback
        traceback.print_exc()
        return []

try:
    # ClickHouse client configuration
    clickhouseClient = clickhouse_connect.get_client(
        host='clickhouse',
        port=8123,
        username='default',
        password='clickhouse_pass',
        database='crime_analytics'
    )

    # Test connection
    result = clickhouseClient.command("SELECT 1")
    print(f"✓ ClickHouse connected: {result}", flush=True)
    
    # Show existing tables
    tables = clickhouseClient.command("SHOW TABLES")
    print(f"✓ Available tables: {tables}", flush=True)

    spark = SparkSession.builder \
        .appName("CDC_ETL") \
        .master("spark://spark-master:7077") \
        .config("spark.executor.memory", "4g") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.cores", "2") \
        .config("spark.cores.max", "8") \
        .config("spark.sql.shuffle.partitions", "16") \
        .config("spark.default.parallelism", "16") \
        .config("spark.streaming.kafka.maxRatePerPartition", "1000") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.memory.fraction", "0.8") \
        .config("spark.memory.storageFraction", "0.3") \
        .config("spark.executor.memoryOverhead", "1536m") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()

    print("✓ Spark session created", flush=True)

    topics = [
        "cdc.public.primary_type",
        "cdc.public.crime",
        "cdc.public.location",
        "cdc.public.patrol_unit",
        "cdc.public.case_report"
    ]

    print(f"✓ Subscribing to topics: {topics}", flush=True)

    kafka_stream_df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", ",".join(topics)) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .option("maxOffsetsPerTrigger", "100") \
        .load()
    
    kafka_stream_df = kafka_stream_df.selectExpr("CAST(topic AS STRING)", "CAST(value AS STRING)")

    print("✓ Kafka stream configured", flush=True)

    def for_each_batch_function(batch_df, batch_id):
        print(f"\n{'='*60}", flush=True)
        print(f"[BATCH {batch_id}] Started processing", flush=True)
        print(f"{'='*60}", flush=True)
        
        rows = batch_df.collect()
        print(f"[BATCH {batch_id}] Total messages: {len(rows)}", flush=True)

        if len(rows) == 0:
            print("[BATCH] Empty batch, skipping\n", flush=True)
            return

        grouped = {}
        for row in rows:
            try:
                topic = row["topic"]
                value = row["value"]
                
                print(f"[MSG] Processing topic: {topic}", flush=True)
                
                # Process the message
                results = process_message(topic, value)
                
                # Group by table
                for table, data in results:
                    if table not in grouped:
                        grouped[table] = []
                    grouped[table].append(data)
                    
            except Exception as e:
                print(f"[ERROR] Failed to process row: {e}", flush=True)
                import traceback
                traceback.print_exc()
                continue

        print(f"\n[BATCH {batch_id}] Summary:", flush=True)
        for table, data_rows in grouped.items():
            print(f"  - {table}: {len(data_rows)} rows", flush=True)
        
        # Write to ClickHouse
        for table, data_rows in grouped.items():
            write_data(table, data_rows, clickhouseClient)
        
        print(f"\n[BATCH {batch_id}] Completed", flush=True)
        print(f"{'='*60}\n", flush=True)
    
    query = kafka_stream_df.writeStream \
        .foreachBatch(for_each_batch_function) \
        .outputMode("append") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    print("✓ Streaming query started. Waiting for data...\n", flush=True)
    
    query.awaitTermination()

except KeyboardInterrupt:
    print("\nStopping ETL job...", flush=True)

except Exception as e:
    print(f"\n[FATAL ERROR] {e}", flush=True)
    import traceback
    traceback.print_exc()
    raise
finally:
    if 'spark' in locals():
        spark.stop()
        print("✓ Spark stopped", flush=True)