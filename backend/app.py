"""
HOTEL MANAGEMENT SYSTEM - COMPLETE IMPLEMENTATION
Single Flask app with NO blueprints, NO subfolders
Raw MySQL queries using mysql-connector-python
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG, SECRET_KEY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = SECRET_KEY

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"DB Error: {e}")
        return None

# ---------------- AUTH DECORATOR ----------------
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please login to access this page.", "error")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("Unauthorized access.", "error")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---------------- AUTH ROUTES ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('login.html', user_type='admin')

@app.route('/guest/login')
def guest_login():
    return render_template('login.html', user_type='guest')

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_type = request.form.get('user_type') or request.args.get('role')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        if not conn:
            flash("Database connection error.", "error")
            return render_template('login.html', user_type=user_type)
        
        try:
            cursor = conn.cursor(dictionary=True)

            if user_type == 'admin':
                cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
                admin = cursor.fetchone()
                if not admin:
                    flash("Admin user not found.", "error")
                    return render_template('login.html', user_type='admin')
                if admin.get('super_admin') != 1:
                    flash("Only the primary admin account can login.", "error")
                    return render_template('login.html', user_type='admin')
                admin_password_valid = False
                try:
                    admin_password_valid = check_password_hash(admin['password'], password)
                except ValueError:
                    # fallback for plain-text password in DB
                    admin_password_valid = (admin['password'] == password)

                if not admin_password_valid:
                    flash("Invalid admin password.", "error")
                    return render_template('login.html', user_type='admin')

                session['user_id'] = admin['id']
                session['user_name'] = admin['name']
                session['role'] = 'admin'
                flash(f"Welcome back, {admin['name']}!", "success")
                return redirect(url_for('admin_dashboard'))

            if user_type == 'guest':
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if not user or not check_password_hash(user['password'], password):
                    flash("Invalid guest credentials.", "error")
                    return render_template('login.html', user_type='guest')

                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['role'] = 'guest'
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('guest_dashboard'))

            # fallback for /login direct access
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            admin = cursor.fetchone()
            if admin and admin.get('super_admin') == 1:
                admin_password_valid = False
                try:
                    admin_password_valid = check_password_hash(admin['password'], password)
                except ValueError:
                    admin_password_valid = (admin['password'] == password)
                if admin_password_valid:
                    session['user_id'] = admin['id']
                    session['user_name'] = admin['name']
                    session['role'] = 'admin'
                    flash(f"Welcome back, {admin['name']}!", "success")
                    return redirect(url_for('admin_dashboard'))

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['role'] = 'guest'
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('guest_dashboard'))

            flash("Invalid email or password.", "error")
        except Error as e:
            flash(f"Login Error: {str(e)}", "error")
        finally:
            conn.close()
        
    return render_template('login.html', user_type=user_type)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        phone = request.form['phone']
        address = request.form['address']
        id_proof = request.form['id_proof']

        conn = get_db()
        if not conn:
            flash("Database connection error.", "error")
            return render_template('register.html')

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password, phone, address, id_proof, role) 
                VALUES (%s, %s, %s, %s, %s, %s, 'guest')
            """, (name, email, password, phone, address, id_proof))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except Error as e:
            flash(f"Error: {str(e)}", "error")
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

# ---------------- ADMIN ROUTES ----------------
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as count FROM rooms")
        total_rooms = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM rooms WHERE availability='available'")
        available_rooms = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='guest'")
        total_guests = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM staff")
        total_staff = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status='confirmed'")
        active_bookings = cursor.fetchone()['count']
        
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as revenue FROM bookings WHERE payment_status='paid'")
        total_revenue = cursor.fetchone()['revenue']
        
        cursor.execute("""
            SELECT b.*, u.name as guest_name, r.room_number 
            FROM bookings b
            JOIN users u ON b.guest_id = u.id
            JOIN rooms r ON b.room_id = r.id
            ORDER BY b.booked_at DESC LIMIT 5
        """)
        recent_bookings = cursor.fetchall()
        return render_template('admin/dashboard.html', 
                            stats={
                                'total_rooms': total_rooms,
                                'available_rooms': available_rooms,
                                'total_guests': total_guests,
                                'total_staff': total_staff,
                                'active_bookings': active_bookings,
                                'total_revenue': total_revenue
                            },
                            recent_bookings=recent_bookings)
    finally:
        conn.close()

