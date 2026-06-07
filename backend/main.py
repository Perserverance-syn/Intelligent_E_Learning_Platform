from fastapi import FastAPI
from database import engine, Base
import models
from routes import users, courses, quiz, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartLearn AI API",
    description="Backend de la plateforme e-learning intelligente",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(quiz.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {"message": "SmartLearn AI Backend is running"}


@app.get("/test-db")
def test_db():
    return {"message": "Database connected successfully"}