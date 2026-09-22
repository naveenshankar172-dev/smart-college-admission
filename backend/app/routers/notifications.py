from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from .auth import require_student

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.patch("/{notification_id}/read", response_model=schemas.NotificationRead)
def mark_read(notification_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    notification = crud.get_notification(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notification.student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Notification ownership check failed")
    return crud.mark_notification_read(db, notification)


@router.patch("/student/{student_id}/read-all", response_model=list[schemas.NotificationRead])
def mark_all_read(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    notifications = crud.list_notifications(db, student_id)
    for notification in notifications:
        notification.read = True
    db.commit()
    return notifications