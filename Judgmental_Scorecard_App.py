# ================================
# ENTERPRISE CREDIT DECISIONING PLATFORM
# Modular Streamlit Architecture
# ================================

# -------------------------------
# FOLDER STRUCTURE
# -------------------------------

"""
credit_decisioning_app/
│
├── app.py
├── config.py
│
├── pages/
│   ├── dashboard.py
│   ├── new_application.py
│   ├── batch_scoring.py
│   ├── analytics.py
│   ├── admin_policy.py
│   ├── reporting.py
│
├── services/
│   ├── scorer.py
│   ├── rule_loader.py
│   ├── validators.py
│   ├── audit_logger.py
│   ├── override_service.py
│   ├── explainability.py
│
├── components/
│   ├── ui_cards.py
│   ├── charts.py
│
├── rules/
│   └── scorecard.yaml
│
├── data/
│   └── sample_applicants.csv
│
├── outputs/
│   ├── audit_log.csv
│   ├── override_log.csv
│
└── utils/
    └── helpers.py
"""

# ================================
# CONFIGURATION FILE
# ================================

# config.py

APP_NAME = "Enterprise Credit Decisioning System"
VERSION = "1.0"

DATA_PATH = "data/"
RULE_PATH = "rules/scorecard.yaml"
OUTPUT_PATH = "outputs/"


# ================================
# RULE LOADER
# ================================

# services/rule_loader.py

import yaml


def load_rules(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


# ================================
# VALIDATOR
# ================================

# services/validators.py


def validate_input(data):
    errors = []

    if data['age'] < 18:
        errors.append("Age below minimum")

    if data['monthly_income'] < 0:
        errors.append("Income cannot be negative")

    if not 0 <= data['obligation_ratio'] <= 100:
        errors.append("Obligation ratio invalid")

    return errors


# ================================
# SCORER ENGINE
# ================================

# services/scorer.py

def band_score(value, bands):
    for b in bands:
        if b['min'] <= value <= b['max']:
            return b['points']
    return 0


def compute_score(data, rules):
    score = 0
    breakdown = {}
    reject_reasons = []

    # Hard reject
    if data['bvn'] == "No":
        reject_reasons.append("BVN not verified")

    if data['bureau'] == "Bad":
        reject_reasons.append("Serious delinquency")

    # Score components
    breakdown['age'] = band_score(data['age'], rules['age'])
    breakdown['income'] = band_score(data['monthly_income'], rules['income'])
    breakdown['employment'] = rules['employment'].get(data['employment'], 0)

    score = sum(breakdown.values())

    # Decision
    if reject_reasons:
        decision = "Decline"
    elif score >= rules['cutoff']['approve']:
        decision = "Approve"
    elif score >= rules['cutoff']['refer']:
        decision = "Refer"
    else:
        decision = "Decline"

    return score, breakdown, decision, reject_reasons


# ================================
# AUDIT LOGGER
# ================================

# services/audit_logger.py

import pandas as pd
from datetime import datetime


def log_audit(record, path="outputs/audit_log.csv"):
    record['timestamp'] = datetime.now()
    df = pd.DataFrame([record])
    df.to_csv(path, mode='a', header=False, index=False)


# ================================
# STREAMLIT APP ENTRY
# ================================

# app.py

import streamlit as st
from services.rule_loader import load_rules
from services.scorer import compute_score
from services.validators import validate_input

rules = load_rules("rules/scorecard.yaml")

st.set_page_config(layout="wide")
st.title("Enterprise Credit Decisioning Platform")

menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "New Application",
    "Batch Scoring",
    "Analytics",
    "Admin",
    "Reports"
])


# ================================
# NEW APPLICATION PAGE
# ================================

if menu == "New Application":

    st.header("Loan Application Scoring")

    with st.form("application_form"):
        age = st.number_input("Age", 18, 100)
        income = st.number_input("Monthly Income")
        employment = st.selectbox("Employment", ["Salaried", "Self-employed", "Unemployed"])
        bureau = st.selectbox("Bureau", ["Good", "Bad"])
        bvn = st.selectbox("BVN Verified", ["Yes", "No"])
        obligation = st.slider("Obligation Ratio", 0, 100)

        submit = st.form_submit_button("Score")

    if submit:
        data = {
            'age': age,
            'monthly_income': income,
            'employment': employment,
            'bureau': bureau,
            'bvn': bvn,
            'obligation_ratio': obligation
        }

        errors = validate_input(data)

        if errors:
            st.error(errors)
        else:
            score, breakdown, decision, reject = compute_score(data, rules)

            st.metric("Score", score)
            st.metric("Decision", decision)

            if reject:
                st.error(reject)

            st.write("Breakdown", breakdown)


# ================================
# SAMPLE RULE FILE (YAML)
# ================================

"""
age:
  - {min: 18, max: 30, points: 5}
  - {min: 31, max: 50, points: 10}

income:
  - {min: 0, max: 50000, points: 5}
  - {min: 50001, max: 200000, points: 15}

employment:
  Salaried: 15
  Self-employed: 10
  Unemployed: 0

cutoff:
  approve: 25
  refer: 15
"""

# ================================
# DEPLOYMENT GUIDE
# ================================

"""
1. Install dependencies:
   pip install streamlit pandas pyyaml

2. Run app:
   streamlit run app.py

3. Deploy:
   - Streamlit Cloud (free)
   - Render / Railway
"""

# ================================
# ARCHITECTURE DECISIONS
# ================================

"""
- Separation of concerns: scoring, validation, UI separated
- External rule config for governance
- Audit logging for compliance
- Modular structure for scalability
"""

# ================================
# GOVERNANCE NOTES
# ================================

"""
- Every decision reproducible
- Policy version controlled
- Overrides logged
- Transparent scoring
"""

# ================================
# ROADMAP
# ================================

"""
1. Move to FastAPI backend
2. Add authentication
3. Integrate with core banking
4. Add ML scorecard
5. Real-time API scoring
"""
