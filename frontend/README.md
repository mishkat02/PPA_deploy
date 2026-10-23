## Run Application

Follow these steps to run all components of the application across separate terminal windows.

### Prerequisites
Make sure **Redis** is installed and running on your local machine:
```bash
redis-server

Terminal 1: Start Backend (Flask API)
source .env/bin/activate
cd backend
python3 app.py

Terminal 2: Start Celery Worker
source .env/bin/activate
cd backend
python3 -m celery -A tasks.celery worker -l info -P solo

Another terminal 
source .env/bin/activate
cd backend
python3 -m celery -A tasks.celery beat --loglevel=info

Terminal 4: Start Frontend (Vue.js)
cd frontend
npm install
npm run dev


Terminal 5: Trigger Scheduled Tasks Manually (For Demo/Testing)
source .env/bin/activate
cd backend
python3 -m celery -A tasks.celery call tasks.send_daily_reminders
python3 -m celery -A tasks.celery call tasks.send_monthly_report
