from app import app, db, Subject

with app.app_context():
    db.create_all()

    if not Subject.query.filter_by(name="البرمجة الكتاب النظري").first():
        db.session.add(Subject(name="البرمجة الكتاب النظري"))

    if not Subject.query.filter_by(name="منصة Qureo").first():
        db.session.add(Subject(name="منصة Qureo"))

    db.session.commit()
    print("Database & subjects ready!")
