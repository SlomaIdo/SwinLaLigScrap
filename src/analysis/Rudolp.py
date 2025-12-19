import pdfplumber
import pandas as pd
import re
import os
import argparse
import sqlite3
from datetime import datetime

# CONFIGURATION
# ---------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PDF_PATH = os.path.join(script_dir, 'data', 'Rudolph_Punkttabelle_2025.pdf')
DEFAULT_OUTPUT_CSV = os.path.join(script_dir, 'data', 'Rudolph_2025_Database_Export.csv')
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'swim_database_2.sqlite3')

# Mappings for German to English Event Names
event_map = {
    'Freistil': 'Freestyle',
    'Brust': 'Breaststroke',
    'Rücken': 'Backstroke',
    'Schmetterling': 'Butterfly',
    'Lagen': 'Individual Medley',
    'F': 'Freestyle', 'B': 'Breaststroke', 'R': 'Backstroke', 'S': 'Butterfly', 'L': 'Individual Medley'
}

def clean_time(time_str):
    """Ensures time is in MM:SS.ss format."""
    if not time_str or time_str == '-':
        return None
    # Replace comma with dot for decimals
    time_str = time_str.replace(',', '.')
    return time_str

def parse_rudolph_pdf(pdf_path):
    all_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            # 1. Detect Gender and Age from Page Header
            # Looking for strings like "männlich, Altersklasse 8" or "weiblich, offene Klasse"
            gender = "Unknown"
            age = "Unknown"
            
            if "männlich" in text.lower():
                gender = "Male"
            elif "weiblich" in text.lower():
                gender = "Female"
                
            # Extract Age
            age_match = re.search(r'Altersklasse\s+(\d+|Offene)', text, re.IGNORECASE)
            if age_match:
                age = age_match.group(1)
                if age.lower() == 'offene':
                    age = 'Open'
                # Fix age mappings: 81 -> 8, 92 -> 9
                elif age == '81':
                    age = '8'
                elif age == '92':
                    age = '9'
                elif age == '83':
                    age = '8'
                elif age == '94':
                    age = '9'

            # 2. Extract Table Data
            # This logic assumes the standard grid layout of Rudolph tables
            # We extract the table using pdfplumber's table finder
            tables = page.extract_tables()
            
            for table in tables:
                # Identify headers (Events) usually in the first few rows
                # This part requires some heuristic adaption based on the exact visual layout
                # Assuming Row 0 or 1 contains distances (50m, 100m) and styles
                
                # Simplified Iteration: finding the 'Points' column (1-20)
                # and mapping other columns to events.
                
                # NOTE: You may need to adjust the column mapping indices below 
                # based on the exact column order of the 2025 PDF.
                # Common Order: Pts | 50F | 100F | 200F | 400F | ...
                
                # Let's flatten the table
                for row in table:
                    # Filter for rows that start with a point value (1-20)
                    try:
                        points = int(row[0]) # First column is usually points
                    except (ValueError, TypeError):
                        continue # Skip header rows
                    
                    if not (1 <= points <= 20):
                        continue

                    # Manual mapping based on 2025 standard layout (Example)
                    # You might need to tweak these indices after looking at the first CSV output
                    # Schema: Gender, Age, Event, Points, Time
                    
                    # Example mapping (Columns 1-N correspond to specific events)
                    # We create a list of (ColumnIndex, EventName)
                    # This is a generic placeholders mapping - check your PDF columns!
                    columns_mapping = [
                        (1, "50m Freestyle"), (2, "100m Freestyle"), (3, "200m Freestyle"),
                        (4, "400m Freestyle"), (5, "800m Freestyle"), (6, "1500m Freestyle"),
                        (7, "50m Breaststroke"), (8, "100m Breaststroke"), (9, "200m Breaststroke"),
                        (10, "50m Butterfly"), (11, "100m Butterfly"), (12, "200m Butterfly"),
                        (13, "50m Backstroke"), (14, "100m Backstroke"), (15, "200m Backstroke"),
                        (16, "200m Individual Medley"), (17, "400m Individual Medley")
                    ]

                    for col_idx, event_name in columns_mapping:
                        if col_idx < len(row):
                            time_val = clean_time(row[col_idx])
                            if time_val:
                                all_data.append([gender, age, event_name, points, time_val])

    # Create DataFrame
    df = pd.DataFrame(all_data, columns=['Gender', 'Age', 'Event', 'Points', 'Time'])
    return df

