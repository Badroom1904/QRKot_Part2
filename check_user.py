import sqlite3

conn = sqlite3.connect('fastapi.db')
cursor = conn.cursor()
cursor.execute("SELECT id, email, is_superuser FROM user;")
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row[0]}, Email: {row[1]}, is_superuser: {row[2]}")

conn.close()