from enum import Enum


class DocumentType(Enum):
    # Text & Office
    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"
    RTF = "rtf"

    # Spreadsheet
    XLSX = "xlsx"
    CSV = "csv"
    TSV = "tsv"

    # Presentation
    PPTX = "pptx"

    # Images
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    TIFF = "tiff"

    # Structured
    JSON = "json"
    XML = "xml"
    YAML = "yaml"

    # Code & Docs
    MD = "md"
    HTML = "html"
    PY = "py"
    JAVA = "java"

    # Archives
    ZIP = "zip"
    TAR = "tar"

    # Multimedia
    MP4 = "mp4"
    MP3 = "mp3"

    UNKNOWN = "unknown"
