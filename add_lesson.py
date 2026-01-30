from app import app, db, Lesson

with app.app_context():  # هنا نفتح الـ context
    lesson38 = Lesson(
        title="شرح Chapter 21 | الشروط (Conditions)",
        description="1",
        video_url="https://www.youtube.com/watch?v=bxptmGCAJJI",
        quiz_url="https://docs.google.com/forms/d/e/1FAIpQLSfp0yTPx-IbEbsALgvDwbL3IhkT8DOHEwo_6raImP5bWvvYzg/viewform?usp=publish-editor",
        subject_id=2
    )
    
    db.session.add(lesson38)
    db.session.commit()
    print("Lesson added successfully!")
