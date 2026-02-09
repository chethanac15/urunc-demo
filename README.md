# urunc CI Intelligence Suite

A practical CI monitoring tool built for the urunc project's LFX Mentorship (2026 Term 1). This isn't just another dashboard—it's designed to help maintainers actually understand what's breaking and why, without drowning in noise.

## Why This Exists

Most CI dashboards just show you red and green. This one tries to be smarter about it. If a test has been failing for 3 days straight, that's different from a flaky test that failed once. If a required job breaks, that's more urgent than an experimental feature. The goal is to surface what actually matters.

## What It Does

**Smart Alerts**  
Only notifies when something *changes* to a failure state. No spam from the same broken build.

**Failure Duration Tracking**  
Knows how long a job has been broken. "Failing for 3 days" hits different than "failed once."

**Job Categorization**  
Automatically groups jobs into REQUIRED (blockers), NIGHTLY, and EXPERIMENTAL based on their names and patterns.

**Latest PR Context**  
Shows which PR was merged most recently, so you can quickly connect the dots when something breaks.

**Slack Integration**  
Can send alerts to Slack when configured locally. Disabled by default for security.

## Architecture

Pretty straightforward pipeline:

```
GitHub API → collector.py → SQLite database
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              normalizer.py    notifier.py    dashboard.py
              (categorize)     (alert)        (visualize)
                    ↓               ↓               ↓
              export_report.py  Slack/Console  Streamlit UI
```

## Quick Start

### 1. Generate Demo Data
```bash
python mock_collector.py
```
This creates realistic test data including a chronic failure scenario to demonstrate the detection logic.

### 2. View the Dashboard
```bash
python -m streamlit run dashboard.py
```
Opens an interactive dashboard at `localhost:8501` with health metrics and job breakdowns.

### 3. Test Notifications
```bash
python notifier.py
```
Runs the alert logic and shows what would be sent to Slack (or actually sends if configured).

## Live Demo

A static snapshot is deployed at: **https://chethanac15.github.io/urunc-demo/**

> **Note:** The live demo is just a static HTML export. The actual system (GitHub API calls, database, Slack alerts) runs locally only. This keeps credentials secure and avoids unnecessary API rate limits.

## Slack Setup (Optional)

Slack notifications are off by default. To enable them locally:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/HERE"
```

If this isn't set, the notifier just prints to console. This is intentional—no credentials in the repo, no accidental alerts.

## Project Structure

```
├── collector.py        # Fetches workflow data from GitHub API
├── database.py         # SQLite persistence layer
├── normalizer.py       # Categorizes jobs and calculates stability
├── notifier.py         # Alert logic with state-change detection
├── dashboard.py        # Streamlit UI for interactive viewing
├── export_report.py    # Generates static HTML snapshot
├── mock_collector.py   # Creates demo data for testing
└── config.py           # Configuration (uses env vars for secrets)
```

## Design Philosophy

The core idea is "signal over noise." Maintainers are busy. They don't need 50 notifications about the same broken build. They need to know:

1. What just broke (state changes)
2. How long it's been broken (chronic vs flaky)
3. How urgent it is (required vs experimental)

Everything else is just clutter.

## For LFX Reviewers

This prototype demonstrates:
- Understanding of CI/CD workflows and GitHub Actions
- Practical approach to alert fatigue (a real problem in CNCF projects)
- Security-conscious design (no hardcoded credentials, local-first)
- Static deployment strategy (zero maintenance on GitHub Pages)

See also:
- **[PROPOSAL_DRAFT.md](./PROPOSAL_DRAFT.md)** - Full LFX application details
- **[MAINTAINER_GUIDE.md](./MAINTAINER_GUIDE.md)** - Walkthrough of the maintainer workflow

## Dependencies

```bash
pip install -r requirements.txt
```

Main libraries: `requests`, `pandas`, `streamlit`, `sqlite3` (built-in)

---

Built for the urunc project's LFX Mentorship 2026. Feedback welcome.
