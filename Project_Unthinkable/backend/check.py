import sqlite3

conn = sqlite3.connect("meetings.db")
cur = conn.cursor()

cur.execute("SELECT id, filename, summary FROM meetings;")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.close()
