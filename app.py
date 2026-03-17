import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Complaint, Reply
from ai_helper import (
    analyze_sentiment, categorize_complaint, generate_reply,
    generate_suggestion, generate_weekly_summary
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ PUBLIC ROUTES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('dashboard'))
        return redirect(url_for('my_complaints'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            if user.is_admin():
                return redirect(url_for('dashboard'))
            return redirect(url_for('my_complaints'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ STUDENT ROUTES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route('/complaint/new', methods=['GET', 'POST'])
@login_required
def new_complaint():
    if current_user.is_admin():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        department = request.form.get('department', '').strip()

        if not title or not description or not department:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('new_complaint'))

        # AI sentiment analysis
        sentiment = analyze_sentiment(f"{title}. {description}")

        # Handle file upload
        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename and allowed_file(file.filename):
                attachment_filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename))

        complaint = Complaint(
            user_id=current_user.id,
            title=title,
            description=description,
            department=department,
            sentiment=sentiment,
            attachment=attachment_filename
        )
        db.session.add(complaint)
        db.session.commit()

        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('my_complaints'))

    return render_template('complaint_form.html')


@app.route('/my-complaints')
@login_required
def my_complaints():
    if current_user.is_admin():
        return redirect(url_for('dashboard'))

    complaints = Complaint.query.filter_by(user_id=current_user.id)\
        .order_by(Complaint.created_at.desc()).all()
    return render_template('my_complaints.html', complaints=complaints)


    # Soft delete â€” hide from student but keep in admin dashboard
    complaint.hidden_by_user = True
    db.session.commit()

    flash('Complaint deleted successfully.', 'success')
    return redirect(url_for('my_complaints'))


@app.route('/complaint/<int:complaint_id>')
@login_required
def complaint_detail(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)

    # Students can only view their own complaints
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('my_complaints'))

    return render_template('complaint_detail.html', complaint=complaint)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ ADMIN ROUTES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin():
        return redirect(url_for('my_complaints'))

    # Stats
    total = Complaint.query.count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    urgent_today = Complaint.query.filter(
        Complaint.sentiment == 'Urgent',
        Complaint.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()

    resolved_pct = round((resolved / total * 100), 1) if total > 0 else 0

    # Top department
    departments = db.session.query(
        Complaint.department, db.func.count(Complaint.id)
    ).group_by(Complaint.department).order_by(db.func.count(Complaint.id).desc()).all()

    top_dept = departments[0][0] if departments else 'N/A'

    # Department chart data
    dept_labels = [d[0] for d in departments]
    dept_counts = [d[1] for d in departments]

    # Weekly trend data (last 7 days)
    trend_labels = []
    trend_counts = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = Complaint.query.filter(
            Complaint.created_at >= day_start,
            Complaint.created_at < day_end
        ).count()
        trend_labels.append(day.strftime('%a'))
        trend_counts.append(count)

    # All complaints for table
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    return render_template('dashboard.html',
                           total=total, resolved=resolved, resolved_pct=resolved_pct,
                           urgent_today=urgent_today, top_dept=top_dept,
                           dept_labels=dept_labels, dept_counts=dept_counts,
                           trend_labels=trend_labels, trend_counts=trend_counts,
                           complaints=complaints)


@app.route('/complaint/<int:complaint_id>/reply', methods=['POST'])
@login_required
def reply_complaint(complaint_id):
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('my_complaints'))

    complaint = Complaint.query.get_or_404(complaint_id)
    reply_text = request.form.get('reply_text', '').strip()

    if not reply_text:
        flash('Reply cannot be empty.', 'danger')
        return redirect(url_for('complaint_detail', complaint_id=complaint_id))

    reply = Reply(
        complaint_id=complaint_id,
        reply_text=reply_text,
        is_ai=False
    )
    db.session.add(reply)
    db.session.commit()

    flash('Reply sent successfully!', 'success')
    return redirect(url_for('complaint_detail', complaint_id=complaint_id))


@app.route('/complaint/<int:complaint_id>/status', methods=['POST'])
@login_required
def update_status(complaint_id):
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403

    complaint = Complaint.query.get_or_404(complaint_id)
    new_status = request.form.get('status', complaint.status)
    complaint.status = new_status
    db.session.commit()

    flash(f'Status updated to {new_status}.', 'success')
    return redirect(url_for('complaint_detail', complaint_id=complaint_id))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ AI API ROUTES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route('/api/ai-suggest', methods=['POST'])
@login_required
def ai_suggest():
    data = request.get_json()
    text = data.get('text', '')
    if len(text) < 15:
        return jsonify({'suggestion': ''})

    suggestion = generate_suggestion(text)
    return jsonify({'suggestion': suggestion or ''})


@app.route('/api/ai-reply', methods=['POST'])
@login_required
def ai_reply():
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    complaint_id = data.get('complaint_id')
    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    reply_text = generate_reply(complaint.title, complaint.description, complaint.department)

    # Save AI reply
    reply = Reply(
        complaint_id=complaint_id,
        reply_text=reply_text,
        is_ai=True
    )
    db.session.add(reply)
    db.session.commit()

    return jsonify({
        'reply': reply_text,
        'created_at': reply.created_at.strftime('%b %d, %Y %I:%M %p')
    })


@app.route('/api/ai-sentiment', methods=['POST'])
@login_required
def ai_sentiment():
    data = request.get_json()
    text = data.get('text', '')
    sentiment = analyze_sentiment(text)
    return jsonify({'sentiment': sentiment})


@app.route('/api/ai-summary', methods=['POST'])
@login_required
def ai_summary():
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403

    # Get this week's complaints
    week_ago = datetime.utcnow() - timedelta(days=7)
    complaints = Complaint.query.filter(Complaint.created_at >= week_ago).all()

    if not complaints:
        return jsonify({'summary': 'No complaints received this week.'})

    # Build data string for AI
    complaints_text = ""
    for c in complaints:
        complaints_text += (
            f"- [{c.sentiment}] {c.department}: {c.title} â€” {c.description[:100]}\n"
        )

    summary = generate_weekly_summary(complaints_text)
    return jsonify({'summary': summary})


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ INIT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def create_tables():
    """Create database tables and default admin account."""
    db.create_all()

    # Create default admin if not exists
    admin = User.query.filter_by(email='admin@smartcampus.com').first()
    if not admin:
        admin = User(name='Admin', email='admin@smartcampus.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("[OK] Default admin created: admin@smartcampus.com / admin123")


if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True, port=5000)
