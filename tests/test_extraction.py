
from io import BytesIO
from pypdf import PdfWriter

from modules.extraction import extract_text_from_pdf


def create_blank_pdf():
    """Create a simple one-page PDF for testing."""

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)

    pdf_bytes = BytesIO()
    writer.write(pdf_bytes)

    return pdf_bytes.getvalue()


def test_blank_pdf_is_detected():
    pdf = create_blank_pdf()

    result = extract_text_from_pdf(pdf)

    assert result["success"] is False
    assert result["page_count"] == 1
    assert "no selectable text" in result["message"]


def test_invalid_pdf_is_handled():
    result = extract_text_from_pdf(b"This is not a PDF")

    assert result["success"] is False
    assert result["page_count"] == 0
    assert "Could not read PDF" in result["message"]
