import sqlite3
import pandas as pd

conn = sqlite3.connect('swim_database_2.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1")
    cols = [description[0] for description in cursor.description]
    print(f"    Columns: {', '.join(cols)}")
    print()
