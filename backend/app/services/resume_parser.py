"""简历文件解析服务，支持 PDF、DOCX、TXT、Markdown 格式。"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_resume_file(file_path: str, ext: str | None = None) -> str:
    """Parse a resume file and extract raw text content.

    Args:
        file_path: Absolute path to the uploaded resume file.
        ext: File extension (e.g. '.pdf', '.docx', '.txt').
             If None, auto-detected from the filename.

    Returns:
        Extracted plain text content.

    Raises:
        ValueError: If the file type is unsupported or parsing fails.
    """
    if ext is None:
        ext = Path(file_path).suffix.lower()

    parsers = {
        ".pdf": _parse_pdf,
        ".docx": _parse_docx,
        ".txt": _parse_txt,
        ".md": _parse_txt,
        ".markdown": _parse_txt,
    }

    parser = parsers.get(ext)
    if parser is None:
        raise ValueError(f"Unsupported file extension: '{ext}'")

    try:
        text = parser(file_path)
        logger.info(f"Successfully parsed resume: {file_path} ({len(text)} chars)")
        return text
    except Exception as e:
        logger.error(f"Failed to parse resume {file_path}: {e}")
        raise ValueError(f"Failed to parse file: {e}") from e


def _parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    from PyPDF2 import PdfReader

    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def _parse_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    from docx import Document

    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _parse_txt(file_path: str) -> str:
    """Read text from a TXT file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
