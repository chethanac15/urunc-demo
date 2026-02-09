# dashboard.py
import streamlit as st
import pandas as pd
import json
import os
import time
from database import get_all_runs
from normalizer import normalize_workflow_data

# Set page config
st.set_page_config(page_title="urunc CI Maintainer Dashboard", layout="wide", page_icon="🛡️")

# V7 "The Chosen One" CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0d1117; color: #c9d1d9; }
    
    .main { background: radial-gradient(circle at top right, #1d2127, #0d1117); }

    /* Maintainer Banner */
    .maintainer-banner {
        background: rgba(248, 81, 73, 0.05); border: 2px solid rgba(248, 81, 73, 0.3);
        padding: 15px 25px; border-radius: 12px; margin-bottom: 30px;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    .pr-status-fail { color: #f85149; font-weight: 900; background: rgba(248, 81, 73, 0.1); padding: 5px 10px; border-radius: 6px; }

    .scorecard-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 30px; }
    .scorecard {
        flex: 1; padding: 25px; border-radius: 12px; background: #161b22;
        border: 1px solid #30363d; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center;
    }
    
    /* Tiered Styles */
    .tier-REQUIRED { border-left: 8px solid #f85149 !important; }
    .tier-NIGHTLY { border-left: 8px solid #58a6ff !important; }
    .tier-EXPERIMENTAL { border-left: 8px solid #8b949e !important; }
    
    .status-card {
        background: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;
        margin-bottom: 20px; transition: 0.3s;
    }
    .status-card:hover { transform: translateY(-5px); border-color: #58a6ff; }
    
    .history-text { font-family: monospace; letter-spacing: 2px; font-size: 0.9rem; }
    .job-name { font-size: 1.1rem; font-weight: 700; color: #adbac7; margin: 0; }
</style>
""", unsafe_allow_html=True)

# Data Normalization
raw_df = get_all_runs()
if raw_df.empty:
    st.warning("No data. Run mock_collector.py")
    st.stop()
df = normalize_workflow_data(raw_df)

# --- V7 Maintainer Context Banner ---
if os.path.exists("latest_pr.json"):
    with open("latest_pr.json", "r") as f: pr = json.load(f)
    result_cls = "pr-status-fail" if pr['ci_impact'] == "FAILURE" else "success-text"
    st.markdown(f"""
    <div class="maintainer-banner">
        <div>
            <span style="color: #8b949e; font-size: 0.8rem; text-transform: uppercase;">Latest Mainline Integration</span><br>
            <span style="font-size: 1.1rem; font-weight: 600;">PR #{pr['id']}: {pr['title']}</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #8b949e; font-size: 0.8rem;">CI Result</span><br>
            <span class="{result_cls}">{pr['ci_impact']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar / Mode Toggle ---
st.sidebar.title("🛠️ View Console")
view_type = st.sidebar.selectbox("Dashboard Style", ["Maintainer (Tiers)", "Classic (Table)"])

# Defensive multiselect defaults
options = sorted(df['intent'].unique().tolist())
default_selection = [v for v in ["REQUIRED", "NIGHTLY"] if v in options]
intent_filter = st.sidebar.multiselect("Active Tiers", options, default=default_selection)

filtered_df = df[df['intent'].isin(intent_filter)]

# --- Metrics ---
st.title("🛡️ urunc Maintainer Portal")
latest_jobs = df.sort_values('created_at').groupby('job_name').tail(1)
total = len(latest_jobs)
failing = (latest_jobs['conclusion'] == 'failure').sum()
crit_fail = (latest_jobs[(latest_jobs['conclusion'] == 'failure') & (latest_jobs['intent'] == 'REQUIRED')]).shape[0]

st.markdown(f"""
<div class="scorecard-container">
    <div class="scorecard"><h2>{total}</h2><p>Tracked Jobs</p></div>
    <div class="scorecard"><h2 style="color: #f85149;">{failing}</h2><p>Total Failures</p></div>
    <div class="scorecard"><h2 style="color: #f85149; font-weight: 900;">{crit_fail}</h2><p>Critical Blockers</p></div>
</div>
""", unsafe_allow_html=True)

# --- Multi-Mode UI ---
if view_type == "Maintainer (Tiers)":
    for tier in intent_filter:
        st.write(f"### {tier}")
        tier_df = filtered_df[filtered_df['intent'] == tier]
        job_names = tier_df['job_name'].unique()
        cols = st.columns(3)
        
        for i, jn in enumerate(job_names):
            j_data = df[df['job_name'] == jn]
            latest = j_data.iloc[0]
            last_5 = j_data.head(5)['conclusion'].tolist()
            
            # Failure duration logic for UI
            duration_msg = ""
            if latest['conclusion'] == 'failure':
                from datetime import datetime
                # Fetch duration from notifier logic if we wanted, let's just use first failure in streak
                fails = 0
                for c in j_data['conclusion']:
                    if c == 'failure': fails +=1
                    else: break
                if fails > 1: duration_msg = f"❗ Failed {fails} runs"
            
            with cols[i % 3]:
                st.markdown(f"""
                <div class="status-card tier-{tier}">
                    <p class="job-name">{jn}</p>
                    <p style="font-size: 0.8rem; margin: 10px 0; color: {'#3fb950' if latest['conclusion'] == 'success' else '#f85149'}">
                        <b>{latest['conclusion'].upper()}</b> {duration_msg}
                    </p>
                    <div class="history-text">
                        {" ".join(['✅' if x == 'success' else '❌' for x in last_5])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.table(latest_jobs[['job_name', 'intent', 'conclusion', 'branch', 'created_at']])

st.divider()
st.caption(f"Refreshed: {time.strftime('%H:%M:%S')} | Signal Intelligence Mode V7")
