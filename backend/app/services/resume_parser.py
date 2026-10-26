"""简历文件解析服务，支持 PDF、DOCX、TXT、Markdown 格式。"""

import logging
import sys
from functools import lru_cache
from pathlib import Path
from threading import Lock

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
_ocr_lock = Lock()

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
    parsers.update({extension: _parse_image for extension in IMAGE_EXTENSIONS})

    parser = parsers.get(ext)
    if parser is None:
        raise ValueError(f"Unsupported file extension: '{ext}'")

    try:
        text = parser(file_path)
        if not text.strip():
            raise ValueError("未识别到文字，请上传清晰、正向且包含完整文字的简历。")
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


@lru_cache(maxsize=1)
def _load_windows_runtime():
    """优先加载虚拟环境运行库，兼容系统中仍保留旧版 DLL 的 Windows。"""
    if sys.platform != "win32":
        return ()
    import ctypes

    directory = Path(sys.prefix) / "Scripts"
    return tuple(
        ctypes.WinDLL(str(directory / name))
        for name in (
            "msvcp140.dll",
            "msvcp140_1.dll",
            "msvcp140_2.dll",
        )
    )


@lru_cache(maxsize=1)
def _get_ocr_engine():
    """复用本地 OCR 模型，控制 CPU 线程数。"""
    _load_windows_runtime()
    from rapidocr import RapidOCR

    return RapidOCR(params={"EngineConfig.onnxruntime.intra_op_num_threads": 2})


def _parse_image(file_path: str) -> str:
    """识别中英文简历图片，原始图片留在本机。"""
    import numpy as np
    from PIL import Image, ImageOps, UnidentifiedImageError

    try:
        with Image.open(file_path) as image:
            if image.width * image.height > 25_000_000:
                raise ValueError("图片分辨率过大，请缩小至 2500 万像素以内。")
            if image.format not in {"JPEG", "PNG", "WEBP", "BMP"}:
                raise ValueError("图片格式不受支持。")
            pixels = np.asarray(ImageOps.exif_transpose(image).convert("RGB"))
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("图片损坏或文件内容并非有效图片。") from error
    with _ocr_lock:
        result = _get_ocr_engine()(pixels)
    return "\n".join(result.txts if result.txts is not None else [])
