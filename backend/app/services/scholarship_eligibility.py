import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def _rules(scholarship: models.Scholarship) -> dict[str, object]:
    try:
        return json.loads(scholarship.eligibility_rules or "{}")
    except json.JSONDecodeError:
        return {}


def _required_documents(scholarship: models.Scholarship) -> list[str]:
    try:
        return json.loads(scholarship.required_documents or "[]")
    except json.JSONDecodeError:
        return []


def evaluate_eligibility(db: Session, student: models.Student, scholarship: models.Scholarship) -> schemas.EligibilityResult:
    rules = _rules(scholarship)
    matched: list[str] = []
    unmatched: list[str] = []
    missing: list[str] = []

    minimum = rules.get("min_percentage")
    if minimum is not None:
        if student.academic_score is None:
            missing.append("academic_score")
        elif student.academic_score >= float(minimum):
            matched.append(f"academic_score >= {minimum}")
        else:
            unmatched.append(f"academic_score >= {minimum}")

    course_contains = str(rules.get("course_contains", "")).strip().lower()
    if course_contains:
        if not student.course:
            missing.append("course")
        elif course_contains in student.course.lower():
            matched.append(f"course contains '{course_contains}'")
        else:
            unmatched.append(f"course contains '{course_contains}'")

    if rules.get("requires_income_information"):
        missing.append("annual_family_income")

    required_documents = _required_documents(scholarship)
    available_documents = list(db.scalars(select(models.Document.name).where(models.Document.student_id == student.id)).all())
    missing_documents = [required for required in required_documents if not any(required.lower() in available.lower() for available in available_documents)]
    if required_documents and not missing_documents:
        matched.append("required documents present")
    elif missing_documents:
        missing.append("required documents")

    if unmatched:
        status = "Not Eligible"
    elif missing:
        status = "Requires Verification"
    else:
        status = "Potentially Eligible"
    return schemas.EligibilityResult(
        student_id=student.id,
        scholarship_id=scholarship.id,
        eligibility_status=status,
        matched_rules=matched,
        unmatched_rules=unmatched,
        missing_information=missing,
        required_documents=required_documents,
        available_documents=available_documents,
        missing_documents=missing_documents,
        remarks="Eligibility screening completed. Final eligibility requires verification.",
    )
