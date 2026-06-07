from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    nom: str
    email: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    nom: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    teacher_id: int | None = None


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    teacher_id: int
    pdf_path: str | None
    summary: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class QuizCreate(BaseModel):
    course_id: int
    title: str


class QuizResponse(BaseModel):
    id: int
    course_id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str

    class Config:
        from_attributes = True


class AnswerItem(BaseModel):
    question_id: int
    answer: str


class SubmitQuizRequest(BaseModel):
    student_id: int | None = None
    answers: list[AnswerItem]


class QuizResultResponse(BaseModel):
    id: int
    student_id: int
    quiz_id: int
    score: int
    total_questions: int
    submitted_at: datetime

    class Config:
        from_attributes = True