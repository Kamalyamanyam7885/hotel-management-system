# database.py
# Run this file once to set up your entire database
# Command: python database.py

import mysql.connector
from werkzeug.security import generate_password_hash

# ─────────────────────────────────────────
#  DB CONFIG — change password to yours
# ─────────────────────────────────────────
config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",   # 👈 change this to your MySQL password
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ Connected to MySQL successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# ─────────────────────────────────────────
#  1. CREATE DATABASE
# ─────────────────────────────────────────
cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_management")
cursor.execute("USE hotel_management")
print("✅ Database ready.")

# ─────────────────────────────────────────
#  2. CREATE TABLES
# ─────────────────────────────────────────

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    email        VARCHAR(100)  NOT NULL UNIQUE,
    password     VARCHAR(255)  NOT NULL,
    phone        VARCHAR(15),
    address      TEXT,
    id_proof     VARCHAR(100),
    role         ENUM('guest') DEFAULT 'guest',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✅ users table ready.")

# ROOMS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    room_number   VARCHAR(10)   NOT NULL UNIQUE,
    type          ENUM('Single','Double','Deluxe','Suite') NOT NULL,
    floor         INT           NOT NULL DEFAULT 1,
    price         DECIMAL(10,2) NOT NULL,
    availability  ENUM('available','booked','maintenance') DEFAULT 'available',
    max_guests    INT           DEFAULT 1,
    amenities     TEXT,
    description   TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✅ rooms table ready.")

# BOOKINGS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    guest_id        INT           NOT NULL,
    room_id         INT           NOT NULL,
    check_in        DATE          NOT NULL,
    check_out       DATE          NOT NULL,
    num_guests      INT           DEFAULT 1,
    total_amount    DECIMAL(10,2),
    payment_status  ENUM('pending','paid','refunded') DEFAULT 'pending',
    payment_method  ENUM('cash','card','upi','online') DEFAULT 'cash',
    status          ENUM('pending_payment','confirmed','cancelled','completed') DEFAULT 'pending_payment',
    special_request TEXT,
    booked_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES users(id)  ON DELETE CASCADE,
    FOREIGN KEY (room_id)  REFERENCES rooms(id)  ON DELETE CASCADE
)
""")
print("✅ bookings table ready.")

# PAYMENTS TABLE
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
print("✅ payments table ready.")

# STAFF TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    email        VARCHAR(100)  NOT NULL UNIQUE,
    password     VARCHAR(255)  NOT NULL,
    phone        VARCHAR(15),
    role         ENUM('receptionist','housekeeping','manager','security') NOT NULL,
    department   VARCHAR(100),
    salary       DECIMAL(10,2),
    shift        ENUM('morning','afternoon','night') DEFAULT 'morning',
    joining_date DATE,
    status       ENUM('active','inactive') DEFAULT 'active',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✅ staff table ready.")

# ADMIN TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    email        VARCHAR(100)  NOT NULL UNIQUE,
    password     VARCHAR(255)  NOT NULL,
    phone        VARCHAR(15),
    super_admin  TINYINT(1)    DEFAULT 0,
    last_login   TIMESTAMP     NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✅ admin table ready.")

# ─────────────────────────────────────────
#  3. INSERT ADMIN
# ─────────────────────────────────────────
admin_pass = generate_password_hash("admin123")
cursor.execute("""
INSERT IGNORE INTO admin (name, email, password, phone, super_admin)
VALUES (%s, %s, %s, %s, %s)
""", ("Super Admin", "admin@hotel.com", admin_pass, "9999999999", 1))
print("✅ Admin inserted → admin@hotel.com / admin123")

# ─────────────────────────────────────────
#  4. INSERT SAMPLE ROOMS
# ─────────────────────────────────────────
sample_rooms = [
    ("101", "Single",  1, 1500.00, "available", 1, "AC, WiFi, TV",                  "Cozy single room with city view"),
    ("102", "Single",  1, 1500.00, "available", 1, "AC, WiFi, TV",                  "Quiet single room on lower floor"),
    ("201", "Double",  2, 2500.00, "available", 2, "AC, WiFi, TV, Minibar",          "Spacious double room with balcony"),
    ("202", "Double",  2, 2500.00, "available", 2, "AC, WiFi, TV, Minibar",          "Double room with garden view"),
    ("301", "Deluxe",  3, 4000.00, "available", 3, "AC, WiFi, TV, Minibar, Bathtub", "Deluxe room with premium amenities"),
    ("302", "Deluxe",  3, 4000.00, "available", 3, "AC, WiFi, TV, Minibar, Bathtub", "Deluxe corner room with two views"),
    ("401", "Suite",   4, 7500.00, "available", 4, "AC, WiFi, TV, Minibar, Jacuzzi", "Luxury suite with living area"),
    ("402", "Suite",   4, 7500.00, "available", 4, "AC, WiFi, TV, Minibar, Jacuzzi", "Presidential suite with jacuzzi"),
]
cursor.executemany("""
INSERT IGNORE INTO rooms
    (room_number, type, floor, price, availability, max_guests, amenities, description)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", sample_rooms)
