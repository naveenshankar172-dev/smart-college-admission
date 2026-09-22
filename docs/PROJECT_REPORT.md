# SMART COLLEGE ADMISSION & DOCUMENT VERIFICATION SYSTEM

## An Integrated Admission, Document Verification, Scholarship Screening and RPA Automation Platform

**Academic project report**  
**Student:** `[Student name]`  
**Registration number:** `[Registration number]`  
**Department:** `[Department]`  
**Institution:** `[College / university]`  
**Academic year:** `[Year]`

> **Evidence status.** This report describes source code inspected on 21 September 2026. Statements are labelled as implemented, manually checked, partially tested, not tested, or future scope where the evidence matters. No production credentials are included.

## Certificate

`[Insert institution-approved certificate text and signatures manually.]`

## Declaration

`[Insert student declaration and signatures manually.]`

## Acknowledgement

`[Insert acknowledgement text manually.]`

## Abstract

College admission commonly requires repeated collection, review and status communication around student information and supporting documents. This project presents a functional full-stack academic prototype that centralizes student onboarding, admission application management, document upload, OCR-assisted content consistency checks, configurable scholarship screening, administrator review and notifications. The browser client is implemented with React and TypeScript, while FastAPI provides the REST API and SQLite provides default persistence. Firebase Authentication and Google Sign-In are supported through Firebase ID tokens verified by the server. A UiPath-compatible REST contract exposes a pending-document queue and processing endpoints; OCR remains implemented in FastAPI services rather than inside UiPath. PDF text extraction uses `pypdf`, while scanned PDFs and images can use PyMuPDF, Pillow, pytesseract and a local Tesseract executable. Document verification compares selected extracted fields, including name and date of birth, with student records. It checks content consistency and does not independently establish official document authenticity. Scholarship rules are configurable and produce potential eligibility, verification-required or not-eligible outcomes; they are not official government determinations. The system also provides administrative review and notification workflows. The prototype demonstrates integration of authentication, admission, documents, OCR, deterministic verification, RPA orchestration, scholarships and administration, while identifying security hardening, test automation and deployment scalability as remaining work.

## Table of Contents

1. Introduction  
2. Existing System  
3. Proposed System  
4. Requirements  
5. System Design  
6. Implementation  
7. Testing  
8. Results  
9. Limitations  
10. Future Scope  
11. Conclusion  
References  
Appendix

# Chapter 1 - Introduction

## 1.1 Background

Admission teams process student profiles, applications and supporting documents across multiple steps. A centralized workflow can reduce repeated data entry, make status information easier to find and provide a consistent place for administrative review.

## 1.2 Problem Statement

Manual or fragmented admission processes can make document handling, duplicate submissions, status tracking and scholarship screening difficult to coordinate. The project addresses these workflow problems without claiming that every institution uses the same process or that automation alone proves document authenticity.

## 1.3 Motivation

The motivation is to demonstrate a practical academic system that combines a student-facing workflow with server-side persistence, OCR-assisted processing, configurable rules and an administrator review surface.

## 1.4 Need for the System

- Centralized student and admission information.
- Digital document submission and processing status.
- Consistent comparison of extracted document fields with stored student information.
- Configurable scholarship screening rather than manual first-pass comparison.
- Visible status changes and notifications for students and administrators.

## 1.5 Proposed Solution

The proposed solution is a React frontend connected to a FastAPI API. Firebase Authentication can establish identity; Firebase Admin verifies bearer tokens on protected endpoints. SQLite persists students, applications, documents, scholarships, scholarship applications and notifications. UiPath can orchestrate document processing through REST calls, while FastAPI services perform OCR and deterministic consistency verification.

## 1.6 Scope

The scope includes student onboarding, profiles, admission applications, documents, OCR, consistency verification, scholarship screening/application, notifications, admin review and a UiPath API contract. It excludes official government eligibility decisions, independent authenticity certification, production-scale deployment, email delivery, audit history and a complete automated test suite.

# Chapter 2 - Existing System

A conventional process may combine web forms, email, paper/PDF exchange, spreadsheets and manual communication. Typical risks include repeated entry, difficult document retrieval, fragmented status information, manual first-pass scholarship comparison and increased administrative effort. These are realistic process limitations, not universal claims about all existing college systems.

## Existing versus proposed

