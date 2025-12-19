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
        for page_num, page in enumerate(pdf.pages, 1):  # 1-indexed page numbers
            text = page.extract_text()
            if not text:
                continue
            
            # 1. Detect Gender and Age from Page Header
            # Hardcode specific pages where title appears on previous page
            if page_num == 3:
                gender = "Male"
                age = "10"
            elif page_num == 4:
                gender = "Male"
                age = "11"
            elif page_num == 5:
                gender = "Male"
                age = "12"
            else:
                # Looking for strings like "männlich, Altersklasse 8" or "weiblich, offene Klasse"
                gender = "Unknown"
                age = "Unknown"
                
                if "männlich" in text.lower():
                    gender = "Male"
                elif "weiblich" in text.lower():
                    gender = "Female"
                    
                # Extract Age
                # Note: Some pages have "A ltersklasse" (with space) due to PDF rendering
                age_match = re.search(r'A?\s*ltersklasse\s+(\d+|Offene)', text, re.IGNORECASE)
                if age_match:
                    age = age_match.group(1)
                    if age.lower() == 'offene':
                        age = 'Open'
                    # Fix age mappings with superscripts: 105 -> 10, 116 -> 11, 81 -> 8, 92 -> 9
                    elif age == '105':
                        age = '10'
                    elif age == '116':
                        age = '11'
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

                    # Correct column mapping based on 2025 PDF structure
                    # The PDF has empty columns between actual data columns
                    # Actual data appears at indices: 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50
                    columns_mapping = [
                        (2, "50m Freestyle"),
                        (5, "100m Freestyle"),
                        (8, "200m Freestyle"),
                        (11, "400m Freestyle"),
                        (14, "800m Freestyle"),
                        (17, "1500m Freestyle"),
                        (20, "50m Breaststroke"),
                        (23, "100m Breaststroke"),
                        (26, "200m Breaststroke"),
                        (29, "50m Butterfly"),
                        (32, "100m Butterfly"),
                        (35, "200m Butterfly"),
                        (38, "50m Backstroke"),
                        (41, "100m Backstroke"),
                        (44, "200m Backstroke"),
                        (47, "200m Individual Medley"),
                        (50, "400m Individual Medley")
                    ]

                    for col_idx, event_name in columns_mapping:
                        if col_idx < len(row):
                            time_val = clean_time(row[col_idx])
                            if time_val:
                                # Fix PDF bug: Male Age 11 100m Backstroke times are inflated by 1 minute
                                if gender == "Male" and age == "11" and event_name == "100m Backstroke":
                                    # Parse time and subtract 60 seconds
                                    try:
                                        parts = time_val.split(':')
                                        if len(parts) == 2:
                                            minutes = int(parts[0])
                                            seconds = float(parts[1])
                                            total_seconds = minutes * 60 + seconds - 60
                                            # Convert back to MM:SS.ss format
                                            new_minutes = int(total_seconds // 60)
                                            new_seconds = total_seconds % 60
                                            time_val = f"{new_minutes:02d}:{new_seconds:05.2f}"
                                    except:
                                        pass  # If parsing fails, use original value
                                
                                all_data.append([gender, age, event_name, points, time_val])

    # Create DataFrame
    df = pd.DataFrame(all_data, columns=['Gender', 'Age', 'Event', 'Points', 'Time'])
    return df

def get_rudolph_score(gender, age, event, time_seconds, df_rudolph=None):
    """
    Calculate the Rudolph score for a given swim time.
    
    Parameters
    ----------
    gender : str
        Gender of the swimmer ('Male' or 'Female')
    age : int or str
        Age of the swimmer (8-18 or 'Open' or 'Unknown')
    event : str
        Event name (e.g., '50m Freestyle', '100m Backstroke')
    time_seconds : float
        Swim time in seconds
    df_rudolph : pd.DataFrame, optional
        Rudolph scores DataFrame. If None, loads from database.
    
    Returns
    -------
    int or None
        Rudolph points (1-20), or None if no score found
        
    Examples
    --------
    >>> get_rudolph_score('Female', 10, '50m Freestyle', 30.4)
    11
    >>> get_rudolph_score('Male', 12, '100m Backstroke', 65.5)
    18
    """
    # Load data if not provided
    if df_rudolph is None:
        try:
            conn = sqlite3.connect(DEFAULT_DB_PATH)
            df_rudolph = pd.read_sql_query("SELECT * FROM rudolph_scores", conn)
            conn.close()
        except Exception as e:
            print(f"Error loading Rudolph scores: {e}")
            return None
    
    # Convert age to string for comparison
    age_str = str(age)
    
    # Filter for the specific gender, age, and event
    filtered = df_rudolph[
        (df_rudolph['Gender'] == gender) & 
        (df_rudolph['Age'] == age_str) & 
        (df_rudolph['Event'] == event)
    ].copy()
    
    if len(filtered) == 0:
        return None
    
    # Convert time strings to seconds for comparison
    from functions import parse_swim_time_to_seconds
    filtered['Time_Seconds'] = filtered['Time'].apply(parse_swim_time_to_seconds)
    
    # Sort by points descending (20 is best, 1 is lowest)
    filtered = filtered.sort_values('Points', ascending=False)
    
    # Find the highest points where time_seconds <= threshold
    for _, row in filtered.iterrows():
        if time_seconds <= row['Time_Seconds']:
            return int(row['Points'])
    
    # If time is slower than even 1 point, return None
    return None


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