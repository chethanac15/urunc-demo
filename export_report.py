# export_report.py
import os
import json
import pandas as pd
from database import get_all_runs
from normalizer import normalize_workflow_data
from datetime import datetime

REPORT_DIR = "dist"
REPORT_FILE = os.path.join(REPORT_DIR, "index.html")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>urunc CI Ultimate Report</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 40px; }}
        .pr-banner {{ border: 1px solid #58a6ff; padding: 10px; border-radius: 8px; margin-bottom: 20px; color: #58a6ff; }}
        .score {{ font-size: 2.5rem; font-weight: 800; color: #adbac7; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
        th {{ text-align: left; color: #8b949e; padding: 10px; border-bottom: 2px solid #30363d; }}
        td {{ padding: 10px; border-bottom: 1px solid #21262d; }}
        .pass {{ color: #3fb950; font-weight: bold; }}
        .fail {{ color: #f85149; font-weight: bold; }}
    </style>
</head>
<body>
    <div style="background:#1f6feb;color:white;padding:12px;text-align:center;margin-bottom:16px;border-radius:6px;">
        <strong>📸 Static Demo Snapshot (GitHub Pages)</strong><br>
        Generated locally from the urunc CI Intelligence Suite.<br>
        Live GitHub API access and Slack notifications run locally only.
    </div>
    <h1>📋 urunc CI Ultimate Dashboard</h1>
    {pr_html}
    
    <div style="display: flex; gap: 40px;">
        <div><div class="score">{total}</div><p>Total Jobs</p></div>
        <div><div class="score" style="color: #3fb950;">{passed}</div><p>Passing</p></div>
        <div><div class="score" style="color: #58a6ff;">{rate}%</div><p>Health Score</p></div>
    </div>

    <table>
        <tr><th>Job Name</th><th>Intent</th><th>Stability</th><th>Latest</th></tr>
        {table_rows}
    </table>

    <p style="margin-top: 40px; color: #8b949e; text-align: center;">Generated on {gen_time} | CNCF urunc LFX Prototype</p>
</body>
</html>
"""

def generate():
    raw_df = get_all_runs()
    if raw_df.empty: return
    df = normalize_workflow_data(raw_df)
    
    pr_html = ""
    if os.path.exists("latest_pr.json"):
        with open("latest_pr.json", "r") as f: pr = json.load(f)
        pr_html = f'<div class="pr-banner">Latest Merged PR: <b>{pr["title"]}</b> by @{pr["author"]}</div>'

    latest_jobs = df.sort_values('created_at').groupby('job_name').tail(1)
    rows = ""
    for _, row in latest_jobs.iterrows():
        job_data = df[df['job_name'] == row['job_name']]
        rate = int((job_data.head(10)['conclusion'] == 'success').sum() / len(job_data.head(10)) * 100)
        cls = "pass" if row['conclusion'] == 'success' else "fail"
        rows += f"""
        <tr>
            <td>{row['job_name']}</td>
            <td><span style="font-size: 0.7rem; color: #8b949e;">{row['intent']}</span></td>
            <td>{rate}%</td>
            <td class="{cls}">{row['conclusion'].upper()}</td>
        </tr>"""

    full_html = HTML_TEMPLATE.format(
        gen_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        pr_html=pr_html, total=len(latest_jobs), 
        passed=(latest_jobs['conclusion'] == 'success').sum(),
        rate=int(((latest_jobs['conclusion'] == 'success').sum()/len(latest_jobs))*100),
        table_rows=rows
    )
    
    if not os.path.exists(REPORT_DIR): os.makedirs(REPORT_DIR)
    with open(REPORT_FILE, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"Ultimate report exported to {REPORT_FILE}")

if __name__ == "__main__":
    generate()
