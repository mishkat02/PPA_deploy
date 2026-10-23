# Deploy: Placement Portal -> Neon (database) + Render (backend + frontend), all free

Why an external database: Render's free web service has an ephemeral disk, so SQLite data would be wiped on every restart/sleep.

## 0. One-time security fix
tasks.py used to contain a real Gmail app password. It is removed from this copy, but it is still in your git history.
Revoke it: Google Account -> Security -> 2-Step Verification -> App passwords -> delete it. Create a new one only if you want emails.

## 1. Push this folder to GitHub
    git add -A && git commit -m "Prepare for deployment" && git push

## 2. Database (Neon free Postgres)
Create a project at https://neon.tech and copy the connection string (postgresql://user:pass@host/db?sslmode=require).

## 3. Backend on Render (Web Service)
New + -> Web Service -> pick the repo.
- Root Directory : backend
- Runtime        : Python 3
- Build Command  : pip install -r requirements.txt
- Start Command  : gunicorn app:app
- Instance Type  : Free
- Environment variables:
    PYTHON_VERSION  = 3.12.8
    DATABASE_URL    = <Neon connection string>
    SECRET_KEY      = <random string>
    JWT_SECRET_KEY  = <another random string>
  (optional) GMAIL_SENDER, GMAIL_APP_PASSWORD   -> only if you want emails
  (optional) REDIS_URL = <Render Key Value URL>  -> otherwise an in-memory cache is used
Deploy, then copy the URL, e.g. https://placement-api.onrender.com
Tables and the admin user (admin@user.com / admin123) are created automatically on first start.

## 4. Frontend on Render (Static Site)
New + -> Static Site -> same repo.
- Root Directory     : frontend
- Build Command      : npm install && npm run build
- Publish Directory  : dist
- Environment variables:
    NODE_VERSION = 22
    VITE_API_URL = https://placement-api.onrender.com     (your backend URL, no trailing slash)
- Redirects/Rewrites tab -> add:  Source /*   Destination /index.html   Action Rewrite
  (needed so refreshing /admin, /student etc. doesn't 404)

## 5. Use it
Open the static-site URL. The first request after 15 min idle takes ~1 min while the backend wakes up.
Log in as admin@user.com / admin123 and change that password.

## Not available on the free tier
- Celery worker / beat (daily reminders, monthly report) - needs a paid background worker. CSV export still works (runs in a thread).
- Outgoing email is likely blocked on free Render, so emails may not send. The CSV file is still generated.
