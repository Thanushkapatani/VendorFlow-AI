import streamlit as st
import pandas as pd

from modules.validation import validate_vendor
from modules.extraction import extract_text_from_pdf
from database import save_run, get_runs


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="VendorFlow AI",
    page_icon="🏢",
    layout="wide"
)


# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.app-heading {
    font-size: 30px;
    font-weight: 700;
    color: #172554;
}

.app-subheading {
    color: #64748b;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def generate_communication(decision, checks, company_name):

    if decision == "APPROVED":
        return f"""
Subject: Vendor Registration Approved

Dear {company_name},

Your vendor registration has been successfully
processed.

All configured onboarding checks have passed.

Thank you for registering with us.
"""

    if decision == "REJECTED":
        return f"""
Subject: Vendor Registration Rejected

Dear {company_name},

We could not approve your vendor registration
because the GSTIN already exists in our vendor
registry.

Please contact the procurement team for
further clarification.
"""

    issues = [
        check["message"]
        for check in checks
        if check["status"] in ["ISSUE", "REVIEW"]
    ]

    issue_text = "\n".join(
        f"- {issue}" for issue in issues
    )

    return f"""
Subject: Additional Information Required

Dear {company_name},

Your vendor registration requires additional
information or manual review.

The following items need attention:

{issue_text}

Please review these items and submit the
necessary corrections or documents.

Thank you.
"""


def process_vendor(vendor, uploaded_files):

    # Get previous vendor records for duplicate checking
    previous_runs = get_runs()

    existing_gstins = [
        run["gstin"]
        for run in previous_runs
        if run["gstin"] and run["decision"] == "APPROVED"
    ]

    # Live progress display
    progress = st.progress(0)
    stage_display = st.empty()

    def update_stage(number, title, description):

        progress.progress(number)

        stage_display.info(
            f"**{title}**\n\n{description}"
        )

    # STAGE 1: Submission
    update_stage(
        10,
        "Stage 1: Submission received",
        "Vendor information received successfully."
    )

    # STAGE 2: Document extraction
    update_stage(
        25,
        "Stage 2: Document extraction",
        "Reading uploaded PDF documents."
    )

    extraction_results = {}

    for document_name, uploaded_file in uploaded_files.items():

        if uploaded_file is not None:

            pdf_result = extract_text_from_pdf(
                uploaded_file.getvalue()
            )

            extraction_results[document_name] = pdf_result

        else:

            extraction_results[document_name] = {
                "success": False,
                "text": "",
                "page_count": 0,
                "message": "Document not uploaded."
            }

    # STAGE 3: Completeness
    update_stage(
        40,
        "Stage 3: Completeness check",
        "Checking mandatory vendor details and documents."
    )

    # STAGE 4: Validation
    update_stage(
        55,
        "Stage 4: Consistency checks",
        "Validating GSTIN, company details and bank information."
    )

    result = validate_vendor(
        vendor,
        existing_gstins
    )

    # Flag uploaded PDFs that could not be read
    for document_name, pdf_result in extraction_results.items():

        if (
            uploaded_files[document_name] is not None
            and not pdf_result["success"]
        ):

            result["checks"].append({
                "check": f"{document_name} extraction",
                "status": "REVIEW",
                "message": pdf_result["message"]
            })

    # STAGE 5: Duplicate detection
    update_stage(
        70,
        "Stage 5: Duplicate detection",
        "Comparing GSTIN against previous vendor records."
    )

    # STAGE 6: Decision
    update_stage(
        82,
        "Stage 6: Decision generation",
        "Generating the final onboarding decision."
    )

    if any(
        check["status"] == "DUPLICATE"
        for check in result["checks"]
    ):

        result["decision"] = "REJECTED"
        result["explanation"] = (
            "Duplicate GSTIN detected in the vendor registry."
        )

    elif any(
        check["status"] in ["ISSUE", "REVIEW"]
        for check in result["checks"]
    ):

        result["decision"] = "PENDING"
        result["explanation"] = (
            "Some requirements are incomplete or require manual review."
        )

    else:

        result["decision"] = "APPROVED"
        result["explanation"] = (
            "All configured onboarding checks passed."
        )

    # STAGE 7: Communication
    update_stage(
        92,
        "Stage 7: Communication generation",
        "Preparing the vendor communication."
    )

    result["communication"] = generate_communication(
        result["decision"],
        result["checks"],
        vendor["company_name"]
    )

    # STAGE 8: Save execution
    update_stage(
        97,
        "Stage 8: Saving execution",
        "Storing the result in the database."
    )

    run_id = save_run(vendor, result)

    progress.progress(100)

    stage_display.success(
        "All processing stages completed successfully!"
    )

    return run_id, result, extraction_results


# --------------------------------------------------
# 4. SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🏢 VendorFlow AI")
    st.caption("Intelligent Vendor Onboarding")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "New Submission",
            "Run History"
        ]
    )

    st.divider()

    st.caption("Vendor Verification System")
    st.caption("Version 1.0")


# --------------------------------------------------
# 5. LOAD DATABASE RECORDS
# --------------------------------------------------

runs = get_runs()

total_runs = len(runs)

approved_count = sum(
    1 for run in runs
    if run["decision"] == "APPROVED"
)

pending_count = sum(
    1 for run in runs
    if run["decision"] == "PENDING"
)

rejected_count = sum(
    1 for run in runs
    if run["decision"] == "REJECTED"
)


