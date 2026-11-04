
import re


# Required documents for vendor onboarding
REQUIRED_DOCUMENTS = [
    "business_registration",
    "gst_certificate",
    "bank_proof"
]


def normalize_name(name):
    """
    Normalize company names before comparing them.
    Ignores differences in capitalization and punctuation.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


def validate_gstin(gstin):
    """
    Check whether a GSTIN follows the expected
    15-character Indian GSTIN format.

    This does NOT verify the GSTIN against
    the official government database.
    """
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"

    return bool(re.fullmatch(pattern, gstin.upper()))


def validate_vendor(vendor, existing_gstins=None):
    """
    Validate vendor details and uploaded documents.

    Returns:
        - Individual validation results
        - Final onboarding decision
        - Explanation of the decision
    """

    if existing_gstins is None:
        existing_gstins = []

    checks = []

    def add_check(name, status, message):
        checks.append({
            "check": name,
            "status": status,
            "message": message
        })

    # 1. Check company name
    company_name = vendor.get("company_name", "").strip()

    if company_name:
        add_check(
            "Company Name",
            "PASS",
            "Company name is provided."
        )
    else:
        add_check(
            "Company Name",
            "ISSUE",
            "Company name is missing."
        )

    # 2. Check GSTIN
    gstin = vendor.get("gstin", "").strip().upper()

    if not gstin:
        add_check(
            "GSTIN",
            "ISSUE",
            "GSTIN is missing."
        )

    elif not validate_gstin(gstin):
        add_check(
            "GSTIN",
            "ISSUE",
            "GSTIN format is invalid. Please correct it."
        )

    else:
        add_check(
            "GSTIN",
            "PASS",
            "GSTIN follows the expected format."
        )

    # 3. Check bank account holder name
    bank_name = vendor.get(
        "bank_account_holder", ""
    ).strip()

    if not bank_name:
        add_check(
            "Bank Account Name",
            "ISSUE",
            "Bank account holder name is missing."
        )

    elif company_name and (
        normalize_name(company_name) != normalize_name(bank_name)
    ):
        add_check(
            "Bank Account Name",
            "REVIEW",
            "Bank account holder name differs from company name. Manual review required."
        )

    else:
        add_check(
            "Bank Account Name",
            "PASS",
            "Bank account holder name matches the company name."
        )

    # 4. Check required documents
    documents = vendor.get("documents", {})

    for document in REQUIRED_DOCUMENTS:

        if documents.get(document, False):
            add_check(
                document,
                "PASS",
                f"{document.replace('_', ' ').title()} uploaded."
            )
        else:
            add_check(
                document,
                "ISSUE",
                f"Required document missing: {document.replace('_', ' ')}."
            )

    # 5. Check for duplicate GSTIN
    normalized_existing = {
        item.strip().upper()
        for item in existing_gstins
        if item
    }

    duplicate = (
        bool(gstin)
        and validate_gstin(gstin)
        and gstin in normalized_existing
    )

    if duplicate:
        add_check(
            "Duplicate Check",
            "DUPLICATE",
            "This GSTIN already exists in the vendor registry."
        )
    else:
        add_check(
            "Duplicate Check",
            "PASS",
            "No matching GSTIN found in the existing vendor registry."
        )

    # 6. Generate final decision
    if duplicate:
        decision = "REJECTED"
        explanation = (
            "Duplicate GSTIN detected in the existing vendor registry."
        )

    elif any(
        check["status"] in ["ISSUE", "REVIEW"]
        for check in checks
    ):
        decision = "PENDING"
        explanation = (
            "Some requirements are incomplete or require manual review."
        )

    else:
        decision = "APPROVED"
        explanation = (
            "All configured onboarding checks passed."
        )

    return {
        "decision": decision,
        "explanation": explanation,
        "checks": checks
    }