def ingest_to_database(df, db_path, table_name='rudolph_scores'):
    """
    Ingest the Rudolph scores DataFrame into the SQLite database.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing Rudolph scores
    db_path : str
        Path to the SQLite database
    table_name : str
        Name of the table to create/replace
    """
    print(f"\nIngesting data into database: {db_path}")
    print(f"Table name: {table_name}")
    
    conn = sqlite3.connect(db_path)
    try:
        # Add a timestamp column
        df['ingestion_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Ingest to database (replace if exists)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Verify ingestion
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print(f"✓ Successfully ingested {count} rows into table '{table_name}'")
        
        # Show table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\nTable structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        return True
    except Exception as e:
        print(f"✗ Error ingesting data: {e}")
        return False
    finally:
        conn.close()

# EXECUTION
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Parse Rudolph Punkttabelle PDF and ingest into database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (uses default paths)
  python Rudolp.py
  
  # Specify custom PDF path
  python Rudolp.py --pdf path/to/custom.pdf
  
  # Custom output CSV and database
  python Rudolp.py --csv output.csv --db custom_database.sqlite3
  
  # Skip database ingestion
  python Rudolp.py --no-ingest
  
  # Custom table name
  python Rudolp.py --table my_rudolph_scores
        """
    )
    
    parser.add_argument(
        '--pdf',
        default=DEFAULT_PDF_PATH,
        help=f'Path to Rudolph PDF file (default: {DEFAULT_PDF_PATH})'
    )
    
    parser.add_argument(
        '--csv',
        default=DEFAULT_OUTPUT_CSV,
        help=f'Output CSV file path (default: {DEFAULT_OUTPUT_CSV})'
    )
    
    parser.add_argument(
        '--db',
        default=DEFAULT_DB_PATH,
        help=f'SQLite database path (default: {DEFAULT_DB_PATH})'
    )
    
    parser.add_argument(
        '--table',
        default='rudolph_scores',
        help='Database table name (default: rudolph_scores)'
    )
    
    parser.add_argument(
        '--no-ingest',
        action='store_true',
        help='Skip database ingestion, only create CSV'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Rudolph Punkttabelle Parser")
    print("=" * 60)
    print(f"PDF Input:  {args.pdf}")
    print(f"CSV Output: {args.csv}")
    if not args.no_ingest:
        print(f"Database:   {args.db}")
        print(f"Table:      {args.table}")
    print("=" * 60)
    
    # Step 1: Parse PDF
    print("\n[1/2] Processing PDF...")
    try:
        df_rudolph = parse_rudolph_pdf(args.pdf)
        print(f"✓ Extracted {len(df_rudolph)} rows")
        print(f"\nData summary:")
        print(f"  Gender: {df_rudolph['Gender'].value_counts().to_dict()}")
        print(f"  Ages: {sorted([str(x) for x in df_rudolph['Age'].unique()])}")
        print(f"  Events: {df_rudolph['Event'].nunique()} unique")
        print(f"  Points range: {df_rudolph['Points'].min()}-{df_rudolph['Points'].max()}")
    except Exception as e:
        print(f"✗ Error processing PDF: {e}")
        return 1
    
    # Step 2: Save CSV
    print(f"\n[2/3] Saving CSV to {args.csv}...")
    try:
        df_rudolph.to_csv(args.csv, index=False)
        print(f"✓ CSV saved successfully")
        print(f"\nSample data:")
        print(df_rudolph.head(10))
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
        return 1
    
    # Step 3: Ingest to database (optional)
    if not args.no_ingest:
        print(f"\n[3/3] Ingesting to database...")
        success = ingest_to_database(df_rudolph, args.db, args.table)
        if not success:
            return 1
    else:
        print(f"\n[3/3] Skipping database ingestion (--no-ingest flag)")
    
    print("\n" + "=" * 60)
    print("✓ Process completed successfully!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    exit(main())