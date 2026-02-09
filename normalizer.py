# normalizer.py

def get_intent_label(workflow_name):
    """Categorizes workflows into tiers based on maintainer priority."""
    name = workflow_name.lower()
    
    # 1. REQUIRED (Mission Critical)
    if any(x in name for x in ["unit-test", "lint", "build (amd64)"]):
        return "REQUIRED", "🛡️"
        
    # 2. NIGHTLY (Stability tracking)
    if "nightly" in name or "e2e" in name:
        return "NIGHTLY", "🌙"
        
    # 3. EXPERIMENTAL / OPTIONAL
    if any(x in name for x in ["arm64", "experimental", "bench"]):
        return "EXPERIMENTAL", "🧪"
        
    # Default
    return "CI", "⚙️"

def normalize_workflow_data(df):
    """Adds intent labels, standardizes columns, and derives health signals."""
    import pandas as pd
    
    if df.empty:
        return df
        
    # Tiered Categorization
    df['intent'], df['intent_icon'] = zip(*df['name'].apply(get_intent_label))
    
    # Column Consistency (Solving KeyErrors permanently)
    rename_map = {
        'head_branch': 'branch',
        'head_sha': 'commit_sha',
        'html_url': 'url'
    }
    for old, new in rename_map.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]
            
    # Success Rate (Last 10)
    # This is calculated per job_name
    return df
