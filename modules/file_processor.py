import pandas as pd
from PyPDF2 import PdfReader
from docx import Document


def process_csv(file):

    df = pd.read_csv(file)

    return df.to_string()


def process_xlsx(file):

    df = pd.read_excel(file)

    return df.to_string()


def process_txt(file):

    return file.read().decode("utf-8")


def process_pdf(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


def process_docx(file):

    doc = Document(file)

    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text


def process_uploaded_file(uploaded_file):

    file_type = uploaded_file.name.split(".")[-1]

    if file_type == "csv":
        return process_csv(uploaded_file)

    elif file_type == "xlsx":
        return process_xlsx(uploaded_file)

    elif file_type == "txt":
        return process_txt(uploaded_file)

    elif file_type == "pdf":
        return process_pdf(uploaded_file)

    elif file_type == "docx":
        return process_docx(uploaded_file)

    else:
        return "Unsupported file type."