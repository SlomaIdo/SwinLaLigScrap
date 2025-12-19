import sqlite3
import pandas as pd

conn = sqlite3.connect('swim_database_2.sqlite3')

# Get sample data
query = """
SELECT Gender, Age, Event, Points, Time 
FROM rudolph_scores 
WHERE Event='100m Backstroke' AND Gender='Female'
ORDER BY Age, Points
LIMIT 30
"""

df = pd.read_sql_query(query, conn)

print("Sample 100m Backstroke Female times:")
print("=" * 80)
print(df.to_string(index=False))

print("\n\nChecking time formats:")
print("=" * 80)
for idx, row in df.head(10).iterrows():
    print(f"Age {row['Age']}, Points {row['Points']}: Time = '{row['Time']}'")

# Check all unique time formats
print("\n\nAll unique times for 100m Backstroke Female Age 8:")
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT Time FROM rudolph_scores WHERE Event='100m Backstroke' AND Gender='Female' AND Age='8' ORDER BY Points")
times = [row[0] for row in cursor.fetchall()]
print(times)

conn.close()
