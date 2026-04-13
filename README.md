# 🏨 Hotel Grand — Management System (FreshPlate)

A full-stack hotel management system built with Flask and MySQL. Features include guest registration, room booking with UPI payments, admin dashboard with staff/room/booking management, and receipt generation.

## 🌐 Live Links

| Service  | URL |
|----------|-----|
| **Frontend** | [https://your-app.vercel.app](https://your-app.vercel.app) |
| **Backend API** | [https://your-app.railway.app](https://your-app.railway.app) |
| **Health Check** | [https://your-app.railway.app/api/health](https://your-app.railway.app/api/health) |

> ⚠️ Replace the placeholder URLs above with your actual deployed URLs.

---

## ✨ Features

- **Guest Portal**: Registration, login, room browsing, booking, UPI payment, receipt generation
- **Admin Dashboard**: Room management, staff management, guest overview, booking status updates
- **Security**: Password hashing (Werkzeug), session-based auth, CORS protection
- **Database**: MySQL with relational schema (users, rooms, bookings, payments, staff, admin)
- **Deployment-Ready**: Gunicorn, environment variables, Railway + Vercel config

---

## 🛠️ Tech Stack

| Layer     | Technology |
|-----------|-----------|
| Backend   | Python, Flask, Gunicorn |
| Database  | MySQL (PyMySQL driver) |
| Frontend  | HTML5, CSS3, JavaScript (Jinja2 templates) |
| Hosting   | Railway (backend + MySQL) · Vercel (frontend static) |

---

## 📂 Project Structure

```
hotel-management-system/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # DB & JWT config (env vars)
│   ├── database.py         # DB schema setup script
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile             # Railway deployment
│   └── .env.example        # Required environment variables
├── templates/
│   ├── base.html           # Base layout (all pages extend this)
│   ├── index.html           # Landing page
│   ├── login.html / register.html
│   ├── admin/              # Admin dashboard templates
│   └── guest/              # Guest portal templates
├── static/
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js          # Frontend logic
│   │   ├── config.js        # Backend URL config
│   │   └── api.js           # API helper module
│   └── images/
├── config.js               # Root config (reference)
├── vercel.json             # Vercel deployment config
├── .gitignore
├── README.md
└── DEPLOYMENT.md
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.9+
- MySQL 8.0+
- pip

### 1. Clone the repo
```bash
git clone https://github.com/Kamalyamanyam7885/hotel-management-system.git
cd hotel-management-system
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials:
# MYSQL_HOST=localhost
# MYSQL_USER=root
# MYSQL_PASSWORD=yourpassword
# MYSQL_DB=hotel_management
# JWT_SECRET=your-secret-key
# PORT=5000
```

### 5. Setup database
```bash
python database.py
```

### 6. Run the server
```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

### Default Credentials
| Role   | Email              | Password  |
|--------|--------------------|-----------|
| Admin  | admin@hotel.com    | admin123  |
| Guest  | arjun@gmail.com    | guest123  |

---

## 📖 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full Railway + Vercel deployment instructions.

---

## 📄 License

This project is for educational purposes.