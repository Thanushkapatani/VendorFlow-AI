
from modules.validation import validate_vendor


def complete_vendor():
    return {
        "company_name": "Acme Technologies Pvt Ltd",
        "gstin": "29ABCDE1234F1Z5",
        "bank_account_holder": "Acme Technologies Pvt Ltd",
        "documents": {
            "business_registration": True,
            "gst_certificate": True,
            "bank_proof": True
        }
    }


def test_approved_vendor():
    vendor = complete_vendor()

    result = validate_vendor(vendor)

    assert result["decision"] == "APPROVED"


def test_missing_document():
    vendor = complete_vendor()

    vendor["documents"]["gst_certificate"] = False

    result = validate_vendor(vendor)

    assert result["decision"] == "PENDING"


def test_bank_name_mismatch():
    vendor = complete_vendor()

    vendor["bank_account_holder"] = "Different Company Ltd"

    result = validate_vendor(vendor)

    assert result["decision"] == "PENDING"


def test_duplicate_gstin():
    vendor = complete_vendor()

    result = validate_vendor(
        vendor,
        existing_gstins=["29ABCDE1234F1Z5"]
    )

    assert result["decision"] == "REJECTED"
