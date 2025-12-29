import sqlite3

def setup_database():
    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()

    # Create users table for RBAC
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT NOT NULL
        )
    ''')

    # Seed initial data
    users = [('admin', 'admin'), ('finance_user', 'finance'), ('intern_user', 'intern')]
    cursor.executemany('INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)', users)

    conn.commit()
    conn.close()
    print("✅ Database initialized with users!")

if __name__ == "__main__":
    setup_database()