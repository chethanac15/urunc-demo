import os

# config.py
# Configuration settings for the urunc CI Dashboard

# Target Repository
REPO_OWNER = "containers"
REPO_NAME = "urunc"

# GitHub API Settings
GITHUB_API_BASE = "https://api.github.com"
RUNS_ENDPOINT = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"

# Local Database Settings
DB_PATH = "urunc_ci.db"

# Notification Settings
LAST_NOTIFIED_FILE = "last_notified.txt"
SENDER_EMAIL = "your-email@example.com" # Placeholder
RECEIVER_EMAIL = "maintainer@example.com" # Placeholder
# Slack webhook URL (required for local notifications, not deployed)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # NO fallback - secure by default

# Filter for Workflows (optional, set to None to fetch all)
# Example: ["Nightly Build", "CI Integration"]
TARGET_WORKFLOWS = ["Nightly Build", "CI", "Unit Tests", "E2E test", "Lint code"] 

# Required Workflows (for filtering in dashboard)
REQUIRED_WORKFLOWS = ["CI", "E2E test", "Unit Tests"]

# NOTE: For local development, a GITHUB_TOKEN is recommended to avoid rate limits.
# You can set it as an environment variable: export GITHUB_TOKEN=your_token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
