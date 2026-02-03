from app import app, db, Lesson

with app.app_context():  # هنا نفتح الـ context
    lesson39 = Lesson(
        title="شرح for loop في JavaScript ببساطة | Chapter 22",
        description="1",
        video_url="https://www.youtube.com/watch?v=63UqxaAWmtg",
        quiz_url="https://docs.google.com/forms/d/e/1FAIpQLSdOSdAu1xM4jdGumsleHHlliABkwxqlKD9SZnl1YrRJXR1Xtg/viewform?usp=dialog",
        subject_id=2
    )
    
    db.session.add(lesson39)
    db.session.commit()
    print("Lesson added successfully!")
