# SMART COLLEGE ADMISSION & DOCUMENT VERIFICATION SYSTEM

An integrated admission, document verification, scholarship screening and RPA automation platform.

## Project Overview

This repository contains a functional full-stack academic prototype for managing student admission applications, document uploads, OCR-assisted content checks, configurable scholarship screening, administrator review and notifications.

The active system uses a React and TypeScript frontend, a FastAPI REST API, SQLite persistence, Firebase Authentication/Google Sign-In support, local OCR services, and an API contract that can be orchestrated by UiPath.

Document verification compares selected information extracted from a document with the student record. It does **not** independently prove official authenticity, government validity, fraud status or tamper resistance.

## Implemented Features

- Firebase bearer-token verification and Google popup sign-in support.
- Firebase Authentication and Google Sign-In are the primary student authentication path. Development login is explicitly opt-in through `AUTH_MODE=development` and `VITE_AUTH_MODE=development`.
- First-time Firebase onboarding and returning-student session lookup.
- Student profiles, admission applications, status changes and remarks.
- PDF/JPG/JPEG/PNG upload handling with a 5 MB limit and document metadata.
- PDF text extraction with `pypdf`; scanned PDF/image OCR with PyMuPDF, Pillow, pytesseract and Tesseract.
- Deterministic name/date-of-birth consistency checks with `verified`, `manual_review` and `failed` outcomes.
- Configurable scholarship rules for minimum percentage, course matching, income information and required documents.
- Scholarship application and admin review flows, with duplicate protection in the main application path.
- Notifications for admission, document and scholarship events, including read and read-all actions.
- Admin dashboard statistics, application review, document review, scholarship CRUD and scholarship application review.
- UiPath-facing pending/process/OCR/verification endpoints.

## Architecture

```text
Student browser
  -> React + TypeScript + Tailwind frontend
  -> Firebase Authentication / Google Sign-In (when Firebase mode is enabled)
  -> FastAPI REST API
  -> SQLite database and local upload storage

UiPath -> pending documents -> FastAPI process endpoint -> OCR -> consistency verification -> SQLite
Administrator -> protected admin API/UI -> applications, documents, scholarships and reports
```

This is a modular full-stack application with one FastAPI API layer, not a microservices or Kubernetes deployment.

## Technology Stack

| Area | Technologies actually present |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite by default |
| Authentication | Firebase Authentication, Google Sign-In, Firebase Admin SDK |
| Automation contract | UiPath through REST endpoints |
| OCR and extraction | Tesseract, pytesseract, PyMuPDF, pypdf, Pillow |
| API | REST/JSON, multipart upload |

## Project Structure

```text
src/                         React frontend
  pages/                     Student, admin and public pages
  services/                  API, Firebase and session adapters
  layouts/                   Public and portal layouts
backend/app/                 FastAPI application
  routers/                   API route modules
  services/                  OCR, verification and scholarship rules
docs/                        Report, diagrams and generated artifacts
backend/uploads/             Local uploaded-document storage
```

## Prerequisites

- Node.js and npm.
- Python with the project virtual environment.
- Tesseract installed and available through `TESSERACT_CMD` for image/scanned-PDF OCR.
- Firebase project configuration only when Firebase mode is enabled.
- Optional UiPath installation for external queue orchestration.

## Installation and Configuration

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
npm install
```

Create a root `.env` using placeholders, never real credentials in source control:

```env
AUTH_MODE=firebase
VITE_AUTH_MODE=firebase
DATABASE_URL=sqlite:///./backend/admissions.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
FIREBASE_SERVICE_ACCOUNT_FILE=./firebase-service-account.json
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
UIPATH_API_KEY=replace-with-a-secret-for-UiPath-automation
```

Firebase web configuration belongs in the frontend environment according to `src/services/firebase.ts`. Firebase Admin service-account credentials remain server-side, must be kept out of README files and screenshots, and should remain gitignored.

## Running the Project

Terminal 1:

```powershell
npm run dev -- --host 127.0.0.1
```

Terminal 2:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Frontend: `http://127.0.0.1:5173/`  
API: `http://127.0.0.1:8000/`  
Swagger: `http://127.0.0.1:8000/docs`  
Health: `GET /api/health`

## UiPath Contract

The UiPath workflow polls `GET /api/documents/pending`, extracts document IDs, calls `POST /api/documents/{id}/process`, optionally calls OCR and verification endpoints separately, retrieves the result with `GET /api/documents/{id}/verification`, and logs structured status/errors. These automation routes require the configured `X-UiPath-Key` or an authenticated admin bearer token. OCR itself is delegated to FastAPI services.

## Security Notes

Firebase Admin verification, ownership checks and admin dependencies are implemented for protected routes. Development authentication remains available only as an explicit local-debug configuration. UiPath processing routes require the configured automation key or an authenticated admin bearer token. Do not expose Firebase service-account JSON, tokens or personal credentials.

## Testing Status

The repository contains no pytest, Vitest, Playwright or FastAPI `TestClient` suite. The frontend and backend were manually reachability-checked during this documentation pass: Vite returned HTTP 200, and `GET /api/health` returned `{"status":"ok"}`. Firebase production mode, Tesseract OCR, scanned PDFs, UiPath execution and route authorization remain not tested in this pass.

## Limitations and Future Scope

Current limitations include local SQLite and upload storage, OCR sensitivity to document quality, manual review for mismatches, lack of official authenticity determination, no email delivery or audit history, and no background RPA worker. Development authentication is retained only for explicitly configured local debugging.

Future scope: production-grade authentication hardening, PostgreSQL, cloud storage, stronger authenticity analysis, improved OCR, exportable analytics, configurable admin rule management, audit logging, institution-wide deployment, additional identity providers, mobile clients and scalable RPA orchestration.

## Generated Documentation

Run the generator from the repository root:

```powershell
.\.venv\Scripts\python.exe docs\generate_artifacts.py
```

It creates `docs/artifacts/PROJECT_REPORT.docx`, `PROJECT_PRESENTATION.pptx`, and readable PNG architecture, ER, DFD, use-case, activity and sequence diagrams. The source report is [PROJECT_REPORT.md](PROJECT_REPORT.md). The Phase 9 audit is [PHASE_9_FINAL_AUDIT.md](PHASE_9_FINAL_AUDIT.md).
