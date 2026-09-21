from pathlib import Path

import pymupdf    # PyMuPDF
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = []

    with pymupdf.open(file_path) as pdf:
        for page in pdf:
            page_text = page.get_text()
            if page_text:
                text.append(page_text)

    return "\n".join(text).strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    document = Document(file_path)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs).strip()


def extract_text(file_path: str) -> str:
    """Automatically select the parser based on file extension."""
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".txt":
        return Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore"
        ).strip()

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Supported formats: PDF, DOCX, TXT."
    )