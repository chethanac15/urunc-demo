# notifier.py
import json
import os
import requests
from database import get_db_connection
from config import SLACK_WEBHOOK_URL
from datetime import datetime

# Path to store the last notified run IDs to avoid spamming (Alert Fatigue Prevention)
LAST_NOTIFIED_JSON = "last_notified_state.json"

def load_notification_state():
    if os.path.exists(LAST_NOTIFIED_JSON):
        with open(LAST_NOTIFIED_JSON, "r") as f:
            return json.load(f)
    return {}

def save_notification_state(state):
    with open(LAST_NOTIFIED_JSON, "w") as f:
        json.dump(state, f)

class NotificationPlugin:
    def notify(self, alert_type, workflow, job, run_id, branch, url, duration_str=""):
        pass

class ConsoleNotifier(NotificationPlugin):
    def notify(self, alert_type, workflow, job, run_id, branch, url, duration_str=""):
        duration_info = f" | {duration_str}" if duration_str else ""
        print(f"\n📢 [{alert_type}] {workflow} / {job}{duration_info}")
        print(f"   Branch: {branch} | Run: {run_id}")
        print(f"   URL: {url}")

class SlackRealNotifier(NotificationPlugin):
    def notify(self, alert_type, workflow, job, run_id, branch, url, duration_str=""):
        if not SLACK_WEBHOOK_URL:
            print("⚠️ SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
            return
        
        # Alerts are sent only on failure transitions or critical priorities to avoid alert fatigue
        emoji = "🚨" if "REQUIRED" in alert_type or "HARD" in alert_type else "⚠️"
        duration_msg = f"\n*Duration:* {duration_str}" if duration_str else ""
        
        payload = {
            "text": f"{emoji} *CI Alert: {alert_type}*\n*Job:* {job}\n*Workflow:* {workflow}\n*Branch:* {branch}{duration_msg}\n<{url}|View Run Details>"
        }
        
        try:
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Slack alert sent for {job}")
            else:
                print(f"❌ Slack notification failed: {response.text}")
        except Exception as e:
            print(f"❌ Slack error: {e}")

def get_failure_duration(job_name):
    """Calculates how long a job has been failing in the current streak."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT created_at, conclusion FROM workflow_runs WHERE job_name=? ORDER BY created_at DESC", 
            (job_name,)
        )
        runs = cursor.fetchall()
        
        failure_start = None
        for run in runs:
            if run['conclusion'] == 'failure':
                failure_start = run['created_at']
            elif run['conclusion'] == 'success':
                break
                
        if failure_start:
            start_dt = datetime.fromisoformat(failure_start)
            now = datetime.now()
            diff = now - start_dt
            if diff.days > 0: return f"Failing for {diff.days} days"
            return f"Failing for {int(diff.seconds // 3600)} hours"
    return ""

def run_notifier():
    print("Checking for CI Regressions (V8 Production Slack)...")
    notifiers = [ConsoleNotifier(), SlackRealNotifier()]
    
    # Load previously notified state to avoid duplicate alerts (Maintainer Empathy)
    notified_state = load_notification_state()
    new_state = dict(notified_state)
    
    with get_db_connection() as conn:
        latest_runs = conn.execute("SELECT * FROM workflow_runs ORDER BY created_at DESC LIMIT 50").fetchall()
        
    for run in latest_runs:
        job_name = run['job_name']
        run_id = str(run['run_id'])
        
        # Only notify if this is a failure AND we haven't already notified for this specific run_id
        if run['conclusion'] == 'failure' and notified_state.get(job_name) != run_id:
            duration = get_failure_duration(job_name)
            
            # Priority logic
            is_required = any(x in job_name.lower() for x in ["unit-test", "lint", "build (amd64)"])
            alert_type = "REQUIRED JOB FAILURE" if is_required else "CI FAILURE"
            
            for n in notifiers:
                n.notify(alert_type, run['name'], job_name, run['run_id'], run['branch'], run['url'], duration)
            
            # Update state to prevent re-notifying for this run
            new_state[job_name] = run_id
            
    save_notification_state(new_state)

if __name__ == "__main__":
    run_notifier()
