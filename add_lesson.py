from app import app, db, Lesson

with app.app_context():  # هنا نفتح الـ context
    lesson37 = Lesson(
        title="Chapter 18 Qureo: دليلك لإنشاء موقع ويب للصف الأول الثانوي",
        description="في هذا الفيديو من Chapter 18 على Qureo، ستتعلم أساسيات HTML لبناء موقع إلكتروني: الوسوم الأساسية، القوائم، وعرض الصور بطريقة سهلة مع أمثلة عملية واقعية.",
        video_url="https://www.youtube.com/watch?v=IkzFl60Jac0",
        quiz_url="https://docs.google.com/forms/d/e/1FAIpQLSddwhwt5PnLAzhV1x0d0huB447727W7Zl-GmIzDY6powfnLhg/viewform",
        subject_id=2
    )
    
    db.session.add(lesson37)
    db.session.commit()
    print("Lesson added successfully!")
