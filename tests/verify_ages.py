import sqlite3

conn = sqlite3.connect('swim_database_2.sqlite3')
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT Gender, Age FROM rudolph_scores WHERE Gender IN ('Male', 'Female') ORDER BY Gender, Age")
results = cursor.fetchall()

print("Gender/Age combinations:")
for gender, age in results:
    print(f"{gender} Age {age}")

# Check specifically for Female 10 and Male 11
cursor.execute("SELECT COUNT(*) FROM rudolph_scores WHERE Gender='Female' AND Age='10'")
female_10_count = cursor.fetchone()[0]
print(f"\nFemale Age 10 records: {female_10_count}")

cursor.execute("SELECT COUNT(*) FROM rudolph_scores WHERE Gender='Male' AND Age='11'")
male_11_count = cursor.fetchone()[0]
print(f"Male Age 11 records: {male_11_count}")

conn.close()
