from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))

    text_parts: list[str] = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            text_parts.append(text)

    return "\n".join(text_parts).strip()
