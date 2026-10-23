from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
from models import db, User, Student, Company, PlacementDrive, Application

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.sqlite3')
if db_url.startswith('postgres://'):          # Render/Neon style URL -> SQLAlchemy style
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'placement-portal-v2-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=24)

# Redis is optional: use it when REDIS_URL is set, otherwise fall back to an in-memory cache
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = REDIS_URL
else:
    app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60
cache = Cache(app)

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(role='Admin').first()
    if not admin:
        hashed_admin_password = generate_password_hash('admin123')
        admin_user = User(
            username='admin',
            email='admin@user.com',
            password=hashed_admin_password,
            role='Admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Database Initialized & Admin Created Successfully!")



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if user.is_blacklisted:
        return jsonify({'message': 'Your account is blacklisted by Admin.'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': user.role,
            'username': user.username,
            'email': user.email
        }
    )

    return jsonify({
        'message': 'Login successful',
        'token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    role = data.get('role')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if role == 'Admin':
        return jsonify({'message': 'Admin registration is not allowed!'}), 403

    if not email or not username or not password or not role:
        return jsonify({'message': 'All basic details are required!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email address already registered'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already taken'}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role
    )
    db.session.add(new_user)
    db.session.commit()

    if role == 'Student':
        new_student = Student(
            user_id=new_user.id,
            student_name=data.get('student_name', username),
            skills=data.get('skills', ''),
            contact_info=data.get('contact_info', '')
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({'message': 'Student registered successfully!'}), 201

    elif role == 'Company':
        new_company = Company(
            user_id=new_user.id,
            company_name=data.get('company_name', username),
            hr_contact=data.get('hr_contact', ''),
            website=data.get('website', '')
        )
        db.session.add(new_company)
        db.session.commit()
        return jsonify({'message': 'Company registered successfully. Pending Admin approval.'}), 201

    else:
        return jsonify({'message': 'Invalid role specified'}), 400








@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()      
def admin_dashboard():
    claims = get_jwt()       
    if claims.get('role') != 'Admin':   
        return jsonify({'message': 'Admin access required!'}), 403

    stats = {
        "total_students": Student.query.count(),
        "total_company": Company.query.count(),
        "total_drives": PlacementDrive.query.count(),
        "total_applications": Application.query.count()
    }

    pending_companies = Company.query.filter_by(approval_status='Pending').all()
    pending_drives = PlacementDrive.query.filter_by(drive_status='Pending').all()
    all_users = User.query.filter(User.role != 'Admin').all()
    all_apps = Application.query.all()

    return jsonify({
        'stats': stats,
        'pending_companies': [
            {'company_id': c.company_id, 'company_name': c.company_name, 'website': c.website or 'N/A'} 
            for c in pending_companies
        ],
        'pending_drives': [
            {'drive_id': d.drive_id, 'job_title': d.job_title, 'company_name': d.company.company_name} 
            for d in pending_drives
        ],
        'users': [
            {'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role, 'is_blacklisted': u.is_blacklisted} 
            for u in all_users
        ],
        'applications': [
            {
                'id': a.application_id,
                'student_name': a.student.student_name,
                'job_title': a.drive.job_title,
                'company_name': a.drive.company.company_name,
                'status': a.application_status
            }
            for a in all_apps
        ]
    }), 200


@app.route('/api/admin/approve_company/<int:company_id>', methods=['POST'])
@jwt_required()
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'Approved'
    for drive in company.drives:
        drive.drive_status = 'Approved'
    db.session.commit()
    cache.clear() 
    return jsonify({'message': 'Company approved successfully!'}), 200


@app.route('/api/admin/reject_company/<int:company_id>', methods=['POST'])
@jwt_required()
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'Rejected'
    for drive in company.drives:
        drive.drive_status = 'Cancelled'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Company rejected.'}), 200


@app.route('/api/admin/approve_drive/<int:drive_id>', methods=['POST'])
@jwt_required()
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.drive_status = 'Approved'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Drive approved!'}), 200


@app.route('/api/admin/reject_drive/<int:drive_id>', methods=['POST'])
@jwt_required()
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.drive_status = 'Rejected'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Drive rejected.'}), 200


@app.route('/api/admin/blacklist_user/<int:user_id>', methods=['POST'])
@jwt_required()
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = not user.is_blacklisted
    
    if user.is_blacklisted and user.role == 'Company' and user.company:
        for drive in user.company.drives:
            drive.drive_status = 'Cancelled'

    db.session.commit()
    cache.clear()
    status = "blacklisted" if user.is_blacklisted else "unblacklisted"
    return jsonify({'message': f'User {user.username} {status} successfully!'}), 200











@app.route('/api/company/dashboard', methods=['GET'])
@jwt_required()
def company_dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if user.role != 'Company':
        return jsonify({'message': 'Company access required!'}), 403

    company = user.company
    if not company:
        return jsonify({'message': 'Company profile not found!'}), 404

    drives = PlacementDrive.query.filter_by(company_id=company.company_id).all()

    return jsonify({
        'company': {
            'company_id': company.company_id,
            'company_name': company.company_name,
            'website': company.website or '',
            'hr_contact': company.hr_contact or '',
            'approval_status': company.approval_status
        },
        'drives': [
            {
                'drive_id': d.drive_id,
                'job_title': d.job_title,
                'job_description': d.job_description,
                'eligibility_criteria': d.eligibility_criteria,
                'application_deadline': d.application_deadline,
                'drive_status': d.drive_status,
                'applications_count': len(d.applications)
            }
            for d in drives
        ]
    }), 200


@app.route('/api/company/create_drive', methods=['POST'])
@jwt_required()
def create_drive():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    company = user.company

    if company.approval_status != 'Approved':
        return jsonify({'message': 'Only approved companies can create placement drives!'}), 403

    data = request.get_json() or {}
    job_title = data.get('job_title')
    job_description = data.get('job_description')
    eligibility_criteria = data.get('eligibility_criteria', '')
    application_deadline = data.get('application_deadline')

    if not job_title or not job_description or not application_deadline:
        return jsonify({'message': 'Job title, description, and deadline are required!'}), 400

    new_drive = PlacementDrive(
        company_id=company.company_id,
        job_title=job_title,
        job_description=job_description,
        eligibility_criteria=eligibility_criteria,
        application_deadline=application_deadline,
        drive_status='Pending'
    )
    db.session.add(new_drive)
    db.session.commit()

    return jsonify({'message': 'Placement drive created and sent for Admin approval!'}), 201


@app.route('/api/company/drive_applications/<int:drive_id>', methods=['GET'])
@jwt_required()
def view_drive_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    apps = Application.query.filter_by(drive_id=drive_id).all()

    return jsonify({
        'drive_title': drive.job_title,
        'applications': [
            {
                'application_id': a.application_id,
                'student_name': a.student.student_name,
                'skills': a.student.skills,
                'contact_info': a.student.contact_info,
                'status': a.application_status
            }
            for a in apps
        ]
    }), 200


@app.route('/api/company/update_app_status/<int:app_id>', methods=['POST'])
@jwt_required()
def update_application_status(app_id):
    data = request.get_json() or {}
    new_status = data.get('status')

    application = Application.query.get_or_404(app_id)
    application.application_status = new_status
    db.session.commit()

    return jsonify({'message': f'Application status updated to {new_status}'}), 200






@app.route('/api/student/dashboard', methods=['GET'])
@jwt_required()
def student_dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if user.role != 'Student':
        return jsonify({'message': 'Student access required!'}), 403

    student = user.student
    if not student:
        return jsonify({'message': 'Student profile not found!'}), 404

    approved_drives = PlacementDrive.query.filter_by(drive_status='Approved').all()
    
    applications = Application.query.filter_by(student_id=student.student_id).all()
    
    applied_drive_ids = set(app.drive_id for app in applications)

    return jsonify({
        'student': {
            'student_id': student.student_id,
            'student_name': student.student_name,
            'skills': student.skills or '',
            'contact_info': student.contact_info or '',
            'resume': student.resume or ''
        },
        'approved_drives': [
            {
                'drive_id': d.drive_id,
                'job_title': d.job_title,
                'company_name': d.company.company_name,
                'job_description': d.job_description,
                'eligibility_criteria': d.eligibility_criteria,
                'application_deadline': d.application_deadline,
                'is_applied': True if d.drive_id in applied_drive_ids else False
            }
            for d in approved_drives
        ],
        'applications': [
            {
                'application_id': a.application_id,
                'job_title': a.drive.job_title,
                'company_name': a.drive.company.company_name,
                'application_date': str(a.application_date),
                'status': a.application_status
            }
            for a in applications
        ]
    }), 200


@app.route('/api/student/apply/<int:drive_id>', methods=['POST'])
@jwt_required()
def apply_for_drive(drive_id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    student = user.student

    existing_app = Application.query.filter_by(student_id=student.student_id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({'message': 'You have already applied for this drive!'}), 400

    new_app = Application(
        student_id=student.student_id,
        drive_id=drive_id,
        application_status='Applied'
    )
    db.session.add(new_app)
    db.session.commit()
    cache.clear() 

    return jsonify({'message': 'Application submitted successfully!'}), 201


@app.route('/api/student/update_profile', methods=['POST'])
@jwt_required()
def update_student_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    student = user.student

    data = request.get_json() or {}
    student.student_name = data.get('student_name', student.student_name)
    student.skills = data.get('skills', student.skills)
    student.contact_info = data.get('contact_info', student.contact_info)
    student.resume = data.get('resume', student.resume)

    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Profile updated successfully!'}), 200


# ===============================================================
@app.route('/api/student/export_csv', methods=['POST'])
@jwt_required()
def export_csv():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if user.role != 'Student':
        return jsonify({'message': 'Student access required!'}), 403

    student = user.student
    if not student:
        return jsonify({'message': 'Student profile not found!'}), 404

    from tasks import export_student_applications_csv
    if os.environ.get('CELERY_BROKER_URL'):
        # A Celery worker + Redis broker are available
        export_student_applications_csv.delay(student.student_id)
    else:
        # No worker on free hosting: run the same task in a background thread instead
        import threading
        threading.Thread(
            target=export_student_applications_csv.run,
            args=(student.student_id,),
            daemon=True
        ).start()

    return jsonify({'message': 'Export process started. You will receive an email once it is ready.'}), 200


@app.route('/api/student/download_csv/<filename>', methods=['GET'])
def download_csv(filename):
    exports_dir = os.path.join(app.root_path, 'static', 'exports')
    return send_from_directory(exports_dir, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')