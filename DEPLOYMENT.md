# 🚀 Deployment Guide — Hotel Grand (FreshPlate)

Complete step-by-step guide to deploy the backend on **Railway** (with MySQL plugin) and frontend on **Vercel**.

---

## 📋 Prerequisites

- GitHub account with repository pushed
- [Railway](https://railway.app) account (linked to GitHub)
- [Vercel](https://vercel.com) account (linked to GitHub)

---

## Step 1: Push to GitHub

```bash
# Navigate to project root
cd hotel-management-system

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "feat: prepare for deployment — Railway + Vercel"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/Kamalyamanyam7885/hotel-management-system.git

# Push to main
git branch -M main
git push -u origin main
```

> If the remote already exists, just push:
> ```bash
> git add .
> git commit -m "feat: deployment config"
> git push origin main
> ```

---

## Step 2: Deploy Backend on Railway

### 2.1 — Create New Project
1. Go to [railway.app](https://railway.app) → **New Project**
2. Select **"Deploy from GitHub repo"**
3. Connect your GitHub account and select `hotel-management-system`

### 2.2 — Add MySQL Plugin
1. In your Railway project dashboard, click **"+ New"** → **"Database"** → **"MySQL"**
2. Railway will provision a MySQL instance automatically
3. Click on the MySQL service → **"Variables"** tab to see credentials:
   - `MYSQLHOST`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`
   - `MYSQLPORT`

### 2.3 — Configure Backend Service
1. Click on your **backend service** (the GitHub deployment)
2. Go to **Settings** tab:
   - **Root Directory**: Set to `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`

3. Go to **Variables** tab and add these environment variables:

| Variable | Value |
|----------|-------|
| `MYSQL_HOST` | _(copy from MySQL plugin → `MYSQLHOST`)_ |
| `MYSQL_USER` | _(copy from MySQL plugin → `MYSQLUSER`)_ |
| `MYSQL_PASSWORD` | _(copy from MySQL plugin → `MYSQLPASSWORD`)_ |
| `MYSQL_DB` | _(copy from MySQL plugin → `MYSQLDATABASE`)_ |
| `JWT_SECRET` | _(generate a strong random string, e.g. `openssl rand -hex 32`)_ |
| `PORT` | `5000` _(Railway auto-assigns, but set as fallback)_ |
| `FLASK_ENV` | `production` |
| `FRONTEND_URL` | `https://your-app.vercel.app` _(update after Vercel deploy)_ |

> **Tip**: You can reference Railway's MySQL variables directly using `${{MySQL.MYSQLHOST}}` syntax in the Variables tab.

### 2.4 — Generate Domain
1. Go to **Settings** → **Networking** → **Generate Domain**
2. Railway will give you a URL like: `https://hotel-management-system-production.up.railway.app`
3. **Save this URL** — you'll need it for the Vercel frontend config

### 2.5 — Initialize Database
After deployment, you need to run the database setup once:

```bash
# Option A: Use Railway CLI
npm install -g @railway/cli
railway login
railway link
railway run python database.py

# Option B: Connect to MySQL directly using Railway's provided credentials
# and run the SQL from database.py manually
```

---

## Step 3: Deploy Frontend on Vercel

### 3.1 — Import Project
1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import your `hotel-management-system` GitHub repository

### 3.2 — Configure Build Settings
| Setting | Value |
|---------|-------|
| **Framework Preset** | Other |
| **Root Directory** | `.` (root — since templates/static are at root level) |
| **Build Command** | _(leave empty — static files, no build needed)_ |
| **Output Directory** | `.` |

### 3.3 — Set Environment Variables
In Vercel project → **Settings** → **Environment Variables**:

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://your-railway-backend-url.up.railway.app` |

### 3.4 — Update config.js for Production
Before deploying, update `static/js/config.js`:

```javascript
const CONFIG = {
    BACKEND_URL: "https://your-railway-backend-url.up.railway.app"
};
```

Or use Vercel's build-time environment variable injection if you set up a build script.

### 3.5 — Deploy
Click **Deploy**. Vercel will deploy your static files and give you a URL like:
`https://hotel-management-system.vercel.app`

### 3.6 — Update Railway FRONTEND_URL
Go back to Railway → Backend service → Variables → Update:
```
FRONTEND_URL=https://hotel-management-system.vercel.app
```

---

## Step 4: Post-Deployment Checklist

- [ ] Visit `https://your-railway-url.up.railway.app/api/health` — should return `{"status": "ok"}`
- [ ] Visit your Vercel URL — landing page should load
- [ ] Test guest registration and login
- [ ] Test admin login (`admin@hotel.com` / `admin123`)
- [ ] Test room booking flow
- [ ] Update README.md live links with actual URLs

---

## 🔄 Updating After Deployment

Simply push to GitHub — both Railway and Vercel auto-deploy on push:

```bash
git add .
git commit -m "fix: your change description"
git push origin main
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` on Railway | Ensure **Root Directory** is set to `backend` in Railway settings |
| Database connection error | Verify MySQL env vars match Railway MySQL plugin credentials |
| CORS errors in browser | Update `FRONTEND_URL` env var on Railway to your Vercel URL |
| Static files not loading on Vercel | Ensure `vercel.json` rewrites are correct & output dir is `.` |
| `gunicorn` not found | Ensure `gunicorn` is in `requirements.txt` |

---

## 📝 Important Notes

1. **This is a server-rendered Flask app** — templates are rendered by Flask on the backend. The Vercel deployment serves the static landing page, but full functionality requires the Railway backend.

2. **For a fully working deployment**, consider deploying the entire app (Flask + templates + static) on Railway only, and using a custom domain. The Vercel deployment is primarily for static assets.

3. **Database migrations**: If you modify the schema, run `database.py` again or create migration scripts.