# --------------------------------------------------
# 6. OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.markdown(
        '<div class="app-heading">Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="app-subheading">'
        'Monitor vendor onboarding and verification activity.'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Runs", total_runs)
    col2.metric("Approved", approved_count)
    col3.metric("Pending", pending_count)
    col4.metric("Rejected", rejected_count)

    st.divider()

    st.subheader("Recent Activity")

    if runs:

        recent_data = []

        for run in runs[:10]:

            recent_data.append({
                "Run ID": run["id"],
                "Company": run["company_name"],
                "GSTIN": run["gstin"],
                "Decision": run["decision"],
                "Date": run["created_at"]
            })

        st.dataframe(
            pd.DataFrame(recent_data),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No vendor submissions yet. "
            "Go to New Submission to process your first vendor."
        )

    st.divider()

    st.subheader("Decision Distribution")

    if total_runs > 0:

        chart_data = pd.DataFrame({
            "Decision": [
                "Approved",
                "Pending",
                "Rejected"
            ],
            "Count": [
                approved_count,
                pending_count,
                rejected_count
            ]
        })

        st.bar_chart(
            chart_data,
            x="Decision",
            y="Count"
        )


# --------------------------------------------------
# 7. NEW SUBMISSION PAGE
# --------------------------------------------------

elif page == "New Submission":

    st.title("New Vendor Submission")

    st.caption(
        "Enter vendor information and upload the required documents."
    )

    with st.form("vendor_form"):

        st.subheader("Company Information")

        company_name = st.text_input(
            "Company Name *",
            placeholder="Acme Technologies Pvt Ltd"
        )

        gstin = st.text_input(
            "GSTIN *",
            placeholder="29ABCDE1234F1Z5"
        )

        st.subheader("Bank Information")

        bank_name = st.text_input(
            "Bank Account Holder Name *",
            placeholder="Acme Technologies Pvt Ltd"
        )

        st.divider()

        st.subheader("Required Documents")

        st.caption(
            "Upload PDF files. Text-based PDFs are supported "
            "in this version."
        )

        business_registration = st.file_uploader(
            "Business Registration Document *",
            type=["pdf"],
            key="business_registration"
        )

        gst_certificate = st.file_uploader(
            "GST Certificate *",
            type=["pdf"],
            key="gst_certificate"
        )

        bank_proof = st.file_uploader(
            "Bank Proof *",
            type=["pdf"],
            key="bank_proof"
        )

        st.divider()

        submitted = st.form_submit_button(
            "Process Vendor",
            type="primary",
            use_container_width=True
        )

    if submitted:

        if not company_name.strip():

            st.error("Please enter the company name.")

        elif not gstin.strip():

            st.error("Please enter the GSTIN.")

        elif not bank_name.strip():

            st.error("Please enter the bank account holder name.")

        else:

            vendor = {
                "company_name": company_name.strip(),
                "gstin": gstin.strip().upper(),
                "bank_account_holder": bank_name.strip(),

                "documents": {
                    "business_registration":
                        business_registration is not None,

                    "gst_certificate":
                        gst_certificate is not None,

                    "bank_proof":
                        bank_proof is not None
                }
            }

            uploaded_files = {
                "business_registration": business_registration,
                "gst_certificate": gst_certificate,
                "bank_proof": bank_proof
            }

            st.divider()

            run_id, result, extraction_results = process_vendor(
                vendor,
                uploaded_files
            )

            st.session_state["last_result"] = result
            st.session_state["last_run_id"] = run_id
            st.session_state["last_extraction"] = extraction_results

            st.subheader("Processing Result")

            if result["decision"] == "APPROVED":

                st.success("VENDOR APPROVED")

            elif result["decision"] == "PENDING":

                st.warning("VENDOR PENDING REVIEW")

            else:

                st.error("VENDOR REJECTED")

            st.markdown(
                f"**Run ID:** {run_id}"
            )

            st.markdown(
                f"**Reason:** {result['explanation']}"
            )

            st.subheader("Validation Report")

            st.dataframe(
                pd.DataFrame(result["checks"]),
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Document Extraction Results")

            for document_name, extraction in extraction_results.items():

                with st.expander(
                    document_name.replace("_", " ").title()
                ):

                    st.write(extraction["message"])

                    st.write(
                        f"Pages: {extraction['page_count']}"
                    )

                    if extraction["text"]:

                        st.text_area(
                            "Extracted Text",
                            extraction["text"],
                            height=150,
                            key=f"extracted_{run_id}_{document_name}"
                        )

            st.subheader("Vendor Communication")

            st.text_area(
                "Generated communication",
                result["communication"],
                height=220
            )


# --------------------------------------------------
# 8. RUN HISTORY PAGE
# --------------------------------------------------

elif page == "Run History":

    st.title("Run History")

    st.caption(
        "Review previously processed vendor submissions."
    )

    if runs:

        history_data = []

        for run in runs:

            history_data.append({
                "Run ID": run["id"],
                "Company": run["company_name"],
                "GSTIN": run["gstin"],
                "Decision": run["decision"],
                "Timestamp": run["created_at"]
            })

        st.dataframe(
            pd.DataFrame(history_data),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("View Run Details")

        selected_id = st.selectbox(
            "Select Run ID",
            [run["id"] for run in runs]
        )

        selected_run = next(
            run for run in runs
            if run["id"] == selected_id
        )

        st.markdown(
            f"### {selected_run['company_name']}"
        )

        st.write(
            f"**GSTIN:** {selected_run['gstin']}"
        )

        st.write(
            f"**Decision:** {selected_run['decision']}"
        )

        st.write(
            f"**Timestamp:** {selected_run['created_at']}"
        )

        st.write(
            f"**Explanation:** {selected_run['explanation']}"
        )

        st.subheader("Validation Details")

        st.dataframe(
            pd.DataFrame(selected_run["checks"]),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No previous vendor runs found.")
