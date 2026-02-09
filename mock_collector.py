# mock_collector.py
import random
import json
import os
from datetime import datetime, timedelta
from database import init_db, save_run

def generate_mock_data(count=150):
    """Generates elite data with REQUIRED/EXPERIMENTAL tiers and failing streaks."""
    print(f"Generating {count} mock workflow runs for The Chosen One (V7)...")
    
    # Categorized Workflows
    workflows = {
        "CI Integration": ["unit-test (amd64)", "lint", "unit-test (arm64)"],
        "Nightly Build": ["e2e (fedoras)", "integration-test"],
        "Experimental": ["benchmarks", "experimental-isolation"],
        "Release": ["build (amd64)", "build (arm64)"]
    }
    
    # 1. Maintainer Context (Latest PR + Result)
    pr_info = {
        "id": 457,
        "title": "feat: optimized hypercall path for urunc-vmm",
        "author": "ananos",
        "merged_at": (datetime.now() - timedelta(hours=4)).isoformat(),
        "url": "https://github.com/containers/urunc/pull/457",
        "ci_impact": "FAILURE" # Mentors care about this link!
    }
    with open("latest_pr.json", "w") as f:
        json.dump(pr_info, f)

    # 2. Runs with Streaks
    for wf, jobs in workflows.items():
        for job in jobs:
            # Determine if this job is currently in a failure streak
            # "unit-test (amd64)" should be failing for 3 days to show V7 power
            is_chronic = "unit-test (amd64)" in job
            
            for i in range(15):
                run_id = random.randint(1000000, 9000000)
                
                # i=0 is most recent. i=14 is oldest.
                # If chronic, last 10 runs are failures
                if is_chronic and i < 9:
                    conclusion = "failure"
                else:
                    # Success probability
                    prob = 0.9 if "REQUIRED" in job.upper() else 0.7
                    conclusion = "success" if random.random() < prob else "failure"
                
                # Timestamp: spaced by 8 hours
                created_at = (datetime.now() - timedelta(hours=i*8 + random.randint(0, 2))).isoformat()
                
                mock_run = {
                    "id": run_id,
                    "name": wf,
                    "job_name": job,
                    "status": "completed",
                    "conclusion": conclusion,
                    "created_at": created_at,
                    "updated_at": created_at,
                    "head_sha": f"sha{random.randint(1000, 9999)}",
                    "head_branch": "main" if i < 5 else "dev",
                    "html_url": f"https://github.com/containers/urunc/actions/runs/{run_id}"
                }
                save_run(mock_run)
        
    print("V7 'The Chosen One' data generation complete.")

if __name__ == "__main__":
    init_db()
    generate_mock_data()
