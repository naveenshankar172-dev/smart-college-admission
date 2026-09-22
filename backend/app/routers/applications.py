from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from .auth import require_admin, require_student

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/statistics")
def application_statistics(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    students = db.scalar(select(func.count(models.Student.id)))
    applications = db.scalar(select(func.count(models.Application.id)))
    pending_documents = db.scalar(select(func.count(models.Document.id)).where(models.Document.processing_status.in_(["pending", "processing"])))
    manual_documents = db.scalar(select(func.count(models.Document.id)).where(models.Document.verification_status == "manual-review"))
    scholarship_applications = db.scalar(select(func.count(models.ScholarshipApplication.id)))
    under_review = db.scalar(select(func.count(models.ScholarshipApplication.id)).where(models.ScholarshipApplication.application_status == "Under Review"))
    approved = db.scalar(select(func.count(models.ScholarshipApplication.id)).where(models.ScholarshipApplication.application_status == "Approved"))
    rejected = db.scalar(select(func.count(models.ScholarshipApplication.id)).where(models.ScholarshipApplication.application_status == "Rejected"))
    return {"total_students": students or 0, "total_applications": applications or 0, "pending_documents": pending_documents or 0, "manual_documents": manual_documents or 0, "scholarship_applications": scholarship_applications or 0, "under_review": under_review or 0, "approved": approved or 0, "rejected": rejected or 0}


@router.get("", response_model=list[schemas.ApplicationRead])
def list_applications(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return crud.list_applications(db)
    
@router.get("/student/{student_id}", response_model=list[schemas.ApplicationRead])
def list_student_applications(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Student ownership check failed")
    return [item for item in crud.list_applications(db) if item.student_id == student_id]
@router.get("/{application_id}", response_model=schemas.ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    application = crud.get_application(db, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.post("", response_model=schemas.ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if payload.student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    if crud.get_student(db, payload.student_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    application = crud.create_application(db, payload)
    crud.create_notification(db, schemas.NotificationCreate(student_id=payload.student_id, title="Admission application submitted", message=f"Your admission application {application.application_number} was submitted.", notification_type="admission"))
    return application


@router.patch("/{application_id}", response_model=schemas.ApplicationRead)
def update_application(application_id: int, payload: schemas.ApplicationUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    application = crud.get_application(db, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    previous_status = application.status
    updated = crud.update_application(db, application, payload)
    if payload.status and payload.status != previous_status:
        crud.create_notification(db, schemas.NotificationCreate(student_id=updated.student_id, title="Admission application status changed", message=f"Your admission application is now {updated.status}.", notification_type="admission"))
    return updated
