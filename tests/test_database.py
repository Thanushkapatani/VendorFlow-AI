
from database import init_db, save_run, get_runs


def test_database_saves_and_retrieves_run(tmp_path):

    db_path = tmp_path / "test_vendors.db"

    vendor = {
        "company_name": "Acme Technologies Pvt Ltd",
        "gstin": "29ABCDE1234F1Z5",
        "documents": {
            "business_registration": True,
            "gst_certificate": True,
            "bank_proof": True
        }
    }

    result = {
        "decision": "APPROVED",
        "explanation": "All checks passed.",
        "checks": [
            {
                "check": "GSTIN",
                "status": "PASS",
                "message": "GSTIN format is valid."
            }
        ]
    }

    init_db(db_path)

    run_id = save_run(vendor, result, db_path)

    runs = get_runs(db_path)

    assert run_id == 1
    assert len(runs) == 1
    assert runs[0]["company_name"] == vendor["company_name"]
    assert runs[0]["decision"] == "APPROVED"
    assert runs[0]["checks"][0]["status"] == "PASS"


def test_empty_database_returns_no_runs(tmp_path):

    db_path = tmp_path / "empty.db"

    runs = get_runs(db_path)

    assert runs == []

