
import sqlite3
import json
from pathlib import Path
from datetime import datetime


# Store the database inside the project's data folder
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "vendors.db"


def init_db(db_path=DEFAULT_DB_PATH):
    """Create the database and table if they don't exist."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS vendor_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            gstin TEXT,
            decision TEXT NOT NULL,
            explanation TEXT,
            checks_json TEXT,
            documents_json TEXT,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_run(vendor, result, db_path=DEFAULT_DB_PATH):
    """Save one vendor processing run."""

    init_db(db_path)

    connection = sqlite3.connect(db_path)

    cursor = connection.execute("""
        INSERT INTO vendor_runs (
            company_name,
            gstin,
            decision,
            explanation,
            checks_json,
            documents_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        vendor.get("company_name", ""),
        vendor.get("gstin", ""),
        result["decision"],
        result["explanation"],
        json.dumps(result["checks"]),
        json.dumps(vendor.get("documents", {})),
        datetime.now().astimezone().isoformat(timespec="seconds")
    ))

    run_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return run_id


def get_runs(db_path=DEFAULT_DB_PATH):
    """Retrieve all previous runs, newest first."""

    init_db(db_path)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT * FROM vendor_runs
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    runs = []

    for row in rows:
        run = dict(row)

        run["checks"] = json.loads(run.pop("checks_json") or "[]")
        run["documents"] = json.loads(
            run.pop("documents_json") or "{}"
        )

        runs.append(run)

    return runs
