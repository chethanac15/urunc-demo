# database.py
import sqlite3
import pandas as pd
from config import DB_PATH

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER UNIQUE,
                name TEXT,
                job_name TEXT,
                status TEXT,
                conclusion TEXT,
                created_at TEXT,
                updated_at TEXT,
                commit_sha TEXT,
                branch TEXT,
                url TEXT
            )
        ''')
        conn.commit()

def save_run(run_data):
    """Saves or updates a workflow run in the database."""
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO workflow_runs (
                run_id, name, job_name, status, conclusion, created_at, updated_at, commit_sha, branch, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                status=excluded.status,
                conclusion=excluded.conclusion,
                updated_at=excluded.updated_at
        ''', (
            run_data['id'],
            run_data['name'],
            run_data.get('job_name', run_data['name']),
            run_data['status'],
            run_data['conclusion'],
            run_data['created_at'],
            run_data['updated_at'],
            run_data.get('head_sha', ''),
            run_data.get('head_branch', ''),
            run_data['html_url']
        ))
        conn.commit()

def get_all_runs():
    """Fetches all runs as a pandas DataFrame for the dashboard."""
    with get_db_connection() as conn:
        query = "SELECT * FROM workflow_runs ORDER BY created_at DESC"
        return pd.read_sql_query(query, conn)

def get_recent_failures():
    """Fetches completed runs that failed and haven't been notified yet."""
    # This logic will be used by notifier.py
    with get_db_connection() as conn:
        query = "SELECT * FROM workflow_runs WHERE status='completed' AND conclusion='failure' ORDER BY created_at DESC"
        return conn.execute(query).fetchall()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
