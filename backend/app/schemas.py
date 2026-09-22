from datetime import datetime
from typing import Optional

import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str
    phone: Optional[str] = None
    course: Optional[str] = None
    academic_score: Optional[float] = Field(default=None, ge=0, le=100)
    city: Optional[str] = None
    date_of_birth: Optional[str] = None
    academic_year: Optional[str] = None
    email_updates: bool = True
    scholarship_suggestions: bool = True


class StudentCreate(StudentBase):
    password: str | None = None


class FirebaseOnboarding(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=7, max_length=32)
    course: str = Field(min_length=1, max_length=160)
    academic_year: str = Field(min_length=1, max_length=40)


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: str | None = None
    phone: str | None = None
    course: str | None = None
    academic_score: float | None = Field(default=None, ge=0, le=100)
    city: str | None = None
    date_of_birth: str | None = None
    academic_year: str | None = None
    email_updates: bool | None = None
    scholarship_suggestions: bool | None = None


class StudentRead(StudentBase, ORMModel):
    id: int
    created_at: datetime


class DocumentBase(BaseModel):
    name: str
    document_type: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    stored_filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    verification_status: str = "pending"
    extracted_text: Optional[str] = None
    ocr_status: str = "not_started"
    ocr_processed_at: Optional[datetime] = None
    matched_fields: Optional[str] = None
    mismatched_fields: Optional[str] = None
    processing_status: str = "pending"
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    status: str = "missing"
    remarks: Optional[str] = None


class DocumentCreate(DocumentBase):
    application_id: Optional[int] = None
    student_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    status: str | None = None
    remarks: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    verification_status: str | None = None


class DocumentRead(DocumentBase, ORMModel):
    id: int
    application_id: Optional[int] = None
    student_id: Optional[int] = None
    uploaded_at: Optional[datetime] = None


class OCRResult(BaseModel):
    document_id: int
    ocr_status: str
    verification_status: str
    extracted_text: str
    matched_fields: list[str] = Field(default_factory=list)
    mismatched_fields: list[str] = Field(default_factory=list)
    remarks: str
    processed_at: datetime | None = None


class DocumentProcessResult(OCRResult):
    processing_status: str
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    processing_error: str | None = None


class ApplicationBase(BaseModel):
    course: str
    status: str = "draft"
    submitted_at: Optional[datetime] = None
    remarks: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    student_id: int


class ApplicationUpdate(BaseModel):
    course: str | None = None
    status: str | None = None
    submitted_at: Optional[datetime] = None
    remarks: Optional[str] = None


class ApplicationRead(ApplicationBase, ORMModel):
    id: int
    application_number: str
    student_id: int
    created_at: datetime
    student: StudentRead | None = None
    documents: list[DocumentRead] = Field(default_factory=list)


class ScholarshipBase(BaseModel):
    name: str = ""
    scheme_name: str | None = None
    provider: str
    amount: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    eligibility_summary: Optional[str] = None
    is_active: bool = True
    eligibility_rules: dict[str, object] = Field(default_factory=dict)
    required_documents: list[str] = Field(default_factory=list)
    application_start_date: Optional[datetime] = None
    application_end_date: Optional[datetime] = None
    amount_or_benefit: Optional[str] = None
    status: str = "active"

    @field_validator("eligibility_rules", mode="before")
    @classmethod
    def decode_eligibility_rules(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return value

    @field_validator("required_documents", mode="before")
    @classmethod
    def decode_required_documents(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []
        return value


class ScholarshipCreate(ScholarshipBase):
    pass


class ScholarshipUpdate(BaseModel):
    name: str | None = None
    scheme_name: str | None = None
    description: str | None = None
    provider: str | None = None
    eligibility_summary: str | None = None
    eligibility_rules: dict[str, object] | None = None
    required_documents: list[str] | None = None
    application_start_date: Optional[datetime] = None
    application_end_date: Optional[datetime] = None
    amount_or_benefit: str | None = None
    amount: str | None = None
    deadline: Optional[datetime] = None
    status: str | None = None
    is_active: bool | None = None


class ScholarshipRead(ScholarshipBase, ORMModel):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ScholarshipApplicationCreate(BaseModel):
    scholarship_id: int
    student_id: int
    eligibility_status: str = "Requires Verification"
    verification_status: str = "pending"
    application_status: str = "Applied"
    remarks: str | None = None


class ScholarshipApplicationRead(ORMModel):
    id: int
    scholarship_id: int
    student_id: int
    eligibility_status: str
    document_status: str
    verification_status: str
    application_status: str
    submitted_at: Optional[datetime] = None
    remarks: str | None = None
    applied_at: datetime | None = None
    updated_at: datetime | None = None


class ScholarshipApplicationUpdate(BaseModel):
    eligibility_status: str | None = None
    verification_status: str | None = None
    application_status: str | None = None
    remarks: str | None = None


class EligibilityResult(BaseModel):
    student_id: int
    scholarship_id: int
    eligibility_status: str
    matched_rules: list[str] = Field(default_factory=list)
    unmatched_rules: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    available_documents: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    remarks: str


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str = "system"
    read: bool = False


class NotificationCreate(NotificationBase):
    student_id: int


class NotificationRead(NotificationBase, ORMModel):
    id: int
    student_id: int
    created_at: datetime
