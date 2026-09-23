# SMART COLLEGE ADMISSION & DOCUMENT VERIFICATION SYSTEM

An integrated admission, document verification, scholarship screening and RPA automation platform implemented as a functional full-stack academic prototype.

The system combines a React/TypeScript frontend, FastAPI REST API, SQLite persistence, local demo authentication, local OCR services, configurable scholarship screening, administrator review and a UiPath-compatible document-processing contract.

## Local demo authentication

This project uses the FastAPI development authentication path for localhost testing. The app is explicitly configured with `AUTH_MODE=development` and `VITE_AUTH_MODE=development` in the local `.env` file so demo login uses the existing student email/password records instead of Firebase Google sign-in.

Do not enable this mode for production. It is intended only for local development and classroom demos.

## Quick Start

```powershell
npm install
\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Run the frontend:

```powershell
npm run dev -- --host 127.0.0.1
```

Run the backend:

```powershell
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Frontend: `http://127.0.0.1:5173/`  
API: `http://127.0.0.1:8000/`  
Swagger: `http://127.0.0.1:8000/docs`

## Documentation

- [Documentation README](docs/README.md)
- [Project report source](docs/PROJECT_REPORT.md)
- [Generated artifacts](docs/artifacts/)

Generate the DOCX report, PPTX presentation and PNG diagrams with:

```powershell
\.venv\Scripts\python.exe docs\generate_artifacts.py
```

## Important Scope Notes

Document verification checks consistency between selected OCR-extracted fields and student data. It does not prove official authenticity. Scholarship outcomes are configurable screening results, not official government eligibility decisions. Firebase production mode, UiPath execution, scanned-document OCR and automated route testing remain to be verified. The current development authentication default and public legacy/prototype routes require hardening before production deployment.

Never place Firebase service-account credentials, tokens, passwords or personal student data in this repository, README files or screenshots.