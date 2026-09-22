import hmac
import os
from fastapi import APIRouter, Depends, Header, HTTPException
import hashlib
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..models import Student
from ..firebase_auth import get_firebase_claims

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_mode() -> str:
    return os.getenv("AUTH_MODE", "firebase").lower()


def _admin_uids() -> set[str]:
    return {value.strip() for value in os.getenv("FIREBASE_ADMIN_UIDS", "").split(",") if value.strip()}


def require_development_mode() -> None:
    if _auth_mode() != "development":
        raise HTTPException(status_code=403, detail="Development authentication is disabled")


def require_student(x_student_id: int | None = Header(default=None), authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> Student:
    if _auth_mode() == "firebase":
        claims = get_firebase_claims(authorization)
        uid = str(claims.get("uid", ""))
        student = db.query(Student).filter(Student.firebase_uid == uid).first()
        if student is None:
            raise HTTPException(status_code=403, detail="Complete student onboarding before accessing the portal")
        return student
    if _auth_mode() != "development":
        raise HTTPException(status_code=503, detail="Unsupported authentication mode")
    if x_student_id is None:
        raise HTTPException(status_code=401, detail="Student session required")
    student = db.get(Student, x_student_id)
    if student is None:
        raise HTTPException(status_code=401, detail="Student session is invalid")
    return student


def require_admin(authorization: str | None = Header(default=None)) -> dict:
    if _auth_mode() == "development":
        return {"uid": "development-admin", "role": "admin"}
    if _auth_mode() != "firebase":
        raise HTTPException(status_code=503, detail="Unsupported authentication mode")
    claims = get_firebase_claims(authorization)
    if str(claims.get("uid", "")) not in _admin_uids():
        raise HTTPException(status_code=403, detail="Admin authorization required")
    return claims


def require_student_or_admin(x_student_id: int | None = Header(default=None), authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
    if _auth_mode() == "firebase":
        claims = get_firebase_claims(authorization)
        uid = str(claims.get("uid", ""))
        if uid in _admin_uids():
            return {"kind": "admin", "claims": claims}
        student = db.query(Student).filter(Student.firebase_uid == uid).first()
        if student is None:
            raise HTTPException(status_code=403, detail="Complete student onboarding before accessing the portal")
        return {"kind": "student", "student": student}
    if _auth_mode() != "development":
        raise HTTPException(status_code=503, detail="Unsupported authentication mode")
    if x_student_id is None:
        raise HTTPException(status_code=401, detail="Student session required")
    student = db.get(Student, x_student_id)
    if student is None:
        raise HTTPException(status_code=401, detail="Student session is invalid")
    return {"kind": "student", "student": student}


def require_admin_or_automation(authorization: str | None = Header(default=None), x_uipath_key: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
    automation_key = os.getenv("UIPATH_API_KEY", "").strip()
    if automation_key and x_uipath_key and hmac.compare_digest(x_uipath_key, automation_key):
        return {"kind": "automation"}
    return {"kind": "admin", "claims": require_admin(authorization)}


def require_student_admin_or_automation(x_student_id: int | None = Header(default=None), authorization: str | None = Header(default=None), x_uipath_key: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
    automation_key = os.getenv("UIPATH_API_KEY", "").strip()
    if automation_key and x_uipath_key and hmac.compare_digest(x_uipath_key, automation_key):
        return {"kind": "automation"}
    return require_student_or_admin(x_student_id, authorization, db)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.get("/firebase/session")
def firebase_session(claims: dict = Depends(get_firebase_claims), db: Session = Depends(get_db)):
    uid = str(claims.get("uid", ""))
    student = db.query(Student).filter(Student.firebase_uid == uid).first()
    allowed_admins = {value.strip() for value in os.getenv("FIREBASE_ADMIN_UIDS", "").split(",") if value.strip()}
    return {"registered": student is not None, "role": "admin" if uid in allowed_admins else "student", "firebase_uid": uid, "email": claims.get("email", ""), "name": claims.get("name", ""), "student_id": student.id if student else None}


@router.post("/firebase/onboard", response_model=schemas.StudentRead, status_code=201)
def firebase_onboard(payload: schemas.FirebaseOnboarding, claims: dict = Depends(get_firebase_claims), db: Session = Depends(get_db)):
    uid = str(claims.get("uid", ""))
    existing = db.query(Student).filter(Student.firebase_uid == uid).first()
    if existing is not None:
        return existing
    email = str(claims.get("email", "")).lower()
    if not email:
        raise HTTPException(status_code=400, detail="Firebase account does not contain an email")
    if db.query(Student).filter(Student.email == email).first() is not None:
        raise HTTPException(status_code=409, detail="A student already exists for this email")
    student = Student(name=payload.name, email=email, phone=payload.phone, course=payload.course, academic_year=payload.academic_year, firebase_uid=uid)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.post("/login", dependencies=[Depends(require_development_mode)])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    student = next((item for item in crud.list_students(db) if item.email.lower() == str(payload.email).lower()), None)
    if student is None:
        if "admin" in str(payload.email).lower():
            return {"id": "admin", "name": "Admissions team", "email": str(payload.email), "role": "admin"}
        raise HTTPException(status_code=401, detail="No student account exists for this email.")
    if student.password_hash and student.password_hash != hashlib.sha256(payload.password.encode("utf-8")).hexdigest():
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return {"id": str(student.id), "name": student.name, "email": student.email, "phone": student.phone or "", "course": student.course or "", "academic_year": student.academic_year or "", "role": "student"}
