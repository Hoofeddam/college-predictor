from pathlib import Path
from pypdf import PdfReader


def load_documents(documents_folder="documents"):

    documents = []

    pdf_files = Path(documents_folder).rglob("*.pdf")

    document_id = 0

    for pdf in pdf_files:

        reader = PdfReader(pdf)

        source = pdf.parent.name

        year = None

        if "2026" in pdf.name:
            year = 2026

        for page_number, page in enumerate(reader.pages, start=1):

            page_text = page.extract_text()

            if not page_text:
                continue

            documents.append(
                {
                    "id": document_id,
                    "source": source,
                    "year": year,
                    "file_name": pdf.name,
                    "path": str(pdf),
                    "page": page_number,
                    "text": page_text
                }
            )

            document_id += 1

    return documents