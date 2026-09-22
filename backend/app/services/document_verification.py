import re
from dataclasses import dataclass

from ..models import Document, Student


@dataclass
class VerificationResult:
    matched_fields: list[str]
    mismatched_fields: list[str]
    remarks: str
    verification_status: str


def _value(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return " ".join(match.group(1).strip().split())
    return None


def extract_fields(text: str, document_type: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    name = _value([r"(?:name|applicant name|student name)\s*[:\-]\s*([^\n]+)", r"^name\s+([^\n]+)$"], text)
    date_of_birth = _value([r"(?:date of birth|dob|birth date)\s*[:\-]\s*([0-9]{1,4}[\-/][0-9]{1,2}[\-/][0-9]{2,4})"], text)
    if name:
        fields["name"] = name
    if date_of_birth:
        fields["date_of_birth"] = date_of_birth
    if document_type.lower() in {"id proof", "aadhaar", "identity document", "aadhaar/identity document"}:
        number = _value([r"(?:aadhaar|identity|document)\s*(?:number|no\.?)*\s*[:\-]?\s*([0-9][0-9 ]{7,})"], text)
        if number:
            fields["document_number"] = number
    return fields


def _normalise(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def verify_document(document: Document, student: Student, extracted_text: str) -> VerificationResult:
    extracted = extract_fields(extracted_text, document.document_type or document.name)
    matched: list[str] = []
    mismatched: list[str] = []
    remarks: list[str] = []
    if extracted.get("name"):
        if _normalise(extracted["name"]) == _normalise(student.name):
            matched.append("name")
        else:
            mismatched.append("name")
            remarks.append(f"OCR name '{extracted['name']}' differs from student name '{student.name}'.")
    else:
        remarks.append("Name was not confidently extracted.")
    if extracted.get("date_of_birth") and student.date_of_birth:
        if _normalise(extracted["date_of_birth"]) == _normalise(student.date_of_birth):
            matched.append("date_of_birth")
        else:
            mismatched.append("date_of_birth")
            remarks.append("OCR date of birth differs from the student record.")
    elif student.date_of_birth:
        remarks.append("Date of birth was not confidently extracted.")
    if mismatched:
        status = "manual_review"
    elif matched:
        status = "verified"
    else:
        status = "failed"
    if not remarks:
        remarks.append("Content fields matched the student record. This is a consistency check, not an authenticity decision.")
    return VerificationResult(matched, mismatched, " ".join(remarks), status)
