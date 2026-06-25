import sqlite3

conn = sqlite3.connect("students.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS roadmaps(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    branch TEXT,
    year TEXT,
    cgpa TEXT,
    interest TEXT,
    roadmap TEXT

)
""")

conn.commit()
conn.close()

print("Roadmaps Table Created")