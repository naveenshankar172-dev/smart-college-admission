from datetime import datetime
import hashlib
import json
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas

ModelT = TypeVar("ModelT")


def list_students(db: Session) -> list[models.Student]:
    return list(db.scalars(select(models.Student).order_by(models.Student.id.desc())).all())


def create_student(db: Session, payload: schemas.StudentCreate) -> models.Student:
    values = payload.model_dump(exclude={"password"})
    password = payload.password
    if password:
        values["password_hash"] = hashlib.sha256(password.encode("utf-8")).hexdigest()
    student = models.Student(**values)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_student(db: Session, student_id: int) -> models.Student | None:
    return db.get(models.Student, student_id)


def update_student(db: Session, student: models.Student, payload: schemas.StudentUpdate) -> models.Student:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


def list_applications(db: Session) -> list[models.Application]:
    return list(db.scalars(select(models.Application).order_by(models.Application.created_at.desc())).all())


def get_application(db: Session, application_id: int) -> models.Application | None:
    return db.get(models.Application, application_id)


def create_application(db: Session, payload: schemas.ApplicationCreate) -> models.Application:
    application = models.Application(**payload.model_dump(), application_number=f"ADM{datetime.utcnow():%Y%m%d%H%M%S%f}"[:16])
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def update_application(db: Session, application: models.Application, payload: schemas.ApplicationBase) -> models.Application:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, key, value)
    db.commit()
    db.refresh(application)
    return application


def list_documents(db: Session, application_id: int | None = None, student_id: int | None = None) -> list[models.Document]:
    query = select(models.Document).order_by(models.Document.id.desc())
    if application_id is not None:
        query = query.where(models.Document.application_id == application_id)
    if student_id is not None:
        query = query.where(models.Document.student_id == student_id)
    return list(db.scalars(query).all())


def create_document(db: Session, payload: schemas.DocumentCreate) -> models.Document:
    document = models.Document(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document(db: Session, document: models.Document, payload: schemas.DocumentUpdate) -> models.Document:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(document, key, value)
    if "verification_status" in payload.model_dump(exclude_unset=True):
        document.status = payload.verification_status or document.status
    elif "status" in payload.model_dump(exclude_unset=True):
        document.verification_status = payload.status or document.verification_status
    db.commit()
    db.refresh(document)
    return document


def list_scholarships(db: Session, active_only: bool = False) -> list[models.Scholarship]:
    query = select(models.Scholarship).order_by(models.Scholarship.id.desc())
    if active_only:
        query = query.where(models.Scholarship.is_active.is_(True))
    return list(db.scalars(query).all())


def create_scholarship(db: Session, payload: schemas.ScholarshipCreate) -> models.Scholarship:
    values = payload.model_dump()
    values["name"] = values.get("scheme_name") or values.get("name") or "Sample Scholarship"
    values["scheme_name"] = values.get("scheme_name") or values["name"]
    values["eligibility_rules"] = json.dumps(values.get("eligibility_rules") or {})
    values["required_documents"] = json.dumps(values.get("required_documents") or [])
    values.pop("status", None)
    values["is_active"] = values.get("is_active", True)
    scholarship = models.Scholarship(**values)
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    return scholarship


def get_scholarship(db: Session, scholarship_id: int) -> models.Scholarship | None:
    return db.get(models.Scholarship, scholarship_id)


def update_scholarship(db: Session, scholarship: models.Scholarship, payload: schemas.ScholarshipUpdate) -> models.Scholarship:
    values = payload.model_dump(exclude_unset=True)
    if "eligibility_rules" in values:
        values["eligibility_rules"] = json.dumps(values["eligibility_rules"] or {})
    if "required_documents" in values:
        values["required_documents"] = json.dumps(values["required_documents"] or [])
    for key, value in values.items():
        if key in {"status", "scheme_name"}:
            if key == "status":
                scholarship.status = value
                scholarship.is_active = value == "active"
            else:
                scholarship.scheme_name = value
                scholarship.name = value or scholarship.name
        elif hasattr(scholarship, key):
            setattr(scholarship, key, value)
    db.commit()
    db.refresh(scholarship)
    return scholarship


def delete_scholarship(db: Session, scholarship: models.Scholarship) -> None:
    db.delete(scholarship)
    db.commit()


def create_scholarship_application(db: Session, payload: schemas.ScholarshipApplicationCreate) -> models.ScholarshipApplication:
    application = models.ScholarshipApplication(**payload.model_dump(), submitted_at=datetime.utcnow(), applied_at=datetime.utcnow())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_scholarship_application(db: Session, application_id: int) -> models.ScholarshipApplication | None:
    return db.get(models.ScholarshipApplication, application_id)


def update_scholarship_application(db: Session, application: models.ScholarshipApplication, payload: schemas.ScholarshipApplicationUpdate) -> models.ScholarshipApplication:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, key, value)
    db.commit()
    db.refresh(application)
    return application


def existing_scholarship_application(db: Session, student_id: int, scholarship_id: int) -> models.ScholarshipApplication | None:
    return db.scalar(select(models.ScholarshipApplication).where(models.ScholarshipApplication.student_id == student_id, models.ScholarshipApplication.scholarship_id == scholarship_id).order_by(models.ScholarshipApplication.id.desc()))


def list_scholarship_applications(db: Session) -> list[models.ScholarshipApplication]:
    return list(db.scalars(select(models.ScholarshipApplication).order_by(models.ScholarshipApplication.id.desc())).all())


def create_notification(db: Session, payload: schemas.NotificationCreate) -> models.Notification:
    notification = models.Notification(**payload.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, student_id: int | None = None) -> list[models.Notification]:
    query = select(models.Notification).order_by(models.Notification.created_at.desc())
    if student_id is not None:
        query = query.where(models.Notification.student_id == student_id)
    return list(db.scalars(query).all())


def get_notification(db: Session, notification_id: int) -> models.Notification | None:
    return db.get(models.Notification, notification_id)


def mark_notification_read(db: Session, notification: models.Notification) -> models.Notification:
    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification
