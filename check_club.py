import sqlite3
import pandas as pd

conn = sqlite3.connect('swim_database_2.sqlite3')

# Get sample data
query = "SELECT * FROM discipline_results_ingest LIMIT 5"
df = pd.read_sql_query(query, conn)

# Find the club column
club_col = [col for col in df.columns if 'Club' in col]
print("Club column name(s):")
for col in club_col:
    print(f"  Name: '{col}'")
    print(f"  Repr: {repr(col)}")
    print(f"  Sample values: {df[col].dropna().head().tolist()}")

conn.close()
