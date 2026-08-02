import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw unicode text from PDF document binary bytes.

    Args:
        pdf_bytes: PDF file contents.

    Returns:
        str: Extracted text.
    """
    text = ""
    # Open PDF stream using PyMuPDF
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
    return text
