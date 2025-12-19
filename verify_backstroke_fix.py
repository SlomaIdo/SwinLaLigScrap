import sqlite3

conn = sqlite3.connect('swim_database_2.sqlite3')
cursor = conn.cursor()

# Check Male Age 11 100m Backstroke times
cursor.execute("""
    SELECT Points, Time 
    FROM rudolph_scores 
    WHERE Gender='Male' AND Age='11' AND Event='100m Backstroke' 
    ORDER BY Points DESC
""")

results = cursor.fetchall()

print("Male Age 11 100m Backstroke - All times:")
print("=" * 50)
for points, time in results:
    print(f"  {points:2d} points: {time}")

conn.close()
