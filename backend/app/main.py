import os
from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from .database import create_tables
from .routers import applications, auth, documents, notifications, scholarships, students
from .services.ocr_service import configure_tesseract

app = FastAPI(title="Smart College Admission API", version="0.1.0")

allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(scholarships.router, prefix="/api")
app.include_router(scholarships.student_router, prefix="/api")
app.include_router(scholarships.application_router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    create_tables()
    configure_tesseract()


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
