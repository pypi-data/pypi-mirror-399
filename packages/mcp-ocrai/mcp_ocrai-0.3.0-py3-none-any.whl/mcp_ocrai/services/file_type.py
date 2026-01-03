import base64
import mimetypes
from enum import Enum


class FileType(Enum):
    Document = 1
    Image = 2
    Unknown = 3


# This is the allowed mimetypes on mistral OCR 30-DIC-2025
document_mimes = {
    "application/pdf",  # PDF
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # Word Documents (.docx)
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # PowerPoint (.pptx)
    "text/plain",  # Text Files (.txt)
    "application/epub+zip",  # EPUB (.epub)
    "application/xml",  # XML/DocBook (.xml)
    "text/xml",  # XML/DocBook (.xml)
    "application/rtf",  # RTF (.rtf)
    "application/vnd.oasis.opendocument.text",  # OpenDocument Text (.odt)
    "application/x-bibtex",  # BibTeX/BibLaTeX (.bib)
    "application/x-fictionbook+xml",  # FictionBook (.fb2)
    "application/json",  # Jupyter Notebooks (.ipynb)
    "application/xml",  # JATS XML (.xml)
    "application/x-latex",  # LaTeX (.tex)
    "text/x-opml",  # OPML (.opml)
    "application/x-troff",  # Troff (.1, .man)
}

image_mimes = {
    "image/jpeg",  # JPEG (.jpg, .jpeg)
    "image/png",  # PNG (.png)
    "image/avif",  # AVIF (.avif)
    "image/tiff",  # TIFF (.tiff)
    "image/gif",  # GIF (.gif)
    "image/heic",  # HEIC/HEIF (.heic, .heif)
    "image/heif",  # HEIC/HEIF (.heic, .heif)
    "image/bmp",  # BMP (.bmp)
    "image/webp",  # WebP (.webp)
}


def categorize_file(mime_type) -> FileType:
    # Check if the MIME type is in the document or image sets
    if mime_type in document_mimes:
        return FileType.Document
    elif mime_type in image_mimes:
        return FileType.Image

    return FileType.Unknown


def read_document(path: str) -> tuple[FileType, str]:
    """
    Generate a URL with the format data:<mime_type>:base64,<base64content>
    """
    with open(path, "rb") as file:
        base64_content = base64.b64encode(file.read()).decode("utf-8")
        mime_type = mimetypes.guess_type(path)[0]
        return categorize_file(mime_type), f"data:{mime_type};base64,{base64_content}"
