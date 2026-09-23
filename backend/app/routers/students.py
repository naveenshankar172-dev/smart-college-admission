from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..models import Student
from .auth import require_admin, require_development_mode, require_student

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[schemas.StudentRead])
def list_students(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return crud.list_students(db)


@router.post("", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db), _development=Depends(require_development_mode)):
    email = str(payload.email).strip().lower()
    if db.query(Student).filter(Student.email.ilike(email)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A student already exists for this email.")
    return crud.create_student(db, payload)


@router.get("/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return crud.update_student(db, student, payload)


@router.get("/{student_id}/notifications", response_model=list[schemas.NotificationRead])
def list_notifications(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    return crud.list_notifications(db, student_id)
