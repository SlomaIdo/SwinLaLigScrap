import sqlite3
import pandas as pd

# Get events from database
conn = sqlite3.connect('swim_database_2.sqlite3')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables in database: {tables}\n")

# Get events from the appropriate table
table_name = tables[0] if tables else None
if table_name:
    cursor.execute(f"SELECT DISTINCT Event FROM {table_name} ORDER BY Event")
    db_events = sorted([row[0] for row in cursor.fetchall()])
    print(f"=== DATABASE EVENTS ({len(db_events)} unique) ===")
    for event in db_events:
        print(f"  {event}")
else:
    print("No tables found!")
    db_events = []

conn.close()

# Get events from Rudolph CSV
df = pd.read_csv('src/analysis/data/Rudolph_2025_Database_Export.csv')
rudolph_events = sorted(df['Event'].unique())

print(f"\n=== RUDOLPH TABLE EVENTS ({len(rudolph_events)} unique) ===")
for event in rudolph_events:
    print(f"  {event}")

# Compare
print("\n=== COMPARISON ===")
db_set = set(db_events)
rudolph_set = set(rudolph_events)

print(f"\nEvents in Rudolph but NOT in database ({len(rudolph_set - db_set)}):")
for event in sorted(rudolph_set - db_set):
    print(f"  - {event}")

print(f"\nEvents in database but NOT in Rudolph ({len(db_set - rudolph_set)}):")
for event in sorted(db_set - rudolph_set):
    print(f"  - {event}")

print(f"\nCommon events ({len(db_set & rudolph_set)}):")
for event in sorted(db_set & rudolph_set):
    print(f"  ✓ {event}")

# Check for similar events that might need mapping
print("\n=== POTENTIAL MATCHES (Similar names) ===")
for r_event in rudolph_set - db_set:
    for d_event in db_set:
        # Check if the distance and stroke type are similar
        if any(dist in r_event and dist in d_event for dist in ['50m', '100m', '200m', '400m', '800m', '1500m']):
            if any(stroke in r_event and stroke in d_event for stroke in ['Freestyle', 'Backstroke', 'Breaststroke', 'Butterfly', 'Medley']):
                print(f"  Rudolph: '{r_event}' <-> Database: '{d_event}'")
