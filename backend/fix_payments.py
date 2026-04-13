import mysql.connector
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG

def fix_payments():
    print("🚀 Fixing Payments Table...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if guest_id exists
        cursor.execute("DESCRIBE payments")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'guest_id' not in columns:
            print("📝 Adding missing 'guest_id' column to 'payments' table...")
            cursor.execute("ALTER TABLE payments ADD COLUMN guest_id INT NOT NULL AFTER booking_id")
            # Also add foreign key
            cursor.execute("ALTER TABLE payments ADD FOREIGN KEY (guest_id) REFERENCES users(id) ON DELETE CASCADE")
            print("✅ 'guest_id' column added.")
        else:
            print("✅ 'guest_id' column already exists.")
            
        conn.commit()
        print("\n🎉 Done!")
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    fix_payments()
