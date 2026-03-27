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

# -------------------------------------------------------------------
# DEPLOYMENT GUIDE
# -------------------------------------------------------------------
"""
1. Create the folder structure exactly as shown above.
2. Save each section into its corresponding file.
3. Install dependencies:
   pip install -r requirements.txt
4. Start the application:
   streamlit run app.py
5. Streamlit will automatically detect the pages/ directory and build multi-page navigation.

Recommended hosting:
- Streamlit Community Cloud for early internal demos
- Render, Azure App Service, or an internal VM for controlled institutional deployment
"""

# -------------------------------------------------------------------
# MAINTENANCE GUIDE
# -------------------------------------------------------------------
"""
1. Policy changes should be made in rules/scorecard.yaml, not in UI files.
2. Validate all scorecard edits in a test environment before production use.
3. Back up outputs/scored_applications.csv regularly or replace it with a database in later phases.
4. Review cut-offs and hard reject rules periodically against realised repayment performance.
5. Add authentication, override logging, and audit trail controls in the next build phases.
"""

# -------------------------------------------------------------------
# PHASE 1 ARCHITECTURE DECISIONS
# -------------------------------------------------------------------
"""
1. Multi-page Streamlit layout was chosen because it gives immediate product structure without forcing a monolithic file design.
2. Score rules were externalised into YAML to support policy governance and future version control.
3. The scoring engine, validators, explainability logic, and repository layer were separated to improve maintainability and later API portability.
4. Plotly was used for premium interactive visuals, particularly the score gauge and dashboard charts.
5. A lightweight CSV repository was retained for Phase 1 simplicity, but isolated behind repository functions so it can later be replaced by SQL with minimal disruption.
"""

# -------------------------------------------------------------------
# PHASE 1 RISK AND GOVERNANCE CONSIDERATIONS
# -------------------------------------------------------------------
"""
1. This remains a judgmental scorecard and therefore requires formal policy approval before operational use.
2. The current persistence layer is appropriate for prototyping and controlled internal demonstration, not full production governance.
3. Duplicate application handling is currently a warning only; later phases should implement stronger entity resolution and case management.
4. No user authentication or role-based access control is included yet; that must be added before production deployment.
5. Override workflows and immutable audit trails are not yet complete and are planned for later phases.
"""

# ================================
# PHASE 2 UPGRADE
# Batch Scoring + Validation + Exception Reporting
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
│   ├── 2_New_Application.py
│   └── 3_Batch_Scoring.py
│
├── services/
│   ├── rule_loader.py
│   ├── scorer.py
│   ├── validators.py
│   ├── explainability.py
│   ├── repository.py
│   └── batch_processor.py
│
├── rules/
│   └── scorecard.yaml
│
├── data/
│   ├── sample_scored_applications.csv
│   └── sample_batch_applications.csv
│
└── outputs/
    ├── scored_applications.csv
    ├── batch_scored_output.csv
    └── batch_exceptions_output.csv
