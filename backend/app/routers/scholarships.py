from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..services.scholarship_eligibility import evaluate_eligibility
from .auth import require_admin, require_student

router = APIRouter(prefix="/scholarships", tags=["scholarships"])
student_router = APIRouter(prefix="/students", tags=["student scholarships"])
application_router = APIRouter(prefix="/scholarship-applications", tags=["scholarship applications"])


@router.get("", response_model=list[schemas.ScholarshipRead])
def list_scholarships(active_only: bool = False, db: Session = Depends(get_db)):
    return crud.list_scholarships(db, active_only)


@router.post("", response_model=schemas.ScholarshipRead, status_code=status.HTTP_201_CREATED)
def create_scholarship(payload: schemas.ScholarshipCreate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return crud.create_scholarship(db, payload)


@router.get("/applications", response_model=list[schemas.ScholarshipApplicationRead])
def list_scholarship_applications(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return crud.list_scholarship_applications(db)


@router.get("/{scholarship_id}", response_model=schemas.ScholarshipRead)
def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    scholarship = crud.get_scholarship(db, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship


@router.patch("/{scholarship_id}", response_model=schemas.ScholarshipRead)
def update_scholarship(scholarship_id: int, payload: schemas.ScholarshipUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    scholarship = crud.get_scholarship(db, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return crud.update_scholarship(db, scholarship, payload)


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scholarship(scholarship_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    scholarship = crud.get_scholarship(db, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    crud.delete_scholarship(db, scholarship)


@router.get("/{scholarship_id}/eligibility/{student_id}", response_model=schemas.EligibilityResult)
def scholarship_eligibility(scholarship_id: int, student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Student ownership check failed")
    scholarship = crud.get_scholarship(db, scholarship_id)
    student = crud.get_student(db, student_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return evaluate_eligibility(db, student, scholarship)


@student_router.get("/{student_id}/scholarships", response_model=list[schemas.ScholarshipApplicationRead])
def student_scholarship_applications(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Student ownership check failed")
    if crud.get_student(db, student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return [item for item in crud.list_scholarship_applications(db) if item.student_id == student_id]


@student_router.get("/{student_id}/scholarships/eligibility", response_model=list[schemas.EligibilityResult])
def student_scholarship_eligibility(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Student ownership check failed")
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return [evaluate_eligibility(db, student, scholarship) for scholarship in crud.list_scholarships(db, active_only=True)]


@application_router.post("", response_model=schemas.ScholarshipApplicationRead, status_code=status.HTTP_201_CREATED)
def create_scholarship_application(payload: schemas.ScholarshipApplicationCreate, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if payload.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Student ownership check failed")
    student = crud.get_student(db, payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    scholarship = crud.get_scholarship(db, payload.scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    existing = crud.existing_scholarship_application(db, payload.student_id, payload.scholarship_id)
    if existing and existing.application_status not in {"Rejected", "Closed"}:
        raise HTTPException(status_code=409, detail="Student already has an active application for this scholarship")
    screening = evaluate_eligibility(db, student, scholarship)
    payload.eligibility_status = screening.eligibility_status
    payload.remarks = screening.remarks
    try:
        application = crud.create_scholarship_application(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Student already has an active application for this scholarship")
    crud.create_notification(db, schemas.NotificationCreate(
        student_id=payload.student_id,
        title="Scholarship application submitted",
        message=f"Your application for {scholarship.name} was submitted for screening.",
        notification_type="scholarship",
    ))
    return application


@application_router.get("", response_model=list[schemas.ScholarshipApplicationRead])
def list_all_scholarship_applications(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return crud.list_scholarship_applications(db)


@application_router.get("/{application_id}", response_model=schemas.ScholarshipApplicationRead)
def get_scholarship_application(application_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    application = crud.get_scholarship_application(db, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Scholarship application not found")
    return application


@application_router.patch("/{application_id}", response_model=schemas.ScholarshipApplicationRead)
def update_scholarship_application(application_id: int, payload: schemas.ScholarshipApplicationUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    application = crud.get_scholarship_application(db, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Scholarship application not found")
    previous_status = application.application_status
    updated = crud.update_scholarship_application(db, application, payload)
    if payload.application_status and payload.application_status != previous_status:
        crud.create_notification(db, schemas.NotificationCreate(
            student_id=updated.student_id,
            title="Scholarship application status changed",
            message=f"Your scholarship application is now {updated.application_status}.",
            notification_type="scholarship",
        ))
    return updated
