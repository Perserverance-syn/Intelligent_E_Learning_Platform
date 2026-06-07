from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Course, Quiz, Question, QuizResult, User
from schemas import QuizResponse, QuestionResponse, SubmitQuizRequest, QuizResultResponse
from auth import require_role
import fitz
import re

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def extract_text_from_pdf(pdf_path: str):
    text = ""

    document = fitz.open(pdf_path)

    for page in document:
        text += page.get_text()

    document.close()

    return text


def clean_text(text: str):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_questions_from_text(text: str, max_questions: int = 5):
    text = clean_text(text)
    sentences = re.split(r"(?<=[.!?]) +", text)

    questions = []

    for sentence in sentences:
        words = sentence.split()

        if len(words) < 10:
            continue

        keyword = words[0]

        question_text = f"Quel est le sujet principal de cette phrase : « {sentence[:120]}... » ?"

        question = {
            "question": question_text,
            "option_a": keyword,
            "option_b": "Une base de données",
            "option_c": "Un réseau informatique",
            "option_d": "Un système d’exploitation",
            "correct_answer": "A"
        }

        questions.append(question)

        if len(questions) >= max_questions:
            break

    return questions


@router.post("/generate/{course_id}", response_model=QuizResponse)
def generate_quiz(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["enseignant", "admin"]))
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    if not course.pdf_path:
        raise HTTPException(status_code=400, detail="Aucun PDF trouvé pour ce cours")

    text = extract_text_from_pdf(course.pdf_path)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF")

    quiz = Quiz(
        course_id=course.id,
        title=f"Quiz automatique - {course.title}"
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    generated_questions = generate_questions_from_text(text)

    if not generated_questions:
        raise HTTPException(status_code=400, detail="Impossible de générer des questions")

    for q in generated_questions:
        question = Question(
            quiz_id=quiz.id,
            question=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"]
        )

        db.add(question)

    db.commit()

    return quiz


@router.get("/", response_model=list[QuizResponse])
def get_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).all()
    return quizzes


@router.get("/{quiz_id}/questions", response_model=list[QuestionResponse])
def get_quiz_questions(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()

    return questions


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz(
    quiz_id: int,
    request: SubmitQuizRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["etudiant", "admin"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()

    if not questions:
        raise HTTPException(status_code=400, detail="Aucune question trouvée pour ce quiz")

    correct_answers = {
        question.id: question.correct_answer.upper()
        for question in questions
    }

    score = 0

    for answer_item in request.answers:
        question_id = answer_item.question_id
        student_answer = answer_item.answer.upper()

        if question_id in correct_answers and student_answer == correct_answers[question_id]:
            score += 1

    result = QuizResult(
        student_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total_questions=len(questions)
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result


@router.get("/results/all", response_model=list[QuizResultResponse])
def get_all_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "enseignant"]))
):
    results = db.query(QuizResult).all()
    return results


@router.get("/results/student/{student_id}", response_model=list[QuizResultResponse])
def get_student_results(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "enseignant", "etudiant"]))
):
    if current_user.role == "etudiant" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    results = db.query(QuizResult).filter(QuizResult.student_id == student_id).all()
    return results