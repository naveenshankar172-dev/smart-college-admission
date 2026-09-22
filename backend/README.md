# Smart College Admission API

Initial FastAPI + SQLite backend for the AdmitFlow frontend.

## Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

## Run

```powershell
uvicorn app.main:app --app-dir backend --reload
```

The API is available at `http://127.0.0.1:8000`.

- Health: `GET /api/health`
- Swagger UI: `http://127.0.0.1:8000/docs`

## UiPath processing contract

UiPath can poll and process documents with the configured automation key or an authenticated admin bearer token:

1. `GET /api/documents/pending` returns uploaded documents whose `processing_status` is `pending`.
2. `POST /api/documents/{document_id}/process` runs the complete OCR and deterministic verification workflow. It returns `processing_status`, `ocr_status`, `verification_status`, extracted text, matched/mismatched fields, remarks, timestamps, and errors.
3. `POST /api/documents/{document_id}/ocr` runs OCR only.
4. `POST /api/documents/{document_id}/verify` runs deterministic content verification using stored OCR text.
5. `GET /api/documents/{document_id}/verification` retrieves the complete verification result.

Processing is guarded against duplicate work: a document already in `processing` returns HTTP `409`, and a `completed` document returns its stored result without rerunning. A failed process returns a structured `failed` result so UiPath can log or retry it.

SQLite is created at `backend/admissions.db` by default. Set `DATABASE_URL` to use another SQLAlchemy database URL. Set `CORS_ORIGINS` to a comma-separated list when the frontend origin changes.

Image OCR uses the local Tesseract executable. Set `TESSERACT_CMD` to its full path, for example `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`. PDF text extraction does not require Tesseract. If Tesseract is unavailable, image OCR returns a clear configuration error.

Firebase Authentication/Google Sign-In is the primary student authentication mechanism. Development login is available only when `AUTH_MODE=development` and the frontend explicitly uses `VITE_AUTH_MODE=development`. File persistence, OCR, RPA orchestration, and configurable scholarship eligibility are implemented in the current prototype. Document verification checks content consistency and does not independently prove official authenticity.
