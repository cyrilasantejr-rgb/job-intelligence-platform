import io

import pytest
from docx import Document
from fastapi import HTTPException

from app.services.resume_service import extract_resume_text


def make_docx_bytes(paragraphs: list[str]) -> bytes:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_extract_resume_text_from_txt():
    text_bytes = b"Experienced Python developer with AWS and SQL skills."
    result = extract_resume_text("resume.txt", text_bytes)
    assert "Python developer" in result
    assert "AWS" in result


def test_extract_resume_text_from_docx():
    docx_bytes = make_docx_bytes(
        ["Jane Doe", "Software Engineer", "Skills: Python, SQL, AWS, Airflow"]
    )
    result = extract_resume_text("resume.docx", docx_bytes)
    assert "Jane Doe" in result
    assert "Python" in result
    assert "Airflow" in result


def test_extract_resume_text_collapses_whitespace():
    text_bytes = b"Line one\n\n\nLine   two   with   gaps"
    result = extract_resume_text("resume.txt", text_bytes)
    assert "  " not in result
    assert "Line one Line two with gaps" == result


def test_extract_resume_text_unsupported_extension_raises_400():
    with pytest.raises(HTTPException) as exc_info:
        extract_resume_text("resume.pages", b"whatever")
    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in exc_info.value.detail


def test_extract_resume_text_empty_content_raises_400():
    with pytest.raises(HTTPException) as exc_info:
        extract_resume_text("resume.txt", b"   ")
    assert exc_info.value.status_code == 400
    assert "Couldn't extract" in exc_info.value.detail