| Concern | Conventional process | Proposed prototype |
|---|---|---|
| Identity | Separate or manually checked identity | Firebase/Google path plus development mode |
| Admission | Forms and separate tracking | FastAPI-backed application records |
| Documents | Manual file exchange | Upload metadata, local storage and processing status |
| Verification | Repeated manual comparison | OCR-assisted deterministic consistency check plus review |
| Scholarship | Manual first-pass screening | Configurable rules and application workflow |
| Communication | Fragmented messages | Stored notifications and read state |
| Administration | Multiple sources | Admin portal backed by API statistics and records |

# Chapter 3 - Proposed System

## 3.1 Architecture

```text
Student
  |
React + TypeScript + Tailwind frontend
  |
Firebase Authentication / Google Sign-In
  |
Firebase ID token in Authorization: Bearer
  |
FastAPI REST API
  |                 \-- Admin portal and notifications
SQLite database     \-- UiPath document-processing contract
  |
OCR and verification services
```

The architecture is a modular full-stack application with a single FastAPI API layer. It is not represented as a Kubernetes or microservices deployment.

## 3.2 Student workflow

Google sign-in establishes a Firebase user. The frontend requests a Firebase session; first-time users complete onboarding and create a student record. Returning users are directed to the portal. Students can update profiles, submit applications, upload documents, inspect scholarship results, apply and read notifications.

## 3.3 Document workflow

The active flow is upload -> local storage/metadata -> pending queue -> UiPath polling -> FastAPI processing -> OCR/text extraction -> deterministic field comparison -> SQLite result -> student/admin status. The service supports text PDFs and OCR fallback for scanned PDFs/images.

## 3.4 Scholarship workflow

Scholarships expose configurable JSON rules. The evaluator checks minimum academic percentage, course substring matching, required income information and required document names. Results are `Potentially Eligible`, `Requires Verification` or `Not Eligible`. These are screening outcomes, not official decisions.

# Chapter 4 - Requirements

## 4.1 Functional requirements

1. Authenticate users through Firebase/Google Sign-In when Firebase mode is configured.
2. Support onboarding and returning-student session detection.
3. Persist and update student profile information.
4. Create and review admission applications.
5. Upload, list, download and delete supported document files subject to current route controls.
6. Extract PDF/image text and store OCR/verification results.
7. Screen scholarship rules and prevent duplicate scholarship applications in the main path.
8. Create notifications for relevant admission, document and scholarship events.
9. Provide admin statistics and review/update actions.
10. Expose UiPath-compatible document-processing endpoints.

## 4.2 Non-functional requirements

- Web-based and modular.
- JSON REST communication.
- SQLite persistence for the academic prototype.
- Configurable origins and service paths through environment variables.
- Clear processing states and structured errors.
- Ownership checks on protected student operations.

## 4.3 Hardware requirements

An ordinary development laptop/desktop with a modern browser, approximately 4 GB or more available RAM, local storage for the application/database/uploads, and optional Tesseract installation is sufficient for the prototype. No high-end hardware is required.

## 4.4 Software requirements

Node.js/npm, Python, FastAPI dependencies, SQLite, a modern browser, Firebase project configuration for Firebase mode, Tesseract for image OCR, and optional UiPath for orchestration.

# Chapter 5 - System Design

## 5.1 Database architecture

The SQLAlchemy models define these entities. Exact field names and types should be confirmed against `backend/app/models.py` when the institution requires a schema appendix.

| Entity | Purpose | Relationships |
|---|---|---|
| `students` | Identity, profile and academic data | Owns applications, documents, scholarship applications and notifications |
| `applications` | Admission application and review state | Belongs to one student; owns documents |
| `documents` | File metadata, storage path, OCR, verification and processing state | Optionally references an application and student |
| `scholarships` | Scholarship definitions and JSON-configured rules | Owns scholarship applications |
| `scholarship_applications` | Student application and review state | Links one student and one scholarship |
| `notifications` | Student-facing event messages and read state | Belongs to one student |

Primary keys are SQLAlchemy integer identifiers in the current model layer; foreign-key relationships are used for the ownership links described above. The generated ER diagram intentionally shows relationships rather than inventing unverified column lists.

## 5.2 Security design