"""

# -------------------------------------------------------------------
# config.py (additions)
# -------------------------------------------------------------------
BATCH_SCORED_OUTPUT_FILE = "outputs/batch_scored_output.csv"
BATCH_EXCEPTION_OUTPUT_FILE = "outputs/batch_exceptions_output.csv"

REQUIRED_BATCH_COLUMNS = [
    "application_id",
    "branch",
    "officer_name",
    "age",
    "monthly_net_income",
    "employment_type",
    "employment_tenure_months",
    "residence_stability_months",
    "bureau_flag",
    "existing_obligations_ratio",
    "account_turnover_strength",
    "savings_behaviour",
    "bvn_verification",
    "bank_account_vintage_months",
]

# -------------------------------------------------------------------
# services/validators.py (additions)
# -------------------------------------------------------------------
from typing import Dict, Any, List
import pandas as pd


def validate_batch_schema(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        return [f"Missing required columns: {', '.join(missing)}"]
    return []


def validate_categorical_values(data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    errors = []
    sv = rules["score_variables"]

    categorical_checks = {
        "employment_type": list(sv["employment_type"].keys()),
        "bureau_flag": list(sv["bureau_flag"].keys()),
        "account_turnover_strength": list(sv["account_turnover_strength"].keys()),
        "savings_behaviour": list(sv["savings_behaviour"].keys()),
        "bvn_verification": list(sv["bvn_verification"].keys()),
    }

    for field, valid_values in categorical_checks.items():
        if data.get(field) not in valid_values:
            errors.append(f"{field} has invalid value: {data.get(field)}")

    return errors

# -------------------------------------------------------------------
# services/repository.py (additions)
# -------------------------------------------------------------------

def write_dataframe(path: str, df: pd.DataFrame) -> None:
    ensure_store(path)
    df.to_csv(path, index=False)

# -------------------------------------------------------------------
# services/batch_processor.py
# -------------------------------------------------------------------
import pandas as pd
from typing import Dict, Any, Tuple, List
from services.validators import validate_application, validate_batch_schema, validate_categorical_values
from services.scorer import compute_score


def process_batch(df: pd.DataFrame, rules: Dict[str, Any], required_columns: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    schema_errors = validate_batch_schema(df, required_columns)
    if schema_errors:
        raise ValueError(" | ".join(schema_errors))

    scored_rows: List[Dict[str, Any]] = []
    exception_rows: List[Dict[str, Any]] = []
    seen_ids = set()

    for idx, row in df.iterrows():
        record = row.to_dict()
        row_num = idx + 2
        app_id = str(record.get("application_id", "")).strip()

        row_errors = []
        if not app_id:
            row_errors.append("application_id is missing")
        if app_id in seen_ids:
            row_errors.append("duplicate application_id within upload")
        seen_ids.add(app_id)

        row_errors.extend(validate_application(record))
        row_errors.extend(validate_categorical_values(record, rules))

        if row_errors:
            exception_rows.append({
                **record,
                "row_number": row_num,
                "error_type": "validation_error",
                "error_details": " | ".join(row_errors),
            })
            continue

        result = compute_score(record, rules)
        scored_rows.append({
            **record,
            "row_number": row_num,
            "total_score": result["total_score"],
            "decision": result["decision"],
            "risk_band": result["risk_band"],
            "reject_reasons": " | ".join(result["reject_reasons"]),
            "recommendation": result["recommendation"],
        })

    scored_df = pd.DataFrame(scored_rows)
    exceptions_df = pd.DataFrame(exception_rows)

    summary = {
        "rows_uploaded": len(df),
        "rows_scored": len(scored_df),
        "rows_failed": len(exceptions_df),
        "approvals": int((scored_df["decision"] == "Approve").sum()) if not scored_df.empty else 0,
        "referrals": int((scored_df["decision"] == "Refer").sum()) if not scored_df.empty else 0,
        "declines": int((scored_df["decision"] == "Decline").sum()) if not scored_df.empty else 0,
        "average_score": round(scored_df["total_score"].mean(), 1) if not scored_df.empty else 0,
    }

    return scored_df, exceptions_df, summary

# -------------------------------------------------------------------
# pages/3_Batch_Scoring.py
# -------------------------------------------------------------------
import io
import pandas as pd
import streamlit as st
from components.styles import inject_global_styles
from components.ui_cards import page_header, kpi_card
from components.charts import decision_donut, score_histogram
from services.rule_loader import load_rules
from services.batch_processor import process_batch
from services.repository import write_dataframe, append_scored_application, load_scored_applications
from config import (
    RULE_FILE,
    REQUIRED_BATCH_COLUMNS,
    BATCH_SCORED_OUTPUT_FILE,
    BATCH_EXCEPTION_OUTPUT_FILE,
    SCORED_APPLICATIONS_FILE,
)

st.set_page_config(page_title="Batch Scoring", page_icon="📂", layout="wide")
inject_global_styles()
page_header(
    "Batch Scoring",
    "Upload multiple loan applications, validate the dataset, score valid rows, and produce exception reports for failed records.",
)

rules = load_rules(RULE_FILE)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Upload input file")
st.write("Supported formats: CSV and Excel (.xlsx). The file must contain all mandatory scorecard columns.")
uploaded_file = st.file_uploader("Select batch file", type=["csv", "xlsx"])
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("View required input schema", expanded=False):
    schema_df = pd.DataFrame({"required_column": REQUIRED_BATCH_COLUMNS})
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            batch_df = pd.read_csv(uploaded_file)
        else:
            batch_df = pd.read_excel(uploaded_file)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Uploaded data preview")
        st.dataframe(batch_df.head(10), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Run batch scoring", type="primary"):
            scored_df, exceptions_df, summary = process_batch(batch_df, rules, REQUIRED_BATCH_COLUMNS)

            write_dataframe(BATCH_SCORED_OUTPUT_FILE, scored_df)
            write_dataframe(BATCH_EXCEPTION_OUTPUT_FILE, exceptions_df)

            if not scored_df.empty:
                for _, r in scored_df.iterrows():
                    existing_store = load_scored_applications(SCORED_APPLICATIONS_FILE)
                    existing_ids = set(existing_store["application_id"].astype(str).tolist()) if not existing_store.empty else set()
                    if str(r["application_id"]) not in existing_ids:
                        append_scored_application(
                            SCORED_APPLICATIONS_FILE,
                            {
                                "application_id": r["application_id"],
                                "branch": r["branch"],
                                "officer_name": r["officer_name"],
                                "age": r["age"],
                                "monthly_net_income": r["monthly_net_income"],
                                "employment_type": r["employment_type"],
                                "employment_tenure_months": r["employment_tenure_months"],
                                "residence_stability_months": r["residence_stability_months"],
                                "bureau_flag": r["bureau_flag"],
                                "existing_obligations_ratio": r["existing_obligations_ratio"],
                                "account_turnover_strength": r["account_turnover_strength"],
                                "savings_behaviour": r["savings_behaviour"],
                                "bvn_verification": r["bvn_verification"],
                                "bank_account_vintage_months": r["bank_account_vintage_months"],
                                "notes": "Batch upload",
                                "total_score": r["total_score"],
                                "decision": r["decision"],
                                "risk_band": r["risk_band"],
                                "reject_reasons": r["reject_reasons"],
                            },
                        )

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                kpi_card("Rows uploaded", f"{summary['rows_uploaded']:,}")
            with c2:
                kpi_card("Rows scored", f"{summary['rows_scored']:,}")
            with c3:
                kpi_card("Rows failed", f"{summary['rows_failed']:,}")
            with c4:
                kpi_card("Approvals", f"{summary['approvals']:,}")
            with c5:
                kpi_card("Referrals", f"{summary['referrals']:,}")
            with c6:
                kpi_card("Average score", f"{summary['average_score']}")

            if not scored_df.empty:
                left, right = st.columns(2)
                with left:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.subheader("Batch decision distribution")
                    st.plotly_chart(decision_donut(scored_df), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with right:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.subheader("Batch score distribution")
                    st.plotly_chart(score_histogram(scored_df), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Scored output")
            if scored_df.empty:
                st.info("No valid rows were available for scoring.")
            else:
                st.dataframe(scored_df, use_container_width=True)
                st.download_button(
                    label="Download scored output CSV",
                    data=scored_df.to_csv(index=False).encode("utf-8"),
                    file_name="batch_scored_output.csv",
                    mime="text/csv",
                )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Exception report")
            if exceptions_df.empty:
                st.success("No row-level exceptions were detected.")
            else:
                st.dataframe(exceptions_df, use_container_width=True)
                st.download_button(
                    label="Download exception report CSV",
                    data=exceptions_df.to_csv(index=False).encode("utf-8"),
                    file_name="batch_exceptions_output.csv",
                    mime="text/csv",
                )
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Batch processing failed: {str(e)}")

# -------------------------------------------------------------------
# data/sample_batch_applications.csv
# -------------------------------------------------------------------
"""
application_id,branch,officer_name,age,monthly_net_income,employment_type,employment_tenure_months,residence_stability_months,bureau_flag,existing_obligations_ratio,account_turnover_strength,savings_behaviour,bvn_verification,bank_account_vintage_months
APP-2001,Lagos Mainland,A. Ajayi,34,180000,Private salaried,30,24,Clean,20,Strong,Regular,Verified and consistent,28
APP-2002,Ibadan Central,M. Bello,27,85000,Informal business,10,8,Minor issues,34,Moderate,Irregular,Verified and consistent,12
APP-2003,Abuja South,T. Okonkwo,43,240000,Government salaried,40,36,Clean,16,Strong,Regular,Verified and consistent,45
APP-2004,Kano Metro,R. Musa,29,95000,Self-employed formal,14,15,Serious delinquency,52,Moderate,Irregular,Verified and consistent,16
APP-2005,Port Harcourt,G. Uche,35,120000,Private salaried,18,20,No bureau history,28,Moderate,Regular,Verified with minor mismatch,20
APP-2005,Port Harcourt,G. Uche,35,120000,Private salaried,18,20,No bureau history,28,Moderate,Regular,Verified with minor mismatch,20
APP-2006,Jos North,H. Danjuma,17,65000,Private salaried,6,7,Clean,15,Low,None observed,Verified and consistent,8
APP-2007,Enugu East,C. Obi,31,-20000,Private salaried,12,15,Clean,25,Moderate,Regular,Verified and consistent,18
APP-2008,Benin City,O. Efe,38,150000,Unknown Type,24,20,Clean,18,Strong,Regular,Verified and consistent,22
APP-2009,Abeokuta,S. Akin,30,110000,Private salaried,18,14,Minor issues,72,Moderate,Irregular,Not verified,15
"""

# -------------------------------------------------------------------
# DEPLOYMENT GUIDE (updated)
# -------------------------------------------------------------------
"""
1. Keep all Phase 1 files.
2. Add services/batch_processor.py.
3. Add pages/3_Batch_Scoring.py.
4. Add sample_batch_applications.csv to the data folder.
5. Update config.py, validators.py, and repository.py with the additions shown above.
6. Install dependencies:
   pip install -r requirements.txt
