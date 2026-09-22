from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..services.document_verification import verify_document
from ..services.ocr_service import OCRProcessingError, extract_text
from .auth import require_admin, require_admin_or_automation, require_student, require_student_admin_or_automation, require_student_or_admin

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_TYPES = {"application/pdf": ".pdf", "image/jpeg": ".jpg", "image/png": ".png"}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[schemas.DocumentRead])
def list_documents(application_id: int | None = None, student_id: int | None = None, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return crud.list_documents(db, application_id, student_id)


@router.post("", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(payload: schemas.DocumentCreate, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if payload.student_id is not None and payload.student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    if payload.application_id is not None:
        application = db.get(models.Application, payload.application_id)
        if application is None or application.student_id != current_student.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Application ownership check failed")
        payload.student_id = current_student.id
    elif payload.student_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student or application ownership is required")
    return crud.create_document(db, payload)


@router.post("/upload", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(student_id: int = Form(...), document_type: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if not document_type.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Document type is required")
    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()
    if file.content_type not in ALLOWED_TYPES or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF, JPG, JPEG, and PNG files are supported")
    application = db.scalar(select(models.Application).where(models.Application.student_id == student_id).order_by(models.Application.id.desc()))
    if application is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submit an admission application before uploading documents")
    existing = db.scalar(select(models.Document).where(models.Document.student_id == student_id, models.Document.document_type == document_type, models.Document.file_path.is_not(None)).order_by(models.Document.id.desc()))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A document of this type already exists. Delete it before uploading a replacement.")
    stored_name = f"{uuid4().hex}{ALLOWED_TYPES[file.content_type]}"
    student_directory = UPLOAD_ROOT / str(student_id)
    stored_path = student_directory / stored_name
    try:
        student_directory.mkdir(parents=True, exist_ok=True)
        file_size = 0
        with stored_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds the 5 MB limit")
                destination.write(chunk)
    except HTTPException:
        stored_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to store the uploaded file") from exc
    document = models.Document(application_id=application.id, student_id=student_id, name=document_type, document_type=document_type, file_name=original_name, original_filename=original_name, stored_filename=stored_name, file_path=str(stored_path.relative_to(UPLOAD_ROOT.parent)), file_type=file.content_type, file_size=file_size, upload_date=datetime.utcnow(), uploaded_at=datetime.utcnow(), status="pending", verification_status="pending")
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save document metadata")
    crud.create_notification(db, schemas.NotificationCreate(student_id=student_id, title="Document uploaded", message=f"Your {document_type} was uploaded and is pending processing.", notification_type="document"))
    return document


@router.get("/student/{student_id}", response_model=list[schemas.DocumentRead])
def list_student_documents(student_id: int, db: Session = Depends(get_db), current_student=Depends(require_student)):
    if student_id != current_student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student ownership check failed")
    if db.get(models.Student, student_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return crud.list_documents(db, student_id=student_id)


@router.get("/pending", response_model=list[schemas.DocumentRead])
def pending_documents(db: Session = Depends(get_db), _automation=Depends(require_admin_or_automation)):
    return list(db.scalars(select(models.Document).where(models.Document.processing_status == "pending", models.Document.file_path.is_not(None)).order_by(models.Document.id.asc())).all())


@router.get("/{document_id}", response_model=schemas.DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db), actor=Depends(require_student_or_admin)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    _ensure_document_access(document, actor)
    return document


def _stored_path(document: models.Document) -> Path:
    if not document.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    candidate = (Path(__file__).resolve().parents[2] / document.file_path).resolve()
    if UPLOAD_ROOT.resolve() not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return candidate


def _document_student(document: models.Document, db: Session) -> models.Student:
    student = document.student or (document.application.student if document.application else None)
    if student is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document is not linked to a student")
    return student


def _ensure_document_access(document: models.Document, actor: dict) -> None:
    if actor["kind"] in {"admin", "automation"}:
        return
    if document.student_id != actor["student"].id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Document ownership check failed")


def _verification_result(document: models.Document, processed_at: datetime | None = None) -> schemas.OCRResult:
    return schemas.OCRResult(document_id=document.id, ocr_status=document.ocr_status, verification_status=document.verification_status, extracted_text=document.extracted_text or "", matched_fields=json.loads(document.matched_fields or "[]"), mismatched_fields=json.loads(document.mismatched_fields or "[]"), remarks=document.remarks or "", processed_at=processed_at or document.ocr_processed_at)


def _process_result(document: models.Document) -> schemas.DocumentProcessResult:
    result = _verification_result(document)
    return schemas.DocumentProcessResult(**result.model_dump(), processing_status=document.processing_status, processing_started_at=document.processing_started_at, processing_completed_at=document.processing_completed_at, processing_error=document.processing_error)


@router.post("/{document_id}/process", response_model=schemas.DocumentProcessResult)
def process_document(document_id: int, db: Session = Depends(get_db), _actor=Depends(require_admin_or_automation)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.processing_status == "processing":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document is already being processed")
    if document.processing_status == "completed":
        return _process_result(document)
    started = datetime.utcnow()
    document.processing_status = "processing"
    document.processing_started_at = started
    document.processing_error = None
    db.commit()
    try:
        path = _stored_path(document)
        document.ocr_status = "processing"
        db.commit()
        text = extract_text(path, document.file_type)
        document.extracted_text = text
        document.ocr_status = "completed"
        document.ocr_processed_at = datetime.utcnow()
        student = _document_student(document, db)
        result = verify_document(document, student, text)
        document.verification_status = result.verification_status
        document.status = result.verification_status
        document.matched_fields = json.dumps(result.matched_fields)
        document.mismatched_fields = json.dumps(result.mismatched_fields)
        document.remarks = result.remarks
        document.processing_status = "completed"
        document.processing_completed_at = datetime.utcnow()
        db.commit()
        crud.create_notification(db, schemas.NotificationCreate(student_id=student.id, title="Document verification completed", message=f"{document.document_type or document.name} processing completed with status {document.verification_status}.", notification_type="document"))
        db.refresh(document)
        return _process_result(document)
    except OCRProcessingError as exc:
        document.ocr_status = "failed"
        document.verification_status = "failed"
        document.processing_status = "failed"
        document.processing_error = str(exc)
        document.remarks = str(exc)
        document.ocr_processed_at = datetime.utcnow()
        db.commit()
        crud.create_notification(db, schemas.NotificationCreate(student_id=document.student_id or 0, title="Document processing failed", message=f"{document.document_type or document.name} requires attention: {exc}", notification_type="document")) if document.student_id else None
        db.refresh(document)
        return _process_result(document)
    except HTTPException:
        document.processing_status = "failed"
        document.processing_error = "Stored document file is unavailable"
        db.commit()
        raise
    except Exception as exc:
        document.processing_status = "failed"
        document.processing_error = "Document processing failed"
        document.remarks = "Document processing failed"
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Document processing failed") from exc


@router.post("/{document_id}/ocr", response_model=schemas.OCRResult)
def process_document_ocr(document_id: int, db: Session = Depends(get_db), actor=Depends(require_student_or_admin)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    _ensure_document_access(document, actor)
    path = _stored_path(document)
    document.ocr_status = "processing"
    db.commit()
    try:
        text = extract_text(path, document.file_type)
        document.extracted_text = text
        document.ocr_status = "completed"
        document.ocr_processed_at = datetime.utcnow()
        document.remarks = None
        db.commit()
        db.refresh(document)
    except OCRProcessingError as exc:
        document.ocr_status = "failed"
        document.ocr_processed_at = datetime.utcnow()
        document.remarks = str(exc)
        document.verification_status = "failed"
        db.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return _verification_result(document)


@router.post("/{document_id}/verify", response_model=schemas.OCRResult)
def verify_document_content(document_id: int, db: Session = Depends(get_db), actor=Depends(require_student_or_admin)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    _ensure_document_access(document, actor)
    if not document.extracted_text:
        process_document_ocr(document_id, db)
        db.refresh(document)
    student = _document_student(document, db)
    result = verify_document(document, student, document.extracted_text or "")
    document.verification_status = result.verification_status
    document.status = result.verification_status
    document.matched_fields = json.dumps(result.matched_fields)
    document.mismatched_fields = json.dumps(result.mismatched_fields)
    document.remarks = result.remarks
    db.commit()
    db.refresh(document)
    return _verification_result(document)


@router.get("/{document_id}/verification", response_model=schemas.OCRResult)
def get_document_verification(document_id: int, db: Session = Depends(get_db), actor=Depends(require_student_admin_or_automation)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    _ensure_document_access(document, actor)
    return _verification_result(document)


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db), actor=Depends(require_student_or_admin)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    _ensure_document_access(document, actor)
    candidate = _stored_path(document)
    return FileResponse(candidate, media_type=document.file_type or "application/octet-stream", filename=document.original_filename or document.file_name or document.stored_filename)


@router.patch("/{document_id}", response_model=schemas.DocumentRead)
def update_document(document_id: int, payload: schemas.DocumentUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return crud.update_document(db, document, payload)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db), actor=Depends(require_student_or_admin)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    _ensure_document_access(document, actor)
    if document.file_path:
        candidate = (Path(__file__).resolve().parents[2] / document.file_path).resolve()
        if UPLOAD_ROOT.resolve() in candidate.parents:
            candidate.unlink(missing_ok=True)
    db.delete(document)
    db.commit()
