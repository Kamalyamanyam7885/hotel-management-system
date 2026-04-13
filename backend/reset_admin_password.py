import mysql.connector
from werkzeug.security import generate_password_hash

# DB CONFIG — same as in database.py
config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",   # Change this to your MySQL password if different
    "database": "hotel_management"
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ Connected to MySQL successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# New password
new_password = "Kamal@2006"
hashed_password = generate_password_hash(new_password)

# Update the super admin password
cursor.execute("""
UPDATE admin
SET password = %s
WHERE super_admin = 1
""", (hashed_password,))

conn.commit()
print(f"✅ Admin password updated successfully! New password: {new_password}")
print("You can now login with email: admin@hotel.com and password: " + new_password)

cursor.close()
conn.close()