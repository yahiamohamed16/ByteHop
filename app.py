from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
from datetime import date
from io import BytesIO
import random
import string
import qrcode
import base64
import os
import io


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'edu.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'cs50-secret-key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(300))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
class Progress(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    completed = db.Column(db.Boolean, default=False)
    lesson = db.relationship('Lesson')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("كلمة المرور وتأكيدها غير متطابقين", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("اسم المستخدم موجود بالفعل", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash("تم إنشاء الحساب وتسجيل الدخول بنجاح", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("تم تسجيل الدخول بنجاح", "success")
            return redirect(url_for("index"))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة", "danger")
    
    return render_template("login.html")
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("يجب تسجيل الدخول للوصول لهذه الصفحة", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route("/profile")
@login_required
def profile():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # جلب الدروس التي تم مشاهدتها
    completed_lessons = Progress.query.filter_by(user_id=user_id, completed=True).all()
    
    # تحويل بيانات الدروس لقائمة مفهومة للعرض
    lessons_info = []
    for progress in completed_lessons:
        lesson = Lesson.query.get(progress.lesson_id)
        lessons_info.append({
            "id": lesson.id,
            "title": lesson.title,
            "completed": progress.completed
        })

    return render_template("profile.html", user=user, lessons=lessons_info)


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("تم تسجيل الخروج", "success")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/thebook")
@login_required

def thebook():
    return render_template("thebook.html")

@app.route("/qureo")
@login_required

def qureo():
    return render_template("qureo.html")


@app.route("/lesson/<int:lesson_id>")
@app.route("/lesson/<int:lesson_id>/")
@login_required
def lesson(lesson_id):
    lesson_data = Lesson.query.get_or_404(lesson_id)

    lesson_dict = {
        "id": lesson_data.id,
        "title": lesson_data.title,
        "video_url": lesson_data.video_url
    }
    return render_template("lesson.html", lesson=lesson_dict)

@app.route("/lesson/complete/<int:lesson_id>", methods=["POST"])
@login_required
def complete_lesson(lesson_id):
    user_id = session['user_id']
    progress = Progress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not progress:
        progress = Progress(user_id=user_id, lesson_id=lesson_id, completed=True)
        db.session.add(progress)
    else:
        progress.completed = True  # تحديث بدل إضافة جديد
    db.session.commit()
    flash("تم وضع الدرس كمكتمل", "success")
    return redirect(url_for('lesson', lesson_id=lesson_id))

@app.route("/certificates")
@login_required
def certificates():
    subjects = Subject.query.all()
    user_id = session['user_id']

    progress = {}
    for subject in subjects:
        total_lessons = Lesson.query.filter_by(subject_id=subject.id).count()
        completed = Progress.query.filter_by(
            user_id=user_id, completed=True
        ).join(Lesson).filter(Lesson.subject_id == subject.id).count()

        progress[subject.id] = {
            "completed": completed,
            "total": total_lessons,
            "percentage": int((completed / total_lessons) * 100) if total_lessons else 0
        }

    return render_template("certificates.html", subjects=subjects, progress=progress)

@app.route("/request_certificate/<int:subject_id>", methods=["POST"])
@login_required
def request_certificate(subject_id):
    user_id = session['user_id']
    subject = Subject.query.get_or_404(subject_id)

    total_lessons = Lesson.query.filter_by(subject_id=subject.id).count()
    completed_count = Progress.query.join(Lesson).filter(
        Progress.user_id == user_id,
        Progress.completed == True,
        Lesson.subject_id == subject.id
    ).count()

    if not total_lessons or completed_count != total_lessons:
        flash("عليك إتمام جميع الدروس للحصول على الشهادة", "warning")
        return redirect(url_for('certificates'))

    issue_date = date.today().strftime("%d/%m/%Y")
    certificate_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # QR
    verify_url = url_for('verify_certificate', certificate_id=certificate_id, _external=True)
    qr = qrcode.make(verify_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    user = User.query.get(session['user_id'])

    return render_template(
        "certificate_generated.html",
        user_name=user.username,
        subject=subject,
        issue_date=issue_date,
        certificate_id=certificate_id,
        qr_code_base64=qr_base64
    )


@app.route("/verify/<certificate_id>")
def verify_certificate(certificate_id):
    return f"الشهادة رقم {certificate_id} صحيحة ✔"

@app.route("/certificate/<int:subject_id>", methods=["GET", "POST"])
@login_required
def choose_certificate_name(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == "POST":
        name_on_certificate = request.form.get("name")
        return redirect(url_for("generate_certificate", subject_id=subject.id, name=name_on_certificate))
    
    return render_template("certificate.html", subject=subject)
@app.route("/generate_certificate/<int:subject_id>")
@login_required
def generate_certificate(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    user_name = request.args.get("name")  # الاسم اللي كتبه المستخدم

    issue_date = date.today().strftime("%d/%m/%Y")
    certificate_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # QR code
    verify_url = url_for('verify_certificate', certificate_id=certificate_id, _external=True)
    qr = qrcode.make(verify_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template(
        "certificate_generated.html",
        user_name=user_name,
        subject=subject,
        issue_date=issue_date,
        certificate_id=certificate_id,
        qr_code_base64=qr_base64
    )





with app.app_context():
    db.create_all()

    if not Subject.query.filter_by(name="البرمجة").first():
        db.session.add(Subject(name="البرمجة"))

    if not Subject.query.filter_by(name="منصة Qureo").first():
        db.session.add(Subject(name="منصة Qureo"))

    db.session.commit()
    print("Database & subjects ready!")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
