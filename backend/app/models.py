from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    firebase_uid: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    course: Mapped[Optional[str]] = mapped_column(String(160))
    academic_score: Mapped[Optional[float]] = mapped_column()
    city: Mapped[Optional[str]] = mapped_column(String(100))
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(20))
    academic_year: Mapped[Optional[str]] = mapped_column(String(40))
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))
    email_updates: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scholarship_suggestions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    applications: Mapped[list["Application"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    scholarship_applications: Mapped[list["ScholarshipApplication"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    course: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    student: Mapped["Student"] = relationship(back_populates="applications")
    documents: Mapped[list["Document"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[Optional[int]] = mapped_column(ForeignKey("applications.id"), nullable=True, index=True)
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    document_type: Mapped[Optional[str]] = mapped_column(String(120))
    original_filename: Mapped[Optional[str]] = mapped_column(String(255))
    stored_filename: Mapped[Optional[str]] = mapped_column(String(255))
    file_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    upload_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    verification_status: Mapped[str] = mapped_column(String(40), default="pending", nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    ocr_status: Mapped[str] = mapped_column(String(40), default="not_started", nullable=False)
    ocr_processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    matched_fields: Mapped[Optional[str]] = mapped_column(Text)
    mismatched_fields: Mapped[Optional[str]] = mapped_column(Text)
    processing_status: Mapped[str] = mapped_column(String(40), default="pending", nullable=False)
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="missing", nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    application: Mapped["Application"] = relationship(back_populates="documents")
    student: Mapped[Optional["Student"]] = relationship()


class Scholarship(Base):
    __tablename__ = "scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    provider: Mapped[str] = mapped_column(String(180), nullable=False)
    amount: Mapped[Optional[str]] = mapped_column(String(80))
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)
    eligibility_summary: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scheme_name: Mapped[Optional[str]] = mapped_column(String(180), index=True)
    eligibility_rules: Mapped[Optional[str]] = mapped_column(Text)
    required_documents: Mapped[Optional[str]] = mapped_column(Text)
    application_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    application_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    amount_or_benefit: Mapped[Optional[str]] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    applications: Mapped[list["ScholarshipApplication"]] = relationship(back_populates="scholarship", cascade="all, delete-orphan")


class ScholarshipApplication(Base):
    __tablename__ = "scholarship_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scholarship_id: Mapped[int] = mapped_column(ForeignKey("scholarships.id"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    eligibility_status: Mapped[str] = mapped_column(String(60), default="Requires Verification", nullable=False)
    document_status: Mapped[str] = mapped_column(String(60), default="pending", nullable=False)
    application_status: Mapped[str] = mapped_column(String(60), default="Applied", nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    verification_status: Mapped[str] = mapped_column(String(60), default="pending", nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    scholarship: Mapped["Scholarship"] = relationship(back_populates="applications")
    student: Mapped["Student"] = relationship(back_populates="scholarship_applications")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(40), default="system", nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    student: Mapped["Student"] = relationship(back_populates="notifications")