Firebase Admin verifies Firebase ID tokens with revocation checking in protected dependencies. The frontend sends the token as a bearer token and does not contain Firebase Admin credentials. Student ownership checks are implemented for protected profile, application, notification, document and scholarship-application paths. Admin authorization is implemented in the Firebase path. Development mode remains available only for explicit local debugging, and UiPath processing is protected by an automation key or admin bearer token.

## 5.3 OCR and verification design

Normal PDF: `pypdf` text extraction -> extracted text.  
Scanned PDF: PDF page rendering -> image -> Tesseract OCR -> extracted text.  
Then: extracted text -> field extraction -> student-record comparison -> result.

The implementation extracts selected name, date-of-birth and, for selected document types, identity/Aadhaar information. A normalized name/date-of-birth comparison can produce `verified` when at least one field matches and no field mismatches, `manual_review` on mismatches, or `failed` when no field can be confidently matched. A mismatch such as an OCR name differing from the student record is a reason for manual review. This does not prove official authenticity.

## 5.4 RPA design

UiPath polls `GET /api/documents/pending`, extracts IDs, calls `POST /api/documents/{document_id}/process`, optionally uses `/ocr` or `/verify`, retrieves `/verification`, and logs returned status/errors. FastAPI owns OCR and verification. No REFramework claim is made because it was not found in the source.

# Chapter 6 - Implementation

## 6.1 Authentication and identity

Implemented: Firebase Authentication, Google popup sign-in, Firebase UID, bearer ID-token transfer, server-side Firebase Admin verification, onboarding, returning-user lookup, logout and protected frontend routes. Firebase is the default and primary authentication mode. Development email/login paths remain available only when both backend `AUTH_MODE=development` and frontend `VITE_AUTH_MODE=development` are explicitly configured.

## 6.2 Student profile

The profile stores personal information, phone and course/academic information through the student API and persists it through SQLAlchemy/SQLite.

## 6.3 Admission management

The API supports application creation, student application retrieval, admin collection/statistics retrieval and admin status updates with remarks/notifications. Multiple-admission uniqueness/lifecycle enforcement is not implemented.

## 6.4 Document management

The active frontend uses the upload endpoint for supported files, while legacy connected pages remain in the repository and should not be used as evidence of the active workflow. Duplicate document-type protection, ownership validation and file size/type checks exist in the implemented paths. Document listing, processing, download, update and deletion now require student, admin or explicit automation authorization according to the operation.

## 6.5 Scholarship module

The active module lists scholarships, evaluates configurable rules, submits applications through the protected main route, prevents duplicates in the main path and exposes admin review/update operations. The defective duplicate `POST /api/scholarships/applications` route was removed; the active API is `POST /api/scholarship-applications`.

## 6.6 Notifications and admin

Notification events cover admission submission/status, document upload/processing and scholarship submission/status. The admin UI includes dashboard counts, application review, document verification review, scholarship CRUD, scholarship application review, aggregate reports and a read-only settings view. Email delivery, export, audit history and background worker status are not implemented.

## 6.7 API inventory

| Group | Implemented routes inspected |
|---|---|
| Health/auth | `GET /api/health`; `GET /api/auth/firebase/session`; `POST /api/auth/firebase/onboard`; `POST /api/auth/login` |
| Students | `GET/POST /api/students`; `GET/PATCH /api/students/{student_id}`; notifications and student scholarship routes |
| Applications | admin statistics/list/detail/update; student list; `POST /api/applications` |
| Documents | list/create/upload/student list/pending/detail/process/ocr/verify/verification/download/update/delete |
| Scholarships | list/create/detail/update/delete; eligibility; scholarship application list/create/detail/update |
| Notifications | mark one read; mark all read for a student |

For exact authentication dependencies and request/response schemas, consult the route modules and `backend/app/schemas.py`; the documentation deliberately does not invent payload fields beyond those verified in source.

# Chapter 7 - Testing

## 7.1 Evidence-based test matrix