@app.route('/admin/rooms', methods=['GET', 'POST'])
@login_required('admin')
def manage_rooms():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            room_number = request.form['room_number']
            room_type = request.form['type']
            floor = request.form['floor']
            price = request.form['price']
            max_guests = request.form['max_guests']
            amenities = request.form['amenities']
            description = request.form['description']
            
            try:
                cursor.execute("""
                    INSERT INTO rooms (room_number, type, floor, price, max_guests, amenities, description, availability)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'available')
                """, (room_number, room_type, floor, price, max_guests, amenities, description))
                conn.commit()
                flash("Room added successfully!", "success")
            except Error as e:
                flash(f"Error: {str(e)}", "error")
                
        cursor.execute("SELECT * FROM rooms ORDER BY room_number")
        rooms = cursor.fetchall()
        return render_template('admin/manage_rooms.html', rooms=rooms)
    finally:
        conn.close()

@app.route('/admin/rooms/edit/<int:id>', methods=['POST'])
@login_required('admin')
def edit_room(id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rooms SET room_number=%s, type=%s, floor=%s, price=%s, 
            max_guests=%s, amenities=%s, description=%s, availability=%s 
            WHERE id=%s
        """, (request.form['room_number'], request.form['type'], request.form['floor'], 
              request.form['price'], request.form['max_guests'], request.form['amenities'], 
              request.form['description'], request.form['availability'], id))
        conn.commit()
        flash("Room updated successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_rooms'))

@app.route('/admin/rooms/delete/<int:id>', methods=['POST'])
@login_required('admin')
def delete_room(id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rooms WHERE id=%s", (id,))
        conn.commit()
        flash("Room deleted successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_rooms'))

@app.route('/admin/staff', methods=['GET', 'POST'])
@login_required('admin')
def manage_staff():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            try:
                cursor.execute("""
                    INSERT INTO staff (name, email, password, phone, role, department, salary, shift, joining_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
                """, (request.form['name'], request.form['email'], 
                      generate_password_hash(request.form['password']), 
                      request.form['phone'], request.form['role'], 
                      request.form['department'], request.form['salary'], 
                      request.form['shift'], request.form['joining_date']))
                conn.commit()
                flash("Staff added successfully!", "success")
            except Error as e:
                flash(f"Error: {str(e)}", "error")
                
        cursor.execute("SELECT * FROM staff")
        staff_members = cursor.fetchall()
        return render_template('admin/manage_staff.html', staff=staff_members)
    finally:
        conn.close()

@app.route('/admin/staff/edit/<int:id>', methods=['POST'])
@login_required('admin')
def edit_staff(id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE staff SET name=%s, email=%s, phone=%s, role=%s, 
            department=%s, salary=%s, shift=%s, status=%s 
            WHERE id=%s
        """, (request.form['name'], request.form['email'], request.form['phone'], 
              request.form['role'], request.form['department'], request.form['salary'], 
              request.form['shift'], request.form['status'], id))
        conn.commit()
        flash("Staff updated successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_staff'))

@app.route('/admin/staff/delete/<int:id>', methods=['POST'])
@login_required('admin')
def delete_staff(id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM staff WHERE id=%s", (id,))
        conn.commit()
        flash("Staff deleted successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_staff'))

@app.route('/admin/guests')
@login_required('admin')
def view_guests():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role='guest' ORDER BY created_at DESC")
        guests = cursor.fetchall()
        return render_template('admin/view_guests.html', guests=guests)
    finally:
        conn.close()

@app.route('/admin/bookings')
@login_required('admin')
def view_bookings():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, u.name as guest_name, r.room_number, r.type as room_type
            FROM bookings b
            JOIN users u ON b.guest_id = u.id
            JOIN rooms r ON b.room_id = r.id
            ORDER BY b.booked_at DESC
        """)
        bookings = cursor.fetchall()
        return render_template('admin/view_bookings.html', bookings=bookings)
    finally:
        conn.close()

@app.route('/admin/bookings/update/<int:id>', methods=['POST'])
@login_required('admin')
def update_booking(id):
    status = request.form.get('status')
    if status not in ['pending_payment', 'confirmed', 'cancelled', 'completed']:
        flash('Invalid status selected.', 'error')
        return redirect(url_for('view_bookings'))

    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT room_id, status FROM bookings WHERE id = %s", (id,))
        booking = cursor.fetchone()
        if not booking:
            flash('Booking not found.', 'error')
            return redirect(url_for('view_bookings'))

        if booking['status'] == 'cancelled' and status != 'cancelled':
            # do not re-open cancelled bookings automatically; admin may handle manually
            pass

        cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (status, id))

        # sync room availability on confirmed/cancelled transitions
        if status == 'cancelled':
            cursor.execute("UPDATE rooms SET availability = 'available' WHERE id = %s", (booking['room_id'],))
        elif status == 'confirmed':
            cursor.execute("UPDATE rooms SET availability = 'booked' WHERE id = %s", (booking['room_id'],))

        conn.commit()
        flash('Booking status updated successfully.', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error updating booking: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('view_bookings'))

# ---------------- GUEST ROUTES ----------------
@app.route('/guest/dashboard')
@login_required('guest')
def guest_dashboard():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE guest_id = %s", (session['user_id'],))
        total_bookings = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE guest_id = %s AND status='confirmed'", (session['user_id'],))
        active_bookings = cursor.fetchone()['count']
        return render_template('guest/dashboard.html', total_bookings=total_bookings, active_bookings=active_bookings)
    finally:
        conn.close()

@app.route('/guest/rooms')
@login_required('guest')
def guest_rooms():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms WHERE availability='available'")
        rooms = cursor.fetchall()
        return render_template('guest/available_rooms.html', rooms=rooms)
    finally:
        conn.close()

@app.route('/guest/book/<int:room_id>', methods=['GET', 'POST'])
@login_required('guest')
def book_room(room_id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            check_in = request.form['check_in']
            check_out = request.form['check_out']
            d1 = datetime.strptime(check_in, '%Y-%m-%d')
            d2 = datetime.strptime(check_out, '%Y-%m-%d')
            nights = (d2 - d1).days
            if nights <= 0:
                flash("Check-out must be after Check-in.", "error")
                return redirect(url_for('book_room', room_id=room_id))
            cursor.execute("""
                SELECT * FROM bookings WHERE room_id = %s AND status = 'confirmed'
                AND NOT (check_out <= %s OR check_in >= %s)
            """, (room_id, check_in, check_out))
            if cursor.fetchone():
                flash("This room is already booked for the selected dates.", "error")
                return redirect(url_for('book_room', room_id=room_id))
            cursor.execute("SELECT price FROM rooms WHERE id = %s", (room_id,))
            room = cursor.fetchone()
            cursor.execute("""
                INSERT INTO bookings (guest_id, room_id, check_in, check_out, num_guests, total_amount, 
                                     payment_status, payment_method, status, special_request)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, 'pending_payment', %s)
            """, (session['user_id'], room_id, check_in, check_out, request.form['num_guests'], 
                  nights * room['price'], request.form['payment_method'], request.form['special_request']))
            booking_id = cursor.lastrowid
            cursor.execute("UPDATE rooms SET availability='booked' WHERE id = %s", (room_id,))
            conn.commit()
            flash("Room booking initiated! Please complete the payment.", "info")
            return redirect(url_for('guest_payment', booking_id=booking_id))
        cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
        room = cursor.fetchone()
        return render_template('guest/book_room.html', room=room)
    finally:
        conn.close()

@app.route('/guest/payment/<int:booking_id>')
@login_required('guest')
def guest_payment(booking_id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return redirect(url_for('my_bookings'))
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, r.room_number, r.type as room_type 
            FROM bookings b 
            JOIN rooms r ON b.room_id = r.id 
            WHERE b.id = %s AND b.guest_id = %s
        """, (booking_id, session['user_id']))
        booking = cursor.fetchone()
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for('my_bookings'))
        return render_template('guest/payment.html', booking=booking)
    finally:
        conn.close()

@app.route('/guest/confirm_payment/<int:booking_id>', methods=['POST'])
@login_required('guest')
def confirm_payment(booking_id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return redirect(url_for('my_bookings'))
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if booking exists and belongs to guest
        cursor.execute("SELECT total_amount FROM bookings WHERE id = %s AND guest_id = %s", (booking_id, session['user_id']))
        booking = cursor.fetchone()
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for('my_bookings'))

        # Record payment
        transaction_id = request.form.get('transaction_id', 'TXN' + datetime.now().strftime('%Y%m%d%H%M%S'))
        cursor.execute("""
            INSERT INTO payments (booking_id, guest_id, amount, payment_method, transaction_id, status)
            VALUES (%s, %s, %s, %s, %s, 'completed')
        """, (booking_id, session['user_id'], booking['total_amount'], 'UPI QR', transaction_id))
        
        # Update booking status
        cursor.execute("""
            UPDATE bookings SET status='confirmed', payment_status='paid' 
            WHERE id = %s
        """, (booking_id,))
        
        conn.commit()
        flash("Booking confirmed!", "success")
        return redirect(url_for('booking_receipt', booking_id=booking_id))
    except Exception as e:
        conn.rollback()
        flash(f"Error confirming payment: {str(e)}", "error")
        return redirect(url_for('guest_payment', booking_id=booking_id))
    finally:
        conn.close()

@app.route('/guest/receipt/<int:booking_id>')
@login_required('guest')
def booking_receipt(booking_id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return redirect(url_for('my_bookings'))
    try:
        cursor = conn.cursor(dictionary=True)
        # Fetch booking with room details
        cursor.execute("""
            SELECT b.*, r.room_number, r.type as room_type, r.floor, r.amenities, r.description as room_description
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.id = %s AND b.guest_id = %s
        """, (booking_id, session['user_id']))
        booking = cursor.fetchone()
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for('my_bookings'))

        # Fetch guest details
        cursor.execute("SELECT name, email, phone FROM users WHERE id = %s", (session['user_id'],))
        guest = cursor.fetchone()

        # Fetch payment details
        cursor.execute("""
            SELECT * FROM payments WHERE booking_id = %s ORDER BY created_at DESC LIMIT 1
        """, (booking_id,))
        payment = cursor.fetchone()

        # Calculate nights
        if booking['check_in'] and booking['check_out']:
            d1 = booking['check_in']
            d2 = booking['check_out']
            if isinstance(d1, str):
                d1 = datetime.strptime(d1, '%Y-%m-%d').date()
            if isinstance(d2, str):
                d2 = datetime.strptime(d2, '%Y-%m-%d').date()
            nights = (d2 - d1).days
        else:
            nights = 0
        price_per_night = booking['total_amount'] / nights if nights > 0 else booking['total_amount']

        return render_template('guest/receipt.html', 
                             booking=booking, guest=guest, payment=payment,
                             nights=nights, price_per_night=price_per_night)
    finally:
        conn.close()

@app.route('/guest/mybookings')
@login_required('guest')
def my_bookings():
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, r.room_number, r.type as room_type
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.guest_id = %s
            ORDER BY b.booked_at DESC
        """, (session['user_id'],))
        bookings = cursor.fetchall()
        return render_template('guest/my_bookings.html', bookings=bookings)
    finally:
        conn.close()

@app.route('/guest/cancel/<int:id>', methods=['POST'])
@login_required('guest')
def cancel_booking(id):
    conn = get_db()
    if conn is None:
        flash('Database connection error.', 'error')
        return render_template('login.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT room_id FROM bookings WHERE id = %s AND guest_id = %s", (id, session['user_id']))
        booking = cursor.fetchone()
        if booking:
            cursor.execute("UPDATE bookings SET status='cancelled' WHERE id = %s", (id,))
            cursor.execute("UPDATE rooms SET availability='available' WHERE id = %s", (booking['room_id'],))
            conn.commit()
            flash("Booking cancelled.", "success")
        else:
            flash("Booking not found.", "error")
    finally:
        conn.close()
    return redirect(url_for('my_bookings'))

if __name__ == '__main__':
    app.run(debug=True)
