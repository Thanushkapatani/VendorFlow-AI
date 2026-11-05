
# VendorFlow AI
### Automated Vendor Onboarding and Verification System

VendorFlow AI is a Python-based application designed to simplify vendor onboarding by automating document processing, information extraction, and vendor verification.

## Features

- **Document Upload:** Upload vendor documents in PDF format.
- **Text Extraction:** Extract relevant information from uploaded documents using PyPDF.
- **Vendor Validation:** Validate vendor details and identify inconsistencies.
- **Duplicate Detection:** Identify duplicate GSTIN entries.
- **Automated Decisions:** Classify vendor applications as Approved, Pending, or Rejected.
- **Database Management:** Store vendor information and verification history using SQLite.
- **Dashboard:** Monitor total submissions, approval status, pending applications, and rejected applications.
- **Run History:** View previously processed vendor applications.

## Tech Stack

- Python
- Streamlit
- Pandas
- PyPDF
- SQLite
- Pytest

## Project Structure

VendorFlow-AI/
│
├── app.py
├── database.py
├── requirements.txt
│
├── modules/
│   ├── __init__.py
│   ├── extraction.py
│   └── validation.py
│
├── tests/
│   ├── test_database.py
│   ├── test_extraction.py
│   └── test_validation.py
│
├── data/
│   └── vendors.db
│
├── sample_documents/
│
└── .gitignore

## Installation and Setup

### 1. Clone the repository

git clone https://github.com/Thanushkapatani/VendorFlow-AI.git

cd VendorFlow-AI

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the environment

Windows:

venv\Scripts\activate

### 4. Install dependencies

pip install -r requirements.txt

### 5. Run the application

python -m streamlit run app.py

The application will open in your browser at:

http://localhost:8501

## Running Tests

To run the automated test suite:

python -m pytest -v

## Testing

The project includes automated tests covering:

- Database operations
- PDF text extraction
- Vendor information validation

All 8 tests are currently passing.

## Author

Thanushka Patani

GitHub: https://github.com/Thanushkapatani
