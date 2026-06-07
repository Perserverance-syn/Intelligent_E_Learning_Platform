from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Course, User
from schemas import CourseCreate, CourseResponse
from auth import require_role
import shutil
import os
import fitz
import re

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

UPLOAD_DIR = "uploads"


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


def generate_simple_summary(text: str, max_sentences: int = 5):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    sentences = re.split(r"(?<=[.!?]) +", text)

    important_sentences = []

    for sentence in sentences:
        if len(sentence.split()) > 8:
            important_sentences.append(sentence)

        if len(important_sentences) >= max_sentences:
            break

    if not important_sentences:
        return "Résumé non disponible. Le texte du PDF est trop court ou mal extrait."

    return " ".join(important_sentences)


@router.post("/", response_model=CourseResponse)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["enseignant", "admin"]))
):
    new_course = Course(
        title=course.title,
        description=course.description,
        teacher_id=current_user.id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.get("/", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses


@router.post("/{course_id}/upload-pdf", response_model=CourseResponse)
def upload_pdf(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["enseignant", "admin"]))
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, f"course_{course_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    course.pdf_path = file_path

    db.commit()
    db.refresh(course)

    return course


@router.get("/{course_id}/extract-text")
def extract_course_text(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    if not course.pdf_path:
        raise HTTPException(status_code=400, detail="Aucun PDF trouvé pour ce cours")

    text = extract_text_from_pdf(course.pdf_path)

    return {
        "course_id": course.id,
        "title": course.title,
        "text_preview": text[:2000]
    }


@router.post("/{course_id}/generate-summary", response_model=CourseResponse)
def generate_course_summary(
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

    summary = generate_simple_summary(text)

    course.summary = summary

    db.commit()
    db.refresh(course)

    return course