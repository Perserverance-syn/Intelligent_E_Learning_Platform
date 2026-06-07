from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Course, Quiz, QuizResult

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "etudiant").count()
    total_teachers = db.query(User).filter(User.role == "enseignant").count()
    total_admins = db.query(User).filter(User.role == "admin").count()

    total_courses = db.query(Course).count()
    total_quizzes = db.query(Quiz).count()
    total_results = db.query(QuizResult).count()

    results = db.query(QuizResult).all()

    if results:
        total_score = sum(result.score for result in results)
        total_questions = sum(result.total_questions for result in results)
        average_score = round((total_score / total_questions) * 100, 2)
    else:
        average_score = 0

    return {
        "users": {
            "total": total_users,
            "students": total_students,
            "teachers": total_teachers,
            "admins": total_admins
        },
        "courses": {
            "total": total_courses
        },
        "quizzes": {
            "total": total_quizzes,
            "results": total_results,
            "average_score_percent": average_score
        }
    }