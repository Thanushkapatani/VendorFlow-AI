
from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(uploaded_file):
    """
    Extract selectable text from an uploaded PDF.

    Returns:
        success: Whether the PDF was read successfully
        text: Extracted text
        page_count: Number of pages
        message: Explanation of the result
    """

    try:
        # Start reading from the beginning of the file
        if isinstance(uploaded_file, bytes):
            pdf_file = BytesIO(uploaded_file)
        else:
            uploaded_file.seek(0)
            pdf_file = uploaded_file

        # Read the PDF
        reader = PdfReader(pdf_file)

        # Extract text from every page
        extracted_text = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            extracted_text.append(page_text)

        full_text = "\n".join(extracted_text).strip()

        # Check whether any readable text was found
        if not full_text:
            return {
                "success": False,
                "text": "",
                "page_count": len(reader.pages),
                "message": (
                    "PDF was opened, but no selectable text was found. "
                    "It may be a scanned document."
                )
            }

        return {
            "success": True,
            "text": full_text,
            "page_count": len(reader.pages),
            "message": "Document text extracted successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "message": f"Could not read PDF: {str(error)}"
        }
