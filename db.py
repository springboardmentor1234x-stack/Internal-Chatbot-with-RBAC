import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY,
    name TEXT,
    marks INTEGER
)
""")

# Insert data
cursor.execute("INSERT INTO student (name, marks) VALUES (?, ?)",
               ("Rahul", 90))

# Fetch data
cursor.execute("SELECT * FROM student")
print(cursor.fetchall())

# Save and close
conn.commit()
conn.close()
