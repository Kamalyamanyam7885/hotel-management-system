import mysql.connector
import sys
import os

# Add the current directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG

def migrate():
    print("🚀 Starting Database Migration...")
    try:
        # Connect to MySQL (without database initially to be safe, but we know it exists)
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # 1. Update bookings table status enum
        print("📝 Updating 'bookings' table status ENUM to include 'pending_payment'...")
        try:
            cursor.execute("""
                ALTER TABLE bookings 
                MODIFY COLUMN status ENUM('pending_payment','confirmed','cancelled','completed') 
                DEFAULT 'pending_payment'
            """)
            print("✅ 'bookings' table updated.")
        except mysql.connector.Error as err:
            print(f"⚠️ Error updating bookings: {err}")
        
        # 2. Add 'payments' table if it doesn't exist
        print("📝 Ensuring 'payments' table exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            booking_id      INT           NOT NULL,
            guest_id        INT           NOT NULL,
            amount          DECIMAL(10,2) NOT NULL,
            payment_method  VARCHAR(50)   DEFAULT 'UPI QR',
            transaction_id  VARCHAR(100),
            status          ENUM('pending','completed','failed') DEFAULT 'pending',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
            FOREIGN KEY (guest_id)   REFERENCES users(id)    ON DELETE CASCADE
        )
        """)
        print("✅ 'payments' table ready.")
        
        conn.commit()
        print("\n🎉 Migration completed successfully!")
    except mysql.connector.Error as err:
        print(f"❌ Error during migration: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    migrate()