print("✅ Sample rooms inserted.")

# ─────────────────────────────────────────
#  5. INSERT SAMPLE STAFF
# ─────────────────────────────────────────
staff_pass = generate_password_hash("staff123")
sample_staff = [
    ("Ravi Kumar",    "ravi@hotel.com",    staff_pass, "9876543210", "receptionist", "Front Desk",   25000.00, "morning",   "2023-01-15"),
    ("Meena Devi",    "meena@hotel.com",   staff_pass, "9876543211", "housekeeping", "Housekeeping", 18000.00, "morning",   "2023-03-10"),
    ("Suresh Babu",   "suresh@hotel.com",  staff_pass, "9876543212", "manager",      "Operations",   45000.00, "morning",   "2022-06-01"),
    ("Kavitha R",     "kavitha@hotel.com", staff_pass, "9876543213", "housekeeping", "Housekeeping", 18000.00, "afternoon", "2023-07-20"),
    ("Manoj Singh",   "manoj@hotel.com",   staff_pass, "9876543214", "security",     "Security",     20000.00, "night",     "2023-05-05"),
    ("Divya Lakshmi", "divya@hotel.com",   staff_pass, "9876543215", "receptionist", "Front Desk",   25000.00, "afternoon", "2024-01-10"),
]
cursor.executemany("""
INSERT IGNORE INTO staff
    (name, email, password, phone, role, department, salary, shift, joining_date)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""", sample_staff)
print("✅ Sample staff inserted → password: staff123")

# ─────────────────────────────────────────
#  6. INSERT SAMPLE GUESTS
# ─────────────────────────────────────────
guest_pass = generate_password_hash("guest123")
sample_users = [
    ("Arjun Kumar",  "arjun@gmail.com",   guest_pass, "9600000001", "Chennai, TN",    "Aadhar"),
    ("Priya Sharma", "priya@gmail.com",   guest_pass, "9600000002", "Bangalore, KA",  "Passport"),
    ("Rahul Verma",  "rahul@gmail.com",   guest_pass, "9600000003", "Mumbai, MH",     "Voter ID"),
    ("Sneha Nair",   "sneha@gmail.com",   guest_pass, "9600000004", "Kochi, KL",      "Aadhar"),
    ("Karthik R",    "karthik@gmail.com", guest_pass, "9600000005", "Coimbatore, TN", "Driving License"),
]
cursor.executemany("""
INSERT IGNORE INTO users
    (name, email, password, phone, address, id_proof, role)
VALUES (%s, %s, %s, %s, %s, %s, 'guest')
""", sample_users)
print("✅ Sample guests inserted → password: guest123")

# ─────────────────────────────────────────
#  7. INSERT SAMPLE BOOKINGS
# ─────────────────────────────────────────
cursor.execute("""
INSERT IGNORE INTO bookings
    (guest_id, room_id, check_in, check_out, num_guests,
     total_amount, payment_status, payment_method, status)
SELECT u.id, r.id,
    '2025-04-01', '2025-04-05', 1,
    6000.00, 'paid', 'card', 'confirmed'
FROM users u, rooms r
WHERE u.email = 'arjun@gmail.com' AND r.room_number = '101'
""")

cursor.execute("""
INSERT IGNORE INTO bookings
    (guest_id, room_id, check_in, check_out, num_guests,
     total_amount, payment_status, payment_method, status)
SELECT u.id, r.id,
    '2025-04-10', '2025-04-12', 2,
    5000.00, 'pending', 'cash', 'confirmed'
FROM users u, rooms r
WHERE u.email = 'priya@gmail.com' AND r.room_number = '201'
""")

cursor.execute("""
INSERT IGNORE INTO bookings
    (guest_id, room_id, check_in, check_out, num_guests,
     total_amount, payment_status, payment_method, status)
SELECT u.id, r.id,
    '2025-03-20', '2025-03-25', 3,
    37500.00, 'paid', 'upi', 'completed'
FROM users u, rooms r
WHERE u.email = 'rahul@gmail.com' AND r.room_number = '401'
""")
print("✅ Sample bookings inserted.")

# ─────────────────────────────────────────
#  COMMIT & CLOSE
# ─────────────────────────────────────────
conn.commit()
cursor.close()
conn.close()

print("\n🎉 Database setup complete!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  Database : hotel_management")
print("  Tables   : users, rooms, bookings, staff, admin")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  Admin  → admin@hotel.com  / admin123")
print("  Staff  → ravi@hotel.com   / staff123")
print("  Guest  → arjun@gmail.com  / guest123")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")