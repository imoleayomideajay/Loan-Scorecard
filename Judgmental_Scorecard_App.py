# ================================
# PHASE 1 UPGRADE
# Premium UI + Dashboard + Risk Visualization
# Enterprise Credit Decisioning Platform
# ================================

# -------------------------------------------------------------------
# PROJECT STRUCTURE
# -------------------------------------------------------------------
"""
credit_decisioning_app/
│
├── app.py
├── config.py
├── requirements.txt
│
├── components/
│   ├── ui_cards.py
│   ├── charts.py
│   └── styles.py
│
├── pages/
│   ├── 1_Dashboard.py
│   └── 2_New_Application.py
│
├── services/
│   ├── rule_loader.py
│   ├── scorer.py
│   ├── validators.py
│   ├── explainability.py
│   └── repository.py
│
├── rules/
│   └── scorecard.yaml
│
├── data/
│   └── sample_scored_applications.csv
│
└── outputs/
    └── scored_applications.csv
"""

# -------------------------------------------------------------------
# requirements.txt
# -------------------------------------------------------------------
"""
streamlit>=1.40.0
pandas>=2.2.0
plotly>=5.24.0
pyyaml>=6.0.2
"""

# -------------------------------------------------------------------
# config.py
# -------------------------------------------------------------------
APP_NAME = "AB Microfinance Credit Decisioning Platform"
APP_VERSION = "1.1.0-phase1"
RULE_FILE = "rules/scorecard.yaml"
SCORED_APPLICATIONS_FILE = "outputs/scored_applications.csv"
SEED_DATA_FILE = "data/sample_scored_applications.csv"

DECISION_COLORS = {
    "Approve": "#0F9D58",
    "Refer": "#F4B400",
    "Decline": "#DB4437",
    "Override": "#7E57C2",
}

RISK_LABELS = {
    "Approve": "Low Risk",
    "Refer": "Medium Risk",
    "Decline": "High Risk",
}

