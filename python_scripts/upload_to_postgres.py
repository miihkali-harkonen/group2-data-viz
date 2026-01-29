import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from pathlib import Path

load_dotenv('.env')

# Get PostgreSQL connection details from environment
PG_HOST = os.getenv('PGHOST')
PG_PORT = os.getenv('PGPORT', '5432')
PG_DATABASE = os.getenv('PGDATABASE')
PG_USER = os.getenv('PGUSER')
PG_PASSWORD = os.getenv('PGPASSWORD')

def clean_table_name(filename):
    """Convert filename to valid PostgreSQL table name"""
    return filename.replace('.csv', '').replace('-', '_').replace(' ', '_').lower()

def upload_csv_to_postgres(csv_path, table_name, conn):
    """Upload a single CSV file to PostgreSQL"""
    print(f"Processing {csv_path}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Create cursor
    cur = conn.cursor()
    
    # Drop table if exists and create new
    cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name)))
    
    # Infer column types and create table
    create_cols = []
    for col in df.columns:
        col_clean = col.replace(' ', '_').replace('-', '_').lower()
        dtype = df[col].dtype
        
        if dtype == 'object':
            pg_type = 'TEXT'
        elif dtype == 'int64':
            pg_type = 'BIGINT'
        elif dtype == 'float64':
            pg_type = 'DOUBLE PRECISION'
        elif dtype == 'bool':
            pg_type = 'BOOLEAN'
        else:
            pg_type = 'TEXT'
        
        create_cols.append(f'"{col_clean}" {pg_type}')
    
    create_table_sql = f"CREATE TABLE {table_name} ({', '.join(create_cols)})"
    cur.execute(create_table_sql)
    
    # Insert data
    df.columns = [col.replace(' ', '_').replace('-', '_').lower() for col in df.columns]
    
    for _, row in df.iterrows():
        placeholders = ', '.join(['%s'] * len(row))
        columns = ', '.join([f'"{col}"' for col in df.columns])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cur.execute(insert_sql, tuple(row))
    
    conn.commit()
    cur.close()
    print(f"✓ Uploaded {len(df)} rows to table '{table_name}'")

def main():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )
    
    print(f"Connected to PostgreSQL database: {PG_DATABASE}")
    
    # Find all CSV files
    base_path = Path(__file__).parent.parent
    csv_paths = []
    
    # Add files from data/
    data_dir = Path('../data')
    if data_dir.exists():
        csv_paths.extend(data_dir.glob('*.csv'))
    
    # Add files from data/extra/
    extra_dir = Path('../data/extra')
    if Path(extra_dir).exists():
        csv_paths.extend(Path(extra_dir).glob('*.csv'))
    
    if not csv_paths:
        print("No CSV files found in data/ or data/extra/")
        return
    
    print(f"\nFound {len(csv_paths)} CSV file(s)")
    
    # Upload each CSV
    for csv_path in csv_paths:
        if "cleaned_fingrid_data" in csv_path.name:
            print(f"Skipping {csv_path.name} as it is handled separately.")
            continue  # Skip this file
        table_name = clean_table_name(csv_path.name)
        try:
            upload_csv_to_postgres(csv_path, table_name, conn)
        except Exception as e:
            print(f"✗ Error uploading {csv_path.name}: {e}")
    
    conn.close()
    print("\n✓ All done!")

if __name__ == "__main__":
    main()
