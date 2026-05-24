"""
file_processor.py
Extracts text content from various uploaded file types.
"""

import io
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document


def process_csv(file) -> str:
    try:
        df = pd.read_csv(file)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error reading CSV: {e}"


def process_xlsx(file) -> str:
    try:
        df = pd.read_excel(file)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error reading XLSX: {e}"


def process_txt(file) -> str:
    try:
        raw = file.read()
        return raw.decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error reading TXT: {e}"


def process_pdf(file) -> str:
    try:
        reader = PdfReader(file)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages) or "No readable text found in PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"


def process_docx(file) -> str:
    try:
        doc = Document(file)
        lines = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(lines) or "No readable text found in DOCX."
    except Exception as e:
        return f"Error reading DOCX: {e}"


def process_uploaded_file(uploaded_file) -> str:
    """Dispatch to the correct reader based on file extension."""
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        return process_csv(uploaded_file)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        return process_xlsx(uploaded_file)
    elif name.endswith(".txt"):
        return process_txt(uploaded_file)
    elif name.endswith(".pdf"):
        return process_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return process_docx(uploaded_file)
    else:
        return "Unsupported file type."