7. Launch:
   streamlit run app.py
"""

# -------------------------------------------------------------------
# MAINTENANCE GUIDE (updated)
# -------------------------------------------------------------------
"""
1. Keep REQUIRED_BATCH_COLUMNS aligned with the rule-driven application input structure.
2. Review batch exception files regularly to identify recurring operational data quality issues.
3. Replace CSV storage with a database table when moving beyond controlled internal usage.
4. For large files, optimise the append logic and avoid row-by-row persistence in the Streamlit layer.
5. Add stronger duplicate handling against historical applications in Phase 3 or Phase 4.
"""

# -------------------------------------------------------------------
# PHASE 2 ARCHITECTURE DECISIONS
# -------------------------------------------------------------------
"""
1. Batch scoring was implemented as a separate service so the logic is reusable for later API or scheduled workflows.
2. Schema validation was separated from row-level validation to provide clearer operational error messages.
3. Exception reporting was built as a first-class output because operational users need to correct bad rows rather than lose the entire file.
4. Batch results are written to dedicated output files and optionally appended into the central scored application store to keep dashboard analytics current.
5. CSV and Excel ingestion were both supported because branch and risk teams often work in spreadsheet-based processes.
"""

# -------------------------------------------------------------------
# PHASE 2 RISK AND GOVERNANCE CONSIDERATIONS
# -------------------------------------------------------------------
"""
1. Batch uploads can introduce operational risk through malformed files, duplicate records, and inconsistent categorizations, so validation and exception reporting are essential.
2. The current implementation prevents the whole batch from failing on row-level errors, which is operationally helpful but requires strong review of exception files.
3. Central storage is still file-based and therefore not yet appropriate for high-concurrency use or tamper-resistant audit requirements.
4. Duplicate handling is currently limited to within-file duplication and lightweight checks against stored application IDs; more robust entity matching is still needed.
5. No approval workflow exists yet for batch-triggered decisions; that will be addressed in later phases with override and audit controls.
"""

# ================================
# PHASE 3 UPGRADE
# Override Workflow + Audit Trail + Searchable Decisions
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
│   ├── 2_New_Application.py
│   ├── 3_Batch_Scoring.py
│   └── 4_Decision_Audit.py
│
├── services/
│   ├── rule_loader.py
│   ├── scorer.py
│   ├── validators.py
│   ├── explainability.py
│   ├── repository.py
│   ├── batch_processor.py
│   ├── audit_logger.py
│   └── override_service.py
│
├── rules/
│   └── scorecard.yaml
│
├── data/
│   ├── sample_scored_applications.csv
│   └── sample_batch_applications.csv
│
└── outputs/
    ├── scored_applications.csv
│   ├── batch_scored_output.csv
│   ├── batch_exceptions_output.csv
│   ├── audit_log.csv
│   └── override_log.csv
"""