| ID | Test | Expected | Actual evidence | Status |
|---|---|---|---|---|
| T01 | Vite dev server reachability | Frontend responds | HTTP 200 from `http://127.0.0.1:5173/` | PASS |
| T02 | FastAPI health endpoint | JSON health response | HTTP 200, `{"status":"ok"}` | PASS |
| T03 | Firebase production sign-in | Authenticated session | Not executed with production credentials | NOT TESTED |
| T04 | Onboarding/profile persistence | Student persists and reloads | No automated test; source path inspected | PARTIALLY TESTED |
| T05 | Admission submission/review | Status and notification update | No automated test | NOT TESTED |
| T06 | File upload and ownership | Valid file stored and isolated | Source inspected; runtime matrix not executed | PARTIALLY TESTED |
| T07 | Text-PDF OCR | Text extracted | Tesseract/PDF fixtures not executed | NOT TESTED |
| T08 | Scanned-PDF OCR | OCR fallback works | Not executed | NOT TESTED |
| T09 | Document consistency | Match/mismatch status | Source inspected; no automated test | PARTIALLY TESTED |
| T10 | UiPath processing loop | Pending/process/result contract works | UiPath not executed | NOT TESTED |
| T11 | Scholarship eligibility | Rule result returned | Source inspected; no automated test | PARTIALLY TESTED |
| T12 | Scholarship duplicate prevention | Duplicate rejected | Source inspected; no runtime test | PARTIALLY TESTED |
| T13 | Notification read state | One/all read actions persist | No automated test | NOT TESTED |
| T14 | Admin authorization | Non-admin denied | Firebase production mode not executed; development mode is intentionally weak | NOT TESTED |
| T15 | Database persistence/migrations | Tables and migration paths work | Startup health passed; migration matrix not executed | PARTIALLY TESTED |

There is no pytest, Vitest, Playwright or FastAPI `TestClient` suite in the repository. PASS is used only for the two reachability checks actually performed in this documentation pass.

# Chapter 8 - Results

The verified prototype demonstrates a connected frontend/backend, a reachable FastAPI service, Firebase authentication integration in source, persistent domain models, document processing services, deterministic content consistency checks, scholarship screening, notifications, admin workflows and an UiPath-compatible processing contract. It does not demonstrate production readiness, official document authenticity, official scholarship decisions or verified performance metrics. No fabricated percentages or throughput values are reported.

# Chapter 9 - Limitations

- Development authentication is retained only as an explicit local-debug mode; Firebase is the default.
- Legacy connected pages remain in the repository, but sensitive backend routes now require authentication, ownership or admin/automation authorization.
- SQLite and local uploads are appropriate for an academic prototype but not a demonstrated institution-scale deployment.
- OCR depends on document quality and Tesseract availability.
- Verification checks extracted content consistency, not official authenticity or tampering.
- Scholarship output is configurable screening, not a government or provider decision.
- UiPath execution, email delivery, audit logging, exports and background orchestration are not implemented/tested.
- Automated testing and production Firebase behavior remain unverified.

# Chapter 10 - Future Scope

Future work includes PostgreSQL, cloud document storage, stronger authenticity analysis, improved OCR, advanced analytics and exports, a configurable admin rule engine, institution-wide deployment, audit logging, additional identity providers, a mobile application and scalable RPA orchestration. These are future enhancements, not current implementation claims.

# Chapter 11 - Conclusion

The Smart College Admission & Document Verification System integrates authentication, admission, document upload, OCR, content consistency verification, RPA orchestration, configurable scholarship screening, administrative review and notifications in one academic prototype. The source audit supports describing it as a functional full-stack system, while the test and security findings require careful qualification. Its strongest contribution is the integration of these workflow stages with explicit status and ownership concepts. Production deployment would require authentication hardening, route closure, stronger storage and authenticity controls, automated tests and operational monitoring.

## References

1. FastAPI source and route modules in `backend/app/`.
2. React/TypeScript source in `src/`.
3. Firebase Authentication and Firebase Admin SDK configuration used by the project.
4. PyMuPDF, pypdf, Pillow, pytesseract and Tesseract integrations present in `backend/app/services/ocr_service.py`.
5. UiPath REST workflow contract documented in `backend/README.md`.

## Appendix A - Screenshot plan

Capture only with test/demo accounts and redact personal data, tokens and credentials: Google sign-in, onboarding, student dashboard, admission form, upload, verification result, scholarship list/eligibility/application, notifications, admin dashboard/applications/documents/scholarships/reports, Swagger UI, UiPath workflow and non-sensitive database evidence.

## Appendix B - Information to fill manually

Student/team names, registration numbers, college/department, supervisor, academic year, certificate/declaration text, acknowledgement, approved screenshots, tested Firebase/Tesseract/UiPath results and institution formatting requirements.
