import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

# Load environment variables
DB_CONFIG = {
    "host": "localhost",  
    "port": "5432",
    "database": "crime_data",
    "user": "postgres",
    "password": "hoaihai161104"
}

try:
    # Find CSV file
    print("\n[1/5] Locating CSV file...")
    
    project_root = Path(__file__).parent.parent.parent.parent
    data_path = project_root / "data" / "raw" / "stream_data.csv"
    
    if not data_path.exists():
        data_path = project_root / "raw" / "stream_data.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(f"CSV file not found at: {data_path}")
    
    # Connect to PostgreSQL
    print("\n[2/5] Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("    ✓ Connected")

    # Read CSV with pandas (limit rows for testing)
    print("\n[3/5] Reading CSV file...")
    df = pd.read_csv(data_path)  # Limit to 100k rows
    # Sample for testing to 1%
    df = df.sample(frac=0.01, random_state=42)
    print(f"    ✓ Loaded {len(df):,} rows")

    # Data cleaning
    print("\n[4/5] Cleaning data...")
    
    # Parse datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df = df.dropna(subset=['Date'])
    
    df['date'] = df['Date'].dt.date
    df['time'] = df['Date'].dt.time
    
    # Convert boolean columns
    df['arrest'] = df['Arrest'].astype(str).str.lower().map({'true': 1, 'false': 0}).fillna(0).astype(int)
    df['domestic'] = df['Domestic'].astype(str).str.lower().map({'true': 1, 'false': 0}).fillna(0).astype(int)
    
    # Fill nulls
    df['Location Description'] = df['Location Description'].fillna('Unknown')
    df['Location'] = df['Location'].fillna('(0.0, 0.0)')
    df['Block'] = df['Block'].fillna('Unknown')
    df['IUCR'] = df['IUCR'].fillna('0000')
    df['Primary Type'] = df['Primary Type'].fillna('Unknown')
    df['Description'] = df['Description'].fillna('Unknown')
    df['FBI Code'] = df['FBI Code'].fillna('00')
    
    # Convert numeric columns - use Python int() to avoid numpy types
    for col in ['Beat', 'District', 'Ward', 'Community Area']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(-1).astype(int)
    
    # Ensure ID and Case Number are valid
    df = df.dropna(subset=['ID', 'Case Number'])
    df['ID'] = df['ID'].astype(int)
    
    print(f"    ✓ Cleaned to {len(df):,} valid rows")

    # Clear existing data
    print("\n[5/5] Inserting data into PostgreSQL...")
    print("  - Clearing existing tables...")
    
    cursor.execute("TRUNCATE TABLE case_report, location, patrol_unit, crime, primary_type RESTART IDENTITY CASCADE;")
    conn.commit()
    print("    ✓ Tables cleared")

    # 1. Primary Type
    print("  - Inserting primary_type...")
    primary_types = df[['Primary Type']].drop_duplicates().reset_index(drop=True)
    primary_types['id'] = range(1, len(primary_types) + 1)
    
    execute_values(cursor, """
        INSERT INTO primary_type (id, name) VALUES %s
    """, [(int(row['id']), row['Primary Type']) for _, row in primary_types.iterrows()])
    
    primary_type_map = dict(zip(primary_types['Primary Type'], primary_types['id']))
    print(f"    ✓ Inserted {len(primary_types)} primary types")
    
    # 2. Crime
    print("  - Inserting crime...")
    crimes = df[['IUCR', 'Primary Type', 'Description', 'FBI Code']].drop_duplicates().reset_index(drop=True)
    crimes['id'] = range(1, len(crimes) + 1)
    crimes['primary_type_id'] = crimes['Primary Type'].map(primary_type_map)
    
    execute_values(cursor, """
        INSERT INTO crime (id, iucr, primary_type, description, fbi_code) VALUES %s
    """, [(int(row['id']), row['IUCR'], int(row['primary_type_id']), row['Description'], row['FBI Code']) 
          for _, row in crimes.iterrows()])
    
    crime_map = {(row['IUCR'], row['Description']): row['id'] for _, row in crimes.iterrows()}
    print(f"    ✓ Inserted {len(crimes)} crimes")
    
    # 3. Location
    print("  - Inserting location...")
    locations = df[['Location Description', 'Block', 'Location']].drop_duplicates().reset_index(drop=True)
    locations['id'] = range(1, len(locations) + 1)
    
    execute_values(cursor, """
        INSERT INTO location (id, location_description, block, location) VALUES %s
    """, [(int(row['id']), row['Location Description'], row['Block'], row['Location']) 
          for _, row in locations.iterrows()])
    
    location_map = {(row['Location Description'], row['Block']): row['id'] for _, row in locations.iterrows()}
    print(f"    ✓ Inserted {len(locations)} locations")
    
    # 4. Patrol Unit - CONVERT NUMPY INT64 TO PYTHON INT
    print("  - Inserting patrol_unit...")
    patrol = df[['Beat', 'District', 'Ward', 'Community Area']].drop_duplicates().reset_index(drop=True)
    patrol['id'] = range(1, len(patrol) + 1)
    
    execute_values(cursor, """
        INSERT INTO patrol_unit (id, beat, district, ward, community_area) VALUES %s
    """, [(int(row['id']), int(row['Beat']), int(row['District']), int(row['Ward']), int(row['Community Area'])) 
          for _, row in patrol.iterrows()])
    
    patrol_map = {(row['District'], row['Beat']): row['id'] for _, row in patrol.iterrows()}
    print(f"    ✓ Inserted {len(patrol)} patrol units")
    
    # 5. Case Report
    print("  - Inserting case_report...")
    
    # Map foreign keys
    df['crime_id'] = df.apply(lambda x: crime_map.get((x['IUCR'], x['Description'])), axis=1)
    df['location_id'] = df.apply(lambda x: location_map.get((x['Location Description'], x['Block'])), axis=1)
    df['patrol_unit_id'] = df.apply(lambda x: patrol_map.get((x['District'], x['Beat'])), axis=1)
    
    # Filter and prepare case data
    case_data = df[['ID', 'Case Number', 'crime_id', 'location_id', 'patrol_unit_id', 
                    'date', 'time', 'arrest', 'domestic']].copy()
    case_data = case_data.dropna(subset=['crime_id', 'location_id', 'patrol_unit_id'])
    
    case_data['crime_id'] = case_data['crime_id'].astype(int)
    case_data['location_id'] = case_data['location_id'].astype(int)
    case_data['patrol_unit_id'] = case_data['patrol_unit_id'].astype(int)
    
    # Insert in batches
    batch_size = 5000
    total_inserted = 0
    
    for i in range(0, len(case_data), batch_size):
        batch = case_data.iloc[i:i+batch_size]
        
        execute_values(cursor, """
            INSERT INTO case_report (id, case_number, crime_id, location_id, patrol_unit_id, date, time, arrest, domestic) 
            VALUES %s
        """, [(int(row['ID']), row['Case Number'], int(row['crime_id']), int(row['location_id']), 
               int(row['patrol_unit_id']), row['date'], row['time'], int(row['arrest']), int(row['domestic'])) 
              for _, row in batch.iterrows()])
        
        total_inserted += len(batch)
        print(f"    - Inserted {total_inserted:,} / {len(case_data):,} case reports...")
    
    print(f"    ✓ Inserted {total_inserted:,} case reports")
    
    conn.commit()
    
    print("\n" + "="*50)
    print("✓ Preprocessing completed successfully!")
    print(f"  - Primary types: {len(primary_types):,}")
    print(f"  - Crimes: {len(crimes):,}")
    print(f"  - Locations: {len(locations):,}")
    print(f"  - Patrol units: {len(patrol):,}")
    print(f"  - Case reports: {total_inserted:,}")
    print("="*50)

except FileNotFoundError as e:
    print(f"\n✗ File error: {e}")
    print("\nPlease ensure the CSV file exists at:")
    print(f"  {Path(__file__).parent.parent.parent / 'data' / 'raw' / 'stream_data.csv'}")
    
except psycopg2.Error as e:
    print(f"\n✗ Database error: {e}")
    print("\nPlease ensure PostgreSQL is running and credentials are correct")
    if 'conn' in locals():
        conn.rollback()
    
except Exception as e:
    print(f"\n✗ Error occurred: {e}")
    import traceback
    traceback.print_exc()
    
    if 'conn' in locals():
        conn.rollback()

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("\n✓ Database connection closed")