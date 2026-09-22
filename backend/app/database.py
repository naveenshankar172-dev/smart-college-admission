from collections.abc import Generator
import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'admissions.db'}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_student_columns()
    _migrate_document_columns()
    _migrate_scholarship_columns()
    _migrate_scholarship_application_constraints()
    _seed_sample_scholarships()


def _migrate_student_columns() -> None:
    inspector = inspect(engine)
    if "students" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("students")}
    additions = {
        "date_of_birth": "VARCHAR(20)",
        "firebase_uid": "VARCHAR(128)",
        "academic_year": "VARCHAR(40)",
        "password_hash": "VARCHAR(128)",
        "email_updates": "BOOLEAN NOT NULL DEFAULT 1",
        "scholarship_suggestions": "BOOLEAN NOT NULL DEFAULT 1",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE students ADD COLUMN {name} {definition}"))


def _migrate_scholarship_application_constraints() -> None:
    inspector = inspect(engine)
    if "scholarship_applications" not in inspector.get_table_names():
        return
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_active_scholarship_application
            ON scholarship_applications (student_id, scholarship_id)
            WHERE application_status NOT IN ('Rejected', 'Closed')
        """))


def _migrate_document_columns() -> None:
    inspector = inspect(engine)
    if "documents" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("documents")}
    additions = {
        "student_id": "INTEGER",
        "document_type": "VARCHAR(120)",
        "original_filename": "VARCHAR(255)",
        "stored_filename": "VARCHAR(255)",
        "file_type": "VARCHAR(100)",
        "file_size": "INTEGER",
        "upload_date": "DATETIME",
        "verification_status": "VARCHAR(40) DEFAULT 'pending'",
        "extracted_text": "TEXT",
        "ocr_status": "VARCHAR(40) DEFAULT 'not_started'",
        "ocr_processed_at": "DATETIME",
        "matched_fields": "TEXT",
        "mismatched_fields": "TEXT",
        "processing_status": "VARCHAR(40) DEFAULT 'pending'",
        "processing_started_at": "DATETIME",
        "processing_completed_at": "DATETIME",
        "processing_error": "TEXT",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE documents ADD COLUMN {name} {definition}"))


def _migrate_scholarship_columns() -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        if "scholarships" in inspector.get_table_names():
            existing = {column["name"] for column in inspector.get_columns("scholarships")}
            additions = {
                "scheme_name": "VARCHAR(180)", "eligibility_rules": "TEXT", "required_documents": "TEXT",
                "application_start_date": "DATETIME", "application_end_date": "DATETIME",
                "amount_or_benefit": "VARCHAR(120)", "status": "VARCHAR(40) DEFAULT 'active'",
                "created_at": "DATETIME", "updated_at": "DATETIME",
            }
            for name, definition in additions.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE scholarships ADD COLUMN {name} {definition}"))
        if "scholarship_applications" in inspector.get_table_names():
            existing = {column["name"] for column in inspector.get_columns("scholarship_applications")}
            additions = {
                "verification_status": "VARCHAR(60) DEFAULT 'pending'", "remarks": "TEXT",
                "applied_at": "DATETIME", "updated_at": "DATETIME",
            }
            for name, definition in additions.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE scholarship_applications ADD COLUMN {name} {definition}"))


def _seed_sample_scholarships() -> None:
    from datetime import datetime
    import json

    if "scholarships" not in inspect(engine).get_table_names():
        return
    with SessionLocal() as db:
        if db.scalar(text("SELECT COUNT(*) FROM scholarships")):
            return
        samples = [
            ("Sample Merit Scholarship", "Sample Education Foundation", "Configurable demo scholarship. Not an official government scheme.", {"min_percentage": 80}, ["ID Proof"]),
            ("Sample Need-Based Scholarship", "Sample Student Support Trust", "Configurable demo scholarship. Not an official government scheme.", {"requires_income_information": True}, ["ID Proof", "Income Certificate"]),
            ("Sample Academic Support Scholarship", "Sample Academic Initiative", "Configurable demo scholarship. Not an official government scheme.", {"min_percentage": 70, "course_contains": ""}, ["ID Proof", "12th Marksheet"]),
        ]
        for name, provider, description, rules, documents in samples:
            db.execute(text("""INSERT INTO scholarships (name, scheme_name, provider, description, eligibility_summary, eligibility_rules, required_documents, amount, amount_or_benefit, status, is_active, created_at, updated_at) VALUES (:name, :scheme_name, :provider, :description, :summary, :rules, :documents, :amount, :benefit, 'active', 1, :created_at, :updated_at)"""), {
                "name": name, "scheme_name": name, "provider": provider, "description": description,
                "summary": "Eligibility screening only; final eligibility requires verification.",
                "rules": json.dumps(rules), "documents": json.dumps(documents), "amount": "Demo benefit",
                "benefit": "Demo benefit", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
            })
        db.commit()
