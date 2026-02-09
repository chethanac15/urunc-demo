# collector.py
import requests
import os
from config import RUNS_ENDPOINT, GITHUB_TOKEN, TARGET_WORKFLOWS
from database import init_db, save_run

def fetch_workflow_runs():
    """Fetches latest workflow runs from GitHub Actions API."""
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    print(f"Fetching runs from {RUNS_ENDPOINT}...")
    try:
        response = requests.get(RUNS_ENDPOINT, headers=headers, params={"per_page": 50})
        response.raise_for_status()
        data = response.json()
        
        runs = data.get("workflow_runs", [])
        print(f"Found {len(runs)} runs.")
        
        for run in runs:
            # Filter by workflow name if specified in config
            if TARGET_WORKFLOWS and run["name"] not in TARGET_WORKFLOWS:
                continue
            
            save_run(run)
            print(f"Saved run {run['id']} ({run['name']}): {run['conclusion']}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub: {e}")
        if response.status_code == 403:
            print("Tip: You might be rate-limited. Set a GITHUB_TOKEN in config.py or environment.")

if __name__ == "__main__":
    init_db()
    fetch_workflow_runs()
