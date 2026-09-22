from pathlib import Path
import re
import logging
import os
import shutil

logger = logging.getLogger(__name__)


class OCRProcessingError(Exception):
    pass


def configure_tesseract() -> str | None:
    configured_path = os.getenv("TESSERACT_CMD", "").strip()
    executable = configured_path or shutil.which("tesseract")
    if not executable:
        logger.warning("Tesseract is unavailable. Set TESSERACT_CMD to enable image OCR.")
        return None
    candidate = Path(executable).expanduser().resolve()
    if not candidate.is_file():
        logger.warning("TESSERACT_CMD does not point to an executable file: %s", configured_path)
        return None
    try:
        import pytesseract
    except ImportError:
        logger.warning("pytesseract is not installed. Install backend requirements to enable image OCR.")
        return None
    pytesseract.pytesseract.tesseract_cmd = str(candidate)
    logger.info("Tesseract OCR configured at %s", candidate)
    return str(candidate)


def tesseract_status() -> dict[str, str | bool | None]:
    configured = os.getenv("TESSERACT_CMD", "").strip() or shutil.which("tesseract")
    if not configured:
        return {"available": False, "path": None, "message": "Tesseract is not installed or TESSERACT_CMD is not configured."}
    candidate = Path(configured).expanduser()
    if not candidate.is_file():
        return {"available": False, "path": str(candidate), "message": "TESSERACT_CMD does not point to an existing executable."}
    return {"available": True, "path": str(candidate.resolve()), "message": "Tesseract is available for image OCR."}


def _recover_pdf_literals(file_path: Path) -> str:
    raw = file_path.read_bytes()
    literals = re.findall(rb"\(([^()\r\n]{3,})\)\s*Tj", raw)
    return "\n".join(item.decode("latin-1", errors="ignore") for item in literals).strip()


def _ocr_pdf_pages(file_path: Path) -> str:
    try:
        import fitz
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise OCRProcessingError("Scanned PDF OCR requires PyMuPDF, Pillow, and pytesseract.") from exc
    configure_tesseract()
    if not tesseract_status()["available"]:
        raise OCRProcessingError("Scanned PDF OCR requires Tesseract. Set TESSERACT_CMD to the executable path.")
    try:
        page_text: list[str] = []
        with fitz.open(str(file_path)) as pdf:
            for page in pdf:
                pixels = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
                page_text.append(pytesseract.image_to_string(image).strip())
        return "\n\n".join(text for text in page_text if text).strip()
    except Exception as exc:
        raise OCRProcessingError("Scanned PDF pages could not be rendered or OCR processed.") from exc


def extract_text(file_path: Path, file_type: str | None = None) -> str:
    if not file_path.is_file():
        raise OCRProcessingError("Stored document file was not found")
    try:
        if file_path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader

                text = "\n".join(page.extract_text() or "" for page in PdfReader(str(file_path)).pages).strip()
            except Exception:
                text = _recover_pdf_literals(file_path)
            if len(re.sub(r"\s+", "", text)) < 10:
                text = _ocr_pdf_pages(file_path)
        else:
            try:
                from PIL import Image
                import pytesseract
            except ImportError as exc:
                raise OCRProcessingError("Image OCR Python dependencies are unavailable. Install Pillow and pytesseract.") from exc
            except Exception as exc:
                raise OCRProcessingError("The image could not be read by the OCR engine") from exc
            configure_tesseract()
            if not tesseract_status()["available"]:
                raise OCRProcessingError("Image OCR is unavailable because Tesseract is not installed. Set TESSERACT_CMD to the executable path.")
            try:
                text = pytesseract.image_to_string(Image.open(file_path)).strip()
            except Exception as exc:
                raise OCRProcessingError("The image could not be read by the OCR engine") from exc
        if not text:
            raise OCRProcessingError("No readable text was found in the document")
        return text
    except OCRProcessingError:
        raise
    except Exception as exc:
        raise OCRProcessingError("The document could not be processed") from exc