# -------------------------------------------------------------------
# components/styles.py
# -------------------------------------------------------------------
import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            .main {
                background-color: #F6F8FB;
            }
            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }
            .app-title {
                font-size: 2rem;
                font-weight: 700;
                color: #0B1F33;
                margin-bottom: 0.25rem;
            }
            .app-subtitle {
                font-size: 0.98rem;
                color: #5B6B7A;
                margin-bottom: 1.25rem;
            }
            .kpi-card {
                background: white;
                border-radius: 18px;
                padding: 1rem 1rem 0.8rem 1rem;
                box-shadow: 0 2px 16px rgba(16, 24, 40, 0.06);
                border: 1px solid #E9EEF5;
            }
            .kpi-label {
                font-size: 0.85rem;
                color: #667085;
                margin-bottom: 0.2rem;
            }
            .kpi-value {
                font-size: 1.7rem;
                font-weight: 700;
                color: #101828;
            }
            .section-card {
                background: white;
                border-radius: 18px;
                padding: 1.15rem;
                box-shadow: 0 2px 16px rgba(16, 24, 40, 0.06);
                border: 1px solid #E9EEF5;
                margin-bottom: 1rem;
            }
            .decision-badge {
                display: inline-block;
                padding: 0.35rem 0.8rem;
                border-radius: 999px;
                font-size: 0.82rem;
                font-weight: 600;
                color: white;
            }
            .summary-card {
                background: linear-gradient(135deg, #0B1F33 0%, #163B65 100%);
                color: white;
                border-radius: 20px;
                padding: 1.25rem;
                box-shadow: 0 8px 24px rgba(11, 31, 51, 0.18);
            }
            .summary-title {
                font-size: 0.95rem;
                opacity: 0.9;
                margin-bottom: 0.4rem;
            }
            .summary-score {
                font-size: 2.2rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
            }
            .small-note {
                font-size: 0.82rem;
                color: #667085;
            }
            div[data-testid="stMetricValue"] {
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# components/ui_cards.py
# -------------------------------------------------------------------
import streamlit as st
from config import DECISION_COLORS


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="app-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str) -> None:
    st.markdown(
        f'''
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def decision_badge(decision: str) -> str:
    color = DECISION_COLORS.get(decision, "#475467")
    return f'<span class="decision-badge" style="background:{color};">{decision}</span>'


def result_summary_card(score: int, decision: str, risk_band: str, recommendation: str) -> None:
    st.markdown(
        f'''
        <div class="summary-card">
            <div class="summary-title">Credit Decision Summary</div>
            <div class="summary-score">{score}</div>
            <div style="margin-bottom:0.6rem;">{decision_badge(decision)}&nbsp;&nbsp;<span style="font-weight:600;">{risk_band}</span></div>
            <div style="font-size:0.95rem; line-height:1.5;">{recommendation}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# components/charts.py
# -------------------------------------------------------------------
import pandas as pd
import plotly.express as px
from config import DECISION_COLORS


def decision_donut(df: pd.DataFrame):
    plot_df = df["decision"].value_counts().reset_index()
    plot_df.columns = ["decision", "count"]
    fig = px.pie(
        plot_df,
        names="decision",
        values="count",
        hole=0.62,
        color="decision",
        color_discrete_map=DECISION_COLORS,
    )
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig


def score_histogram(df: pd.DataFrame):
    fig = px.histogram(df, x="total_score", nbins=15)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig


def employment_avg_score(df: pd.DataFrame):
    plot_df = (
        df.groupby("employment_type", as_index=False)["total_score"]
        .mean()
        .sort_values("total_score", ascending=False)
    )
    fig = px.bar(plot_df, x="employment_type", y="total_score")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig


def score_gauge(score: int, approve_cutoff: int, refer_cutoff: int):
    import plotly.graph_objects as go

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"font": {"size": 34}},
            gauge={
                "axis": {"range": [0, 120]},
                "bar": {"color": "#163B65"},
                "steps": [
                    {"range": [0, refer_cutoff], "color": "#FDECEC"},
                    {"range": [refer_cutoff, approve_cutoff], "color": "#FEF6DD"},
                    {"range": [approve_cutoff, 120], "color": "#E7F6EC"},
                ],
                "threshold": {
                    "line": {"color": "#101828", "width": 4},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
    return fig

# -------------------------------------------------------------------
# services/rule_loader.py
# -------------------------------------------------------------------
from __future__ import annotations
import yaml
from typing import Any, Dict


def load_rules(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    return rules

# -------------------------------------------------------------------
# services/validators.py
# -------------------------------------------------------------------
from typing import Dict, Any, List


def validate_application(data: Dict[str, Any]) -> List[str]:
    errors = []
    if not 18 <= data["age"] <= 75:
        errors.append("Age must be between 18 and 75.")
    if data["monthly_net_income"] < 0:
        errors.append("Monthly net income cannot be negative.")
    if not 0 <= data["existing_obligations_ratio"] <= 100:
        errors.append("Existing obligations ratio must be between 0 and 100.")
    if data["employment_tenure_months"] < 0:
        errors.append("Employment tenure cannot be negative.")
    if data["residence_stability_months"] < 0:
        errors.append("Residence stability cannot be negative.")
    if data["bank_account_vintage_months"] < 0:
        errors.append("Bank account vintage cannot be negative.")
    return errors

# -------------------------------------------------------------------
# services/scorer.py
# -------------------------------------------------------------------
from __future__ import annotations
from typing import Dict, Any, List


def score_band(value: float, rules: List[Dict[str, Any]]) -> int:
    for rule in rules:
        if rule["min"] <= value <= rule["max"]:
            return int(rule["points"])
    return 0


def evaluate_hard_rejects(data: Dict[str, Any], hard_rules: Dict[str, Any]) -> List[str]:
    reasons = []
    if data["bvn_verification"] == "Not verified":
        reasons.append(hard_rules["bvn_not_verified"])
    if data["bureau_flag"] == "Serious delinquency":
        reasons.append(hard_rules["serious_delinquency"])
    if data["existing_obligations_ratio"] > hard_rules["max_existing_obligations_ratio"]:
        reasons.append(f"Existing obligations ratio exceeds {hard_rules['max_existing_obligations_ratio']}% policy threshold.")
    return reasons


def compute_score(data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    hard_rejects = evaluate_hard_rejects(data, rules["hard_reject_rules"])

    component_scores = {
        "Age": score_band(data["age"], rules["score_variables"]["age"]),
        "Monthly net income": score_band(data["monthly_net_income"], rules["score_variables"]["monthly_net_income"]),
        "Employment type": rules["score_variables"]["employment_type"].get(data["employment_type"], 0),
        "Employment tenure": score_band(data["employment_tenure_months"], rules["score_variables"]["employment_tenure_months"]),
        "Residence stability": score_band(data["residence_stability_months"], rules["score_variables"]["residence_stability_months"]),
        "Bureau flag": rules["score_variables"]["bureau_flag"].get(data["bureau_flag"], 0),
        "Existing obligations ratio": score_band(data["existing_obligations_ratio"], rules["score_variables"]["existing_obligations_ratio"]),
        "Account turnover": rules["score_variables"]["account_turnover_strength"].get(data["account_turnover_strength"], 0),
        "Savings behaviour": rules["score_variables"]["savings_behaviour"].get(data["savings_behaviour"], 0),
        "BVN verification": rules["score_variables"]["bvn_verification"].get(data["bvn_verification"], 0),
        "Bank account vintage": score_band(data["bank_account_vintage_months"], rules["score_variables"]["bank_account_vintage_months"]),
    }

    total_score = int(sum(component_scores.values()))
    cutoffs = rules["decision_cutoffs"]

    if hard_rejects:
        decision = "Decline"
        risk_band = "High Risk"
    elif total_score >= cutoffs["approve"]:
        decision = "Approve"
        risk_band = "Low Risk"
    elif total_score >= cutoffs["refer"]:
        decision = "Refer"
        risk_band = "Medium Risk"
    else:
        decision = "Decline"
        risk_band = "High Risk"

    recommendation = build_recommendation(decision, hard_rejects)

    return {
        "component_scores": component_scores,
        "total_score": total_score,
        "decision": decision,
        "risk_band": risk_band,
        "reject_reasons": hard_rejects,
        "recommendation": recommendation,
    }


def build_recommendation(decision: str, reject_reasons: List[str]) -> str:
    if reject_reasons:
        return "Application failed one or more non-negotiable policy checks and should not proceed without exceptional governance approval."
    if decision == "Approve":
        return "Applicant meets policy expectations on affordability, stability, and behavioural indicators. Proceed to standard approval workflow."
    if decision == "Refer":
        return "Application is borderline and should be reviewed manually by a credit officer or committee before a final lending decision is made."
    return "Application score is below the policy cut-off and should be declined under current judgmental scorecard rules."

# -------------------------------------------------------------------
# services/explainability.py
# -------------------------------------------------------------------
from typing import Dict, List


def explain_result(component_scores: Dict[str, int], reject_reasons: List[str]) -> Dict[str, List[str]]:
    positive = [f"{k} contributed positively (+{v})" for k, v in component_scores.items() if v > 0]
    negative = [f"{k} reduced score ({v})" for k, v in component_scores.items() if v < 0]
    policy = reject_reasons if reject_reasons else ["No hard reject rule was triggered."]
    return {
        "positive_factors": positive,
        "negative_factors": negative,
        "policy_flags": policy,
    }

# -------------------------------------------------------------------
# services/repository.py
# -------------------------------------------------------------------
from __future__ import annotations
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any


def ensure_store(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        seed = pd.DataFrame(columns=[
            "application_id", "branch", "officer_name", "age", "monthly_net_income", "employment_type",
            "employment_tenure_months", "residence_stability_months", "bureau_flag", "existing_obligations_ratio",
            "account_turnover_strength", "savings_behaviour", "bvn_verification", "bank_account_vintage_months",
            "total_score", "decision", "risk_band", "reject_reasons", "timestamp"
        ])
        seed.to_csv(path, index=False)


def load_scored_applications(path: str) -> pd.DataFrame:
    ensure_store(path)
    return pd.read_csv(path)


def append_scored_application(path: str, row: Dict[str, Any]) -> None:
    ensure_store(path)
    row = row.copy()
    row["timestamp"] = datetime.now().isoformat(timespec="seconds")
    pd.DataFrame([row]).to_csv(path, mode="a", index=False, header=False)

# -------------------------------------------------------------------
# rules/scorecard.yaml
# -------------------------------------------------------------------
"""
metadata:
  scorecard_name: "Judgmental Retail Scorecard"
  version: "2026.03"
  effective_date: "2026-03-01"
  approved_by: "Head of Credit Risk"
  last_updated: "2026-03-20"

decision_cutoffs:
  approve: 85
  refer: 65

hard_reject_rules:
  max_existing_obligations_ratio: 60
  bvn_not_verified: "Applicant failed BVN verification."
  serious_delinquency: "Credit bureau shows serious delinquency."

score_variables:
  age:
    - {min: 18, max: 24, points: 4}
    - {min: 25, max: 35, points: 10}
    - {min: 36, max: 50, points: 14}
    - {min: 51, max: 75, points: 8}

  monthly_net_income:
    - {min: 0, max: 49999, points: 3}
    - {min: 50000, max: 99999, points: 8}
    - {min: 100000, max: 199999, points: 14}
    - {min: 200000, max: 99999999, points: 20}

  employment_type:
    Unemployed: 0
    Informal business: 6
    Self-employed formal: 10
    Private salaried: 14
    Government salaried: 18

  employment_tenure_months:
    - {min: 0, max: 5, points: 2}
    - {min: 6, max: 11, points: 5}
    - {min: 12, max: 23, points: 9}
    - {min: 24, max: 600, points: 14}

  residence_stability_months:
    - {min: 0, max: 5, points: 1}
    - {min: 6, max: 11, points: 4}
    - {min: 12, max: 23, points: 7}
    - {min: 24, max: 600, points: 10}

  bureau_flag:
    Clean: 18
    Minor issues: 8
    Serious delinquency: -20
    No bureau history: 5

  existing_obligations_ratio:
    - {min: 0, max: 20, points: 15}
    - {min: 21, max: 40, points: 8}
    - {min: 41, max: 60, points: 2}
    - {min: 61, max: 100, points: -10}

  account_turnover_strength:
    Low: 3
    Moderate: 8
    Strong: 14

  savings_behaviour:
    None observed: 0
    Irregular: 5
    Regular: 12

  bvn_verification:
    Verified and consistent: 10
    Verified with minor mismatch: 4
    Not verified: -15

  bank_account_vintage_months:
    - {min: 0, max: 5, points: 2}
    - {min: 6, max: 11, points: 5}
    - {min: 12, max: 23, points: 8}
    - {min: 24, max: 600, points: 12}
"""

# -------------------------------------------------------------------
# app.py
# -------------------------------------------------------------------
import streamlit as st
from components.styles import inject_global_styles
from components.ui_cards import page_header
from config import APP_NAME, APP_VERSION

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
page_header(APP_NAME, f"Internal credit decisioning workspace • Version {APP_VERSION}")

st.info("Use the left navigation to access the dashboard and application scoring workflow.")

# -------------------------------------------------------------------
# pages/1_Dashboard.py
# -------------------------------------------------------------------
import streamlit as st
import pandas as pd
from components.styles import inject_global_styles
from components.ui_cards import page_header, kpi_card, decision_badge
from components.charts import decision_donut, score_histogram, employment_avg_score
from services.repository import load_scored_applications
from config import SCORED_APPLICATIONS_FILE

st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")
inject_global_styles()
page_header("Portfolio Dashboard", "Executive summary of scored applications, decisions, and portfolio mix.")

df = load_scored_applications(SCORED_APPLICATIONS_FILE)

if df.empty:
    st.warning("No scored applications found yet. Score an application to populate the dashboard.")
else:
    total_apps = len(df)
    approvals = int((df["decision"] == "Approve").sum())
    referrals = int((df["decision"] == "Refer").sum())
    declines = int((df["decision"] == "Decline").sum())
    avg_score = round(df["total_score"].astype(float).mean(), 1)
    override_rate = "0.0%"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Applications", f"{total_apps:,}")
    with c2:
        kpi_card("Approvals", f"{approvals:,}")
    with c3:
        kpi_card("Referrals", f"{referrals:,}")
    with c4:
        kpi_card("Declines", f"{declines:,}")
    with c5:
        kpi_card("Override rate", override_rate)
    with c6:
        kpi_card("Average score", f"{avg_score}")

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Decision distribution")
        st.plotly_chart(decision_donut(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Score distribution")
        st.plotly_chart(score_histogram(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns([1, 1])
    with left2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Average score by employment type")
        st.plotly_chart(employment_avg_score(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Recent applications")
        show_cols = [
            "application_id", "branch", "officer_name", "employment_type", "total_score", "decision", "timestamp"
        ]
        recent_df = df.sort_values("timestamp", ascending=False).head(10)[show_cols].copy()
        recent_df["decision"] = recent_df["decision"].apply(lambda x: decision_badge(x))
        st.write(recent_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# pages/2_New_Application.py
# -------------------------------------------------------------------
import streamlit as st
import pandas as pd
from components.styles import inject_global_styles
from components.ui_cards import page_header, result_summary_card
from components.charts import score_gauge
from services.rule_loader import load_rules
from services.validators import validate_application
from services.scorer import compute_score
from services.explainability import explain_result
from services.repository import append_scored_application, load_scored_applications
from config import RULE_FILE, SCORED_APPLICATIONS_FILE

st.set_page_config(page_title="New Application", page_icon="🧾", layout="wide")
inject_global_styles()
page_header("New Application Scoring", "Capture applicant information, run policy checks, and generate an explainable judgmental credit decision.")

rules = load_rules(RULE_FILE)
score_vars = rules["score_variables"]
cutoffs = rules["decision_cutoffs"]

with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.caption("Workflow progress")
    st.progress(33, text="Phase 1: Application scoring and visual decision support")
    st.markdown('</div>', unsafe_allow_html=True)

with st.form("new_application_form"):
    tab1, tab2, tab3, tab4 = st.tabs([
        "Personal Details",
        "Income & Employment",
        "Credit Exposure",
        "Behaviour & Verification",
    ])

    with tab1:
        c1, c2, c3 = st.columns(3)
        application_id = c1.text_input("Application ID", value="APP-1001", help="Unique reference for the application.")
        branch = c2.text_input("Branch", value="Lagos Mainland", help="Originating branch or sales location.")
        officer_name = c3.text_input("Credit officer", value="A. Ajayi", help="Officer handling this case.")
        age = st.number_input("Age", min_value=18, max_value=75, value=31, help="Applicant age in completed years.")
        residence_stability_months = st.number_input(
            "Residence stability (months)", min_value=0, max_value=600, value=18,
            help="Number of months applicant has stayed at current residence."
        )

    with tab2:
        c1, c2 = st.columns(2)
        monthly_net_income = c1.number_input(
            "Monthly net income", min_value=0, value=150000, step=5000,
            help="Net monthly income available after statutory deductions."
        )
        employment_type = c2.selectbox(
            "Employment type", list(score_vars["employment_type"].keys()),
            help="Primary employment classification used in policy assessment."
        )
        employment_tenure_months = st.number_input(
            "Employment tenure (months)", min_value=0, max_value=600, value=24,
            help="Duration in current employment or business activity."
        )

    with tab3:
        c1, c2 = st.columns(2)
        bureau_flag = c1.selectbox(
            "Credit bureau flag", list(score_vars["bureau_flag"].keys()),
            help="Most severe current bureau interpretation under policy."
        )
        existing_obligations_ratio = c2.slider(
            "Existing obligations ratio (%)", min_value=0, max_value=100, value=25,
            help="Estimated debt service burden from current obligations."
        )

    with tab4:
        c1, c2, c3 = st.columns(3)
        account_turnover_strength = c1.selectbox(
            "Account turnover strength", list(score_vars["account_turnover_strength"].keys()),
            help="Qualitative assessment of banking inflow and activity strength."
        )
        savings_behaviour = c2.selectbox(
            "Savings behaviour", list(score_vars["savings_behaviour"].keys()),
            help="Observed consistency of savings pattern."
        )
        bvn_verification = c3.selectbox(
            "BVN verification", list(score_vars["bvn_verification"].keys()),
            help="Outcome of identity verification against BVN records."
        )
        bank_account_vintage_months = st.number_input(
            "Bank account vintage (months)", min_value=0, max_value=600, value=18,
            help="How long the primary operating bank account has been active."
        )

    notes = st.text_area("Credit officer notes", help="Optional underwriting context or observations.")
    submit = st.form_submit_button("Run scorecard")

if submit:
    application = {
        "application_id": application_id,
        "branch": branch,
        "officer_name": officer_name,
        "age": age,
        "monthly_net_income": monthly_net_income,
        "employment_type": employment_type,
        "employment_tenure_months": employment_tenure_months,
        "residence_stability_months": residence_stability_months,
        "bureau_flag": bureau_flag,
        "existing_obligations_ratio": existing_obligations_ratio,
        "account_turnover_strength": account_turnover_strength,
        "savings_behaviour": savings_behaviour,
        "bvn_verification": bvn_verification,
        "bank_account_vintage_months": bank_account_vintage_months,
        "notes": notes,
    }

    validation_errors = validate_application(application)
    if validation_errors:
        for err in validation_errors:
            st.error(err)
    else:
        existing = load_scored_applications(SCORED_APPLICATIONS_FILE)
        if not existing.empty and application_id in existing.get("application_id", pd.Series(dtype=str)).astype(str).tolist():
            st.warning("Duplicate application ID detected. Review whether this is a resubmission or a duplicate entry.")

        result = compute_score(application, rules)
        explanations = explain_result(result["component_scores"], result["reject_reasons"])

        append_scored_application(
            SCORED_APPLICATIONS_FILE,
            {
                **application,
                "total_score": result["total_score"],
                "decision": result["decision"],
                "risk_band": result["risk_band"],
                "reject_reasons": " | ".join(result["reject_reasons"]),
            },
        )

        left, right = st.columns([1.1, 0.9])
        with left:
            result_summary_card(
                result["total_score"],
                result["decision"],
                result["risk_band"],
                result["recommendation"],
            )
            st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Component score breakdown")
            breakdown_df = pd.DataFrame({
                "Component": list(result["component_scores"].keys()),
                "Points": list(result["component_scores"].values()),
            })
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Score visualization")
            st.plotly_chart(
                score_gauge(result["total_score"], cutoffs["approve"], cutoffs["refer"]),
                use_container_width=True,
            )
            st.markdown("<p class='small-note'>Green indicates approval zone, amber indicates referral zone, and red indicates decline zone.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Positive drivers")
            for item in explanations["positive_factors"]:
                st.write(f"• {item}")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Policy flags and constraints")
            for item in explanations["policy_flags"]:
                st.write(f"• {item}")
            if explanations["negative_factors"]:
                st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
                st.caption("Negative contributors")
                for item in explanations["negative_factors"]:
                    st.write(f"• {item}")
            st.markdown('</div>', unsafe_allow_html=True)

        if result["decision"] == "Approve":
            st.success("Application meets current policy threshold and may proceed to the next stage of approval workflow.")
        elif result["decision"] == "Refer":
            st.warning("Application requires manual review before final credit action is taken.")
        else:
            st.error("Application should be declined under the current policy unless an exceptional governance process applies.")

# -------------------------------------------------------------------
# data/sample_scored_applications.csv
# -------------------------------------------------------------------
"""
application_id,branch,officer_name,age,monthly_net_income,employment_type,employment_tenure_months,residence_stability_months,bureau_flag,existing_obligations_ratio,account_turnover_strength,savings_behaviour,bvn_verification,bank_account_vintage_months,total_score,decision,risk_band,reject_reasons,timestamp
APP-0901,Lagos Mainland,A. Ajayi,32,180000,Private salaried,28,24,Clean,22,Strong,Regular,Verified and consistent,30,104,Approve,Low Risk,,2026-03-25T09:12:00
APP-0902,Ibadan Central,M. Bello,24,70000,Informal business,8,10,Minor issues,35,Moderate,Irregular,Verified and consistent,12,58,Decline,High Risk,,2026-03-25T10:03:00
APP-0903,Abuja South,T. Okonkwo,41,220000,Government salaried,36,48,Clean,18,Strong,Regular,Verified and consistent,42,119,Approve,Low Risk,,2026-03-25T11:45:00
APP-0904,Kano Metro,R. Musa,29,95000,Self-employed formal,14,15,Serious delinquency,52,Moderate,Irregular,Verified and consistent,16,50,Decline,High Risk,Credit bureau shows serious delinquency.,2026-03-25T13:20:00
APP-0905,Port Harcourt,G. Uche,35,120000,Private salaried,18,20,No bureau history,28,Moderate,Regular,Verified with minor mismatch,20,81,Refer,Medium Risk,,2026-03-25T14:05:00
"""
