import sqlite3

db = sqlite3.connect("backend/resqflow.db")

cursor = db.execute(
    """
    UPDATE users
    SET full_name = ?
    WHERE username = ?
    """,
    ("Emergency Coordinator", "authority_admin")
)

db.commit()

print("Updated rows:", cursor.rowcount)

db.close()