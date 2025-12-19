import sqlite3

conn = sqlite3.connect('swim_database_2.sqlite3')
cursor = conn.cursor()

# Get table info
cursor.execute('PRAGMA table_info(rudolph_scores)')
cols = [c[1] for c in cursor.fetchall()]
print('Columns:', cols)

# Get sample data
cursor.execute('SELECT * FROM rudolph_scores LIMIT 10')
rows = cursor.fetchall()
print('\nSample rows:')
for row in rows:
    print(f"  {row}")

# Get counts by gender
cursor.execute('SELECT Gender, COUNT(*) FROM rudolph_scores GROUP BY Gender')
print('\nGender distribution:')
for r in cursor.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Get counts by age
cursor.execute('SELECT Age, COUNT(*) FROM rudolph_scores GROUP BY Age ORDER BY Age')
print('\nAge distribution:')
for r in cursor.fetchall():
    print(f"  Age {r[0]}: {r[1]}")

# Get unique events
cursor.execute('SELECT DISTINCT Event FROM rudolph_scores ORDER BY Event')
print('\nEvents in table:')
for r in cursor.fetchall():
    print(f"  - {r[0]}")

conn.close()
