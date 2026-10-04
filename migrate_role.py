import sqlite3

db = sqlite3.connect("backend/resqflow.db")

cursor = db.execute(
    "UPDATE users SET role = ? WHERE role = ?",
    ("EMERGENCY_COORDINATOR", "AUTHORITY")
)

db.commit()

print("Updated rows:", cursor.rowcount)

db.close()