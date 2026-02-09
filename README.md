# 🛡️ urunc CI Intelligence Suite (Maintainer-First)

This project is a high-fidelity, "Mentor-Ready" prototype designed for the `urunc` LFX Mentorship (2026 Term 1). While other dashboards focus purely on visualization, this suite is engineered around **Maintainer Empathy**—delivering signal, reducing noise, and tracking stability over time.

## 🌟 Elite Features (V8)
- **Production Slack Integration**: Real-time alerts delivered to `#ci-alerts` in the `urunc-dem0` workspace.
- **State-Change Intelligence**: Only notifies on *transitions* to failure, definitively solving the alert fatigue problem.
- **Triage-Aware Categorization**: Automatically groups signals into `REQUIRED` (Blockers), `NIGHTLY`, and `EXPERIMENTAL`.
- **Chronic Failure Tracking**: Detects how long a job has been broken (e.g., "Failing for 3 days").
- **Latest Merged PR context**: Explicitly links the most recent integration to the current CI result.

## 🧠 Philosophy: Built for Signal, Not Noise
Mentors in the CNCF space are often overwhelmed by "Alert Fatigue." This suite is designed to be **empathetic**:
- **It knows history**: It tracks how many *consecutive* runs a job has failed.
- **It knows prioritization**: `REQUIRED` jobs (unit tests, linting) are treated as blockers; `EXPERIMENTAL` jobs are treated as signals.
- **It knows simplicity**: There is no "backend" to manage. It's a series of scripts and a static export.

## 🏗️ Architecture
The suite is designed with clear separation of concerns (Data Collection -> Signal Normalization -> Notification Plugins -> UI Presentation).

```text
[ GitHub API ] -> [ collector.py ] -> [ SQLite / JSON ]
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
 [ normalizer.py ]                 [ notifier.py ]                  [ dashboard.py ]
(Signals & Tiers)                 (Slack/GH Plugins)               (Elite Streamlit UI)
        |                                 |                                 |
 [ export_report.py ]             [ Real-time Alerts ]              [ Static dist/ ]
```

## 🚀 Final Hands-on (Demo Instructions)

### 1. Initialize Elite Data
```bash
python mock_collector.py
```
*Note: This generates "The Chosen One" data, including a chronic 3-day failure in the REQUIRED `unit-test (amd64)` job to showcase signal detection.*

### 2. Run the Intelligence Console
```bash
python -m streamlit run dashboard.py
```
- **Maintainer View**: Uses tiers and blocker counts.
- **Kata-Style View**: A tabular mode requested by urunc maintainers.

### 3. Check Notifier Output
```bash
python notifier.py
```
*Watch the console (or Slack if configured) report failure durations and priority levels.*

## 🌐 Deployment

A static snapshot of the CI Intelligence Dashboard is deployed via GitHub Pages:

**Live Demo:** https://chethanac15.github.io/urunc-demo/

> **Note**  
> The live system (GitHub API access, SQLite persistence, and Slack notifications) runs **locally only** and is intentionally not deployed to avoid credential exposure and alert noise. The GitHub Pages deployment is a **static snapshot** for evaluation purposes.

### Slack Notifications (Optional)

Slack alerts are disabled by default.

To enable locally:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

If the variable is not set, alerts are skipped by design. This follows a zero-trust, secure-by-default model.

## 📂 Key Mentee Resources
- **[PROPOSAL_DRAFT.md](./PROPOSAL_DRAFT.md)**: A ready-to-use LFX application blueprint mapping this implementation to CNCF goals.
- **[MAINTAINER_GUIDE.md](./MAINTAINER_GUIDE.md)**: A walkthrough of the maintainer's decision loop using this tool.

---
*Built with maintainer empathy by [Your Name] for LFX 2026.*
