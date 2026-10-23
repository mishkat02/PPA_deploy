import os
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

from app import app
from models import User, Student, PlacementDrive, Application

BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery = Celery('tasks', broker=BROKER_URL, backend=BROKER_URL)

celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(minute='*/1'),
    },
    'monthly-report': {
        'task': 'tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
    }
}

GMAIL_SENDER = os.environ.get('GMAIL_SENDER')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')

def send_email(to_email, subject, body_html):
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        print('Email skipped (GMAIL_SENDER / GMAIL_APP_PASSWORD not configured):', subject)
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        print("Email sent to:", to_email)
    except Exception as e:
        print("Email error:", e)


# Export Applications as CSV
@celery.task
def export_student_applications_csv(student_id):
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            return "Student not found"

        applications = Application.query.filter_by(student_id=student_id).all()

        folder = os.path.join(app.root_path, 'static', 'exports')
        os.makedirs(folder, exist_ok=True)
        filename = f"export_{student_id}.csv"
        filepath = os.path.join(folder, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Dates'])
            
            for a in applications:
                writer.writerow([
                    student.student_id,
                    a.drive.company.company_name if a.drive and a.drive.company else 'N/A',
                    a.drive.job_title if a.drive else 'N/A',
                    a.application_status,
                    str(a.application_date)
                ])

        email_body = f"""
        <h3>Hello {student.student_name},</h3>
        <p>Your placement application history CSV export is ready.</p>
        <p>File saved in static/exports/export_{student_id}.csv</p>
        """
        send_email(student.user.email, "Application Export Ready", email_body)
        return filename


# Daily Reminders
@celery.task
def send_daily_reminders():
    with app.app_context():
        tomorrow = str(datetime.now().date() + timedelta(days=1))
        closing_drives = PlacementDrive.query.filter_by(application_deadline=tomorrow, drive_status='Approved').all()

        if closing_drives:
            drives_list = "".join([f"<li><b>{d.company.company_name}</b>: {d.job_title}</li>" for d in closing_drives if d.company])
            msg_body = f"""
            <h3>Placement Drive Deadline Reminder</h3>
            <p>The following drives are closing tomorrow ({tomorrow}):</p>
            <ul>{drives_list}</ul>
            <p>Please log in and apply before the deadline.</p>
            """

            students = User.query.filter_by(role='Student', is_blacklisted=False).all()
            for s in students:
                send_email(s.email, "Upcoming Application Deadline Reminder", msg_body)


# Monthly Activity Report
@celery.task
def send_monthly_report():
    with app.app_context():
        admin = User.query.filter_by(role='Admin').first()
        if admin:
            total_drives = PlacementDrive.query.count()
            total_apps = Application.query.count()
            selected_apps = Application.query.filter_by(application_status='Selected').count()

            report_html = f"""
            2 Monthly Placement Activity Report
            <hr>
            <p><b>Number of drives conducted:</b> {total_drives}</p>
            <p><b>Number of students applied:</b> {total_apps}</p>
            <p><b>Number of students selected:</b> {selected_apps}</p>
            """
            send_email(admin.email, "Monthly Placement Activity Report", report_html)