# -------------------------------------------------------------------
# config.py (additions)
# -------------------------------------------------------------------
AUDIT_LOG_FILE = "outputs/audit_log.csv"
OVERRIDE_LOG_FILE = "outputs/override_log.csv"

USER_ROLES = ["viewer", "scorer", "approver", "admin"]
AUTHORIZED_OVERRIDE_ROLES = ["approver", "admin"]

# -------------------------------------------------------------------
# components/ui_cards.py (additions)
# -------------------------------------------------------------------

def status_banner(message: str, banner_type: str = "info") -> None:
    if banner_type == "success":
        st.success(message)
    elif banner_type == "warning":
        st.warning(message)
    elif banner_type == "error":
        st.error(message)
    else:
        st.info(message)

# -------------------------------------------------------------------
# services/repository.py (additions)
# -------------------------------------------------------------------

def ensure_named_store(path: str, columns: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def load_table(path: str, columns: list[str]) -> pd.DataFrame:
    ensure_named_store(path, columns)
    return pd.read_csv(path)


def append_row(path: str, row: Dict[str, Any], columns: list[str]) -> None:
    ensure_named_store(path, columns)
    aligned = {col: row.get(col, "") for col in columns}
    pd.DataFrame([aligned]).to_csv(path, mode="a", index=False, header=False)

# -------------------------------------------------------------------
# services/audit_logger.py
# -------------------------------------------------------------------
import json
from datetime import datetime
from typing import Dict, Any
from services.repository import append_row
from config import AUDIT_LOG_FILE

AUDIT_COLUMNS = [
    "audit_id",
    "event_timestamp",
    "event_type",
    "application_id",
    "user_name",
    "user_role",
    "scorecard_version",
    "original_decision",
    "final_decision",
    "risk_band",
    "total_score",
    "reject_reasons",
    "override_flag",
    "override_reason",
    "input_payload_json",
    "component_scores_json",
    "notes",
]


def log_scoring_event(application: Dict[str, Any], result: Dict[str, Any], user_name: str, user_role: str, scorecard_version: str) -> None:
    audit_row = {
        "audit_id": f"AUD-{application['application_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "event_timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": "score_application",
        "application_id": application["application_id"],
        "user_name": user_name,
        "user_role": user_role,
        "scorecard_version": scorecard_version,
        "original_decision": result["decision"],
        "final_decision": result["decision"],
        "risk_band": result["risk_band"],
        "total_score": result["total_score"],
        "reject_reasons": " | ".join(result["reject_reasons"]),
        "override_flag": "No",
        "override_reason": "",
        "input_payload_json": json.dumps(application, default=str),
        "component_scores_json": json.dumps(result["component_scores"], default=str),
        "notes": application.get("notes", ""),
    }
    append_row(AUDIT_LOG_FILE, audit_row, AUDIT_COLUMNS)

# -------------------------------------------------------------------
# services/override_service.py
# -------------------------------------------------------------------
from datetime import datetime
from typing import Dict, Any, Tuple
from services.repository import append_row
from config import OVERRIDE_LOG_FILE, AUTHORIZED_OVERRIDE_ROLES

OVERRIDE_COLUMNS = [
    "override_id",
    "override_timestamp",
    "application_id",
    "override_user",
    "override_user_role",
    "original_decision",
    "overridden_decision",
    "override_reason",
    "credit_officer_notes",
]


def can_override(user_role: str) -> bool:
    return user_role in AUTHORIZED_OVERRIDE_ROLES


def apply_override(
    application_id: str,
    original_decision: str,
    overridden_decision: str,
    override_reason: str,
    override_user: str,
    override_user_role: str,
    credit_officer_notes: str = "",
) -> Tuple[bool, str]:
    if not can_override(override_user_role):
        return False, "Current user role is not authorized to perform overrides."
    if not override_reason.strip():
        return False, "Override reason is mandatory."
    if original_decision == overridden_decision:
        return False, "Override decision must differ from the original decision."

    override_row = {
        "override_id": f"OVR-{application_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "override_timestamp": datetime.now().isoformat(timespec="seconds"),
        "application_id": application_id,
        "override_user": override_user,
        "override_user_role": override_user_role,
        "original_decision": original_decision,
        "overridden_decision": overridden_decision,
        "override_reason": override_reason.strip(),
        "credit_officer_notes": credit_officer_notes,
    }
    append_row(OVERRIDE_LOG_FILE, override_row, OVERRIDE_COLUMNS)
    return True, "Override recorded successfully."

# -------------------------------------------------------------------
# pages/2_New_Application.py (replace imports and selected sections)
# -------------------------------------------------------------------
import streamlit as st
import pandas as pd
from components.styles import inject_global_styles
from components.ui_cards import page_header, result_summary_card, status_banner
from components.charts import score_gauge
from services.rule_loader import load_rules
from services.validators import validate_application
from services.scorer import compute_score
from services.explainability import explain_result
from services.repository import append_scored_application, load_scored_applications
from services.audit_logger import log_scoring_event
from services.override_service import apply_override, can_override
from config import RULE_FILE, SCORED_APPLICATIONS_FILE, USER_ROLES

st.set_page_config(page_title="New Application", page_icon="🧾", layout="wide")
inject_global_styles()
page_header("New Application Scoring", "Capture applicant information, run policy checks, and generate an explainable judgmental credit decision.")

rules = load_rules(RULE_FILE)
score_vars = rules["score_variables"]
cutoffs = rules["decision_cutoffs"]
scorecard_version = rules["metadata"]["version"]

with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.caption("Workflow progress")
    st.progress(50, text="Phase 3: Application scoring, override control, and audit logging")
    st.markdown('</div>', unsafe_allow_html=True)

with st.form("new_application_form"):
    identity_col1, identity_col2 = st.columns(2)
    current_user = identity_col1.text_input("Logged-in user name", value="risk.officer")
    current_role = identity_col2.selectbox("User role", USER_ROLES, index=1)

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

        log_scoring_event(application, result, current_user, current_role, scorecard_version)

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
            status_banner("Application meets current policy threshold and may proceed to the next stage of approval workflow.", "success")
        elif result["decision"] == "Refer":
            status_banner("Application requires manual review before final credit action is taken.", "warning")
        else:
            status_banner("Application should be declined under the current policy unless an exceptional governance process applies.", "error")

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Override workflow")
        st.caption("Only approver and admin roles may record overrides. Every override requires a mandatory reason.")
        override_allowed = can_override(current_role)
        override_decision = st.selectbox("Override decision", ["Approve", "Refer", "Decline"], index=["Approve", "Refer", "Decline"].index(result["decision"]))
        override_reason = st.text_area("Override reason", help="Explain why the original scorecard decision should be changed.")
        if st.button("Record override", disabled=not override_allowed):
            success, message = apply_override(
                application_id=application_id,
                original_decision=result["decision"],
                overridden_decision=override_decision,
                override_reason=override_reason,
                override_user=current_user,
                override_user_role=current_role,
                credit_officer_notes=notes,
            )
            if success:
                status_banner(message, "success")
            else:
                status_banner(message, "error")
        if not override_allowed:
            st.info("Current role is read-only for overrides. Switch role to approver or admin to test override workflow.")
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# pages/4_Decision_Audit.py
# -------------------------------------------------------------------
import streamlit as st
import pandas as pd
from components.styles import inject_global_styles
from components.ui_cards import page_header, kpi_card, decision_badge
from services.repository import load_table
from services.audit_logger import AUDIT_COLUMNS
from services.override_service import OVERRIDE_COLUMNS
from config import AUDIT_LOG_FILE, OVERRIDE_LOG_FILE

st.set_page_config(page_title="Decision Audit", page_icon="🛡️", layout="wide")
inject_global_styles()
page_header("Decision Audit & Search", "Search scored decisions, inspect audit records, and review overrides for governance control.")

audit_df = load_table(AUDIT_LOG_FILE, AUDIT_COLUMNS)
overrides_df = load_table(OVERRIDE_LOG_FILE, OVERRIDE_COLUMNS)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Audit events", f"{len(audit_df):,}")
with c2:
    kpi_card("Overrides", f"{len(overrides_df):,}")
with c3:
    approvals = int((audit_df["final_decision"] == "Approve").sum()) if not audit_df.empty else 0
    kpi_card("Audited approvals", f"{approvals:,}")
with c4:
    declines = int((audit_df["final_decision"] == "Decline").sum()) if not audit_df.empty else 0
    kpi_card("Audited declines", f"{declines:,}")

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Search historical decisions")
search_application = st.text_input("Search by application ID")
search_user = st.text_input("Search by user name")
decision_filter = st.multiselect("Filter by final decision", ["Approve", "Refer", "Decline"], default=["Approve", "Refer", "Decline"])
st.markdown('</div>', unsafe_allow_html=True)

filtered_audit = audit_df.copy()
if not filtered_audit.empty:
    if search_application.strip():
        filtered_audit = filtered_audit[filtered_audit["application_id"].astype(str).str.contains(search_application.strip(), case=False, na=False)]
    if search_user.strip():
        filtered_audit = filtered_audit[filtered_audit["user_name"].astype(str).str.contains(search_user.strip(), case=False, na=False)]
    filtered_audit = filtered_audit[filtered_audit["final_decision"].isin(decision_filter)]

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Audit trail")
if filtered_audit.empty:
    st.info("No audit records found for the selected filters.")
else:
    audit_display = filtered_audit[[
        "event_timestamp", "application_id", "user_name", "user_role", "scorecard_version",
        "original_decision", "final_decision", "risk_band", "total_score", "override_flag", "override_reason"
    ]].copy()
    audit_display["final_decision"] = audit_display["final_decision"].apply(lambda x: decision_badge(x))
    st.write(audit_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.download_button(
        label="Download filtered audit log CSV",
        data=filtered_audit.to_csv(index=False).encode("utf-8"),
        file_name="filtered_audit_log.csv",
        mime="text/csv",
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Override register")
if overrides_df.empty:
    st.info("No overrides have been recorded yet.")
else:
    st.dataframe(overrides_df.sort_values("override_timestamp", ascending=False), use_container_width=True)
    st.download_button(
        label="Download override log CSV",
        data=overrides_df.to_csv(index=False).encode("utf-8"),
        file_name="override_log.csv",
        mime="text/csv",
    )
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# DEPLOYMENT GUIDE (updated)
# -------------------------------------------------------------------
"""
1. Keep all Phase 1 and Phase 2 files.
2. Add services/audit_logger.py and services/override_service.py.
3. Add pages/4_Decision_Audit.py.
4. Update config.py, repository.py, ui_cards.py, and pages/2_New_Application.py with the additions shown above.
5. Launch:
   streamlit run app.py
6. Test with a scorer role and then with an approver role to confirm override permissions behave correctly.
"""

# -------------------------------------------------------------------
# MAINTENANCE GUIDE (updated)
# -------------------------------------------------------------------
"""
1. Audit and override files should be backed up and access-controlled because they form part of governance evidence.
2. The current audit log is append-based and human-readable; later phases should make it immutable and database-backed.
3. Search filters should be expanded in later phases to include date ranges, branch, and officer identifiers.
4. Override reasons should be reviewed periodically by risk management to monitor policy drift and underwriter behaviour.
5. Before production use, authentication and digital signatures should be added to strengthen accountability.
"""

# -------------------------------------------------------------------
# PHASE 3 ARCHITECTURE DECISIONS
# -------------------------------------------------------------------
"""
1. Audit logging was implemented as a separate service to preserve traceability independently of the UI workflow.
2. Override capture was separated into its own service because it is a governance action, not a scoring calculation.
3. Role authorization was introduced as a lightweight placeholder to prepare the app for later authentication and role-based access control.
4. A dedicated decision-audit page was added so governance users can search and export records without interacting with the scoring workflow.
5. File-backed logs remain simple for internal prototyping, but the service boundaries make migration to SQL or an event store straightforward.
"""

# -------------------------------------------------------------------
# PHASE 3 RISK AND GOVERNANCE CONSIDERATIONS
# -------------------------------------------------------------------
"""
1. Overrides are powerful governance events and must never be allowed without mandatory rationale and role restriction.
2. The current role model is illustrative only and is not a substitute for real identity and access management.
3. Audit logs are currently appendable files, which is operationally convenient but not fully tamper-resistant.
4. Scoring and override records should eventually be reconciled so the final decision state is visible in one canonical store.
5. Frequent overrides may indicate poor scorecard calibration, policy ambiguity, or weak frontline data capture and should therefore be monitored.
"""

# -------------------------------------------------------------------
# ROADMAP TO ENTERPRISE CREDIT DECISION ENGINE
# -------------------------------------------------------------------
"""
Phase 4:
- Advanced analytics page
- Decline reason frequency
- Approval rates by branch and bureau category
- Portfolio monitoring hooks

Phase 5:
- Admin policy page
- Scorecard upload and validation
- Version comparison
- Role placeholders and governance controls

Phase 6:
- Database backend
- Authentication and authorization
- API layer with FastAPI
- Integration with loan origination or core banking systems
"""
