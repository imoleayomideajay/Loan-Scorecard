import os
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# READY-TO-RUN SINGLE-FILE ENTERPRISE CREDIT DECISIONING APP
# Phase 1: Premium UI + scoring
# Phase 2: Batch scoring + exceptions
# Phase 3: Override + audit trail
# Phase 4: Advanced analytics
# ============================================================

# -------------------------------
# APP CONFIG
# -------------------------------
APP_NAME = "AB Microfinance Credit Decisioning Platform"
APP_VERSION = "2.0.0-single-file-phase4"

OUTPUT_DIR = "outputs"
SCORED_APPLICATIONS_FILE = os.path.join(OUTPUT_DIR, "scored_applications.csv")
BATCH_SCORED_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "batch_scored_output.csv")
BATCH_EXCEPTION_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "batch_exceptions_output.csv")
AUDIT_LOG_FILE = os.path.join(OUTPUT_DIR, "audit_log.csv")
OVERRIDE_LOG_FILE = os.path.join(OUTPUT_DIR, "override_log.csv")

DECISION_COLORS = {
    "Approve": "#0F9D58",
    "Refer": "#F4B400",
    "Decline": "#DB4437",
    "Override": "#7E57C2",
}

USER_ROLES = ["viewer", "scorer", "approver", "admin"]
AUTHORIZED_OVERRIDE_ROLES = ["approver", "admin"]

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

DEFAULT_RULES = {
    "metadata": {
        "scorecard_name": "Judgmental Retail Scorecard",
        "version": "2026.03",
        "effective_date": "2026-03-01",
        "approved_by": "Head of Credit Risk",
        "last_updated": "2026-03-20",
    },
    "decision_cutoffs": {
        "approve": 85,
        "refer": 65,
    },
    "hard_reject_rules": {
        "max_existing_obligations_ratio": 60,
        "bvn_not_verified": "Applicant failed BVN verification.",
        "serious_delinquency": "Credit bureau shows serious delinquency.",
    },
    "score_variables": {
        "age": [
            {"min": 18, "max": 24, "points": 4},
            {"min": 25, "max": 35, "points": 10},
            {"min": 36, "max": 50, "points": 14},
            {"min": 51, "max": 75, "points": 8},
        ],
        "monthly_net_income": [
            {"min": 0, "max": 49999, "points": 3},
            {"min": 50000, "max": 99999, "points": 8},
            {"min": 100000, "max": 199999, "points": 14},
            {"min": 200000, "max": 99999999, "points": 20},
        ],
        "employment_type": {
            "Unemployed": 0,
            "Informal business": 6,
            "Self-employed formal": 10,
            "Private salaried": 14,
            "Government salaried": 18,
        },
        "employment_tenure_months": [
            {"min": 0, "max": 5, "points": 2},
            {"min": 6, "max": 11, "points": 5},
            {"min": 12, "max": 23, "points": 9},
            {"min": 24, "max": 600, "points": 14},
        ],
        "residence_stability_months": [
            {"min": 0, "max": 5, "points": 1},
            {"min": 6, "max": 11, "points": 4},
            {"min": 12, "max": 23, "points": 7},
            {"min": 24, "max": 600, "points": 10},
        ],
        "bureau_flag": {
            "Clean": 18,
            "Minor issues": 8,
            "Serious delinquency": -20,
            "No bureau history": 5,
        },
        "existing_obligations_ratio": [
            {"min": 0, "max": 20, "points": 15},
            {"min": 21, "max": 40, "points": 8},
            {"min": 41, "max": 60, "points": 2},
            {"min": 61, "max": 100, "points": -10},
        ],
        "account_turnover_strength": {
            "Low": 3,
            "Moderate": 8,
            "Strong": 14,
        },
        "savings_behaviour": {
            "None observed": 0,
            "Irregular": 5,
            "Regular": 12,
        },
        "bvn_verification": {
            "Verified and consistent": 10,
            "Verified with minor mismatch": 4,
            "Not verified": -15,
        },
        "bank_account_vintage_months": [
            {"min": 0, "max": 5, "points": 2},
            {"min": 6, "max": 11, "points": 5},
            {"min": 12, "max": 23, "points": 8},
            {"min": 24, "max": 600, "points": 12},
        ],
    },
}

SCORED_COLUMNS = [
    "application_id", "branch", "officer_name", "age", "monthly_net_income", "employment_type",
    "employment_tenure_months", "residence_stability_months", "bureau_flag", "existing_obligations_ratio",
    "account_turnover_strength", "savings_behaviour", "bvn_verification", "bank_account_vintage_months",
    "notes", "total_score", "decision", "risk_band", "reject_reasons", "final_decision",
    "override_flag", "timestamp"
]

AUDIT_COLUMNS = [
    "audit_id", "event_timestamp", "event_type", "application_id", "user_name", "user_role",
    "scorecard_version", "original_decision", "final_decision", "risk_band", "total_score",
    "reject_reasons", "override_flag", "override_reason", "input_payload_json", "component_scores_json", "notes"
]

OVERRIDE_COLUMNS = [
    "override_id", "override_timestamp", "application_id", "override_user", "override_user_role",
    "original_decision", "overridden_decision", "override_reason", "credit_officer_notes"
]

# -------------------------------
# PAGE SETUP
# -------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------
# STYLES
# -------------------------------
def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            .main {background-color: #F6F8FB;}
            .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1380px;}
            .app-title {font-size: 2rem; font-weight: 700; color: #0B1F33; margin-bottom: 0.25rem;}
            .app-subtitle {font-size: 0.98rem; color: #5B6B7A; margin-bottom: 1.25rem;}
            .kpi-card {background: white; border-radius: 18px; padding: 1rem 1rem 0.8rem 1rem; box-shadow: 0 2px 16px rgba(16,24,40,.06); border: 1px solid #E9EEF5;}
            .kpi-label {font-size: .85rem; color: #667085; margin-bottom: .2rem;}
            .kpi-value {font-size: 1.7rem; font-weight: 700; color: #101828;}
            .section-card {background: white; border-radius: 18px; padding: 1.15rem; box-shadow: 0 2px 16px rgba(16,24,40,.06); border: 1px solid #E9EEF5; margin-bottom: 1rem;}
            .decision-badge {display: inline-block; padding: 0.35rem 0.8rem; border-radius: 999px; font-size: .82rem; font-weight: 600; color: white;}
            .summary-card {background: linear-gradient(135deg,#0B1F33 0%,#163B65 100%); color: white; border-radius: 20px; padding: 1.25rem; box-shadow: 0 8px 24px rgba(11,31,51,.18);}
            .summary-title {font-size: .95rem; opacity: .9; margin-bottom: .4rem;}
            .summary-score {font-size: 2.2rem; font-weight: 800; margin-bottom: .2rem;}
            .small-note {font-size: .82rem; color: #667085;}
            div[data-testid="stMetricValue"] {font-weight: 700;}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_global_styles()

# -------------------------------
# HELPERS
# -------------------------------
def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="app-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str) -> None:
    st.markdown(
        f'''<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>''',
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


def status_banner(message: str, banner_type: str = "info") -> None:
    if banner_type == "success":
        st.success(message)
    elif banner_type == "warning":
        st.warning(message)
    elif banner_type == "error":
        st.error(message)
    else:
        st.info(message)


def ensure_file(path: str, columns: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def load_table(path: str, columns: List[str]) -> pd.DataFrame:
    ensure_file(path, columns)
    return pd.read_csv(path)


def append_row(path: str, row: Dict[str, Any], columns: List[str]) -> None:
    ensure_file(path, columns)
    aligned = {col: row.get(col, "") for col in columns}
    pd.DataFrame([aligned]).to_csv(path, mode="a", index=False, header=False)


def overwrite_table(path: str, df: pd.DataFrame, columns: List[str]) -> None:
    ensure_file(path, columns)
    if df.empty:
        pd.DataFrame(columns=columns).to_csv(path, index=False)
    else:
        ordered = df.copy()
        for col in columns:
            if col not in ordered.columns:
                ordered[col] = ""
        ordered[columns].to_csv(path, index=False)


def score_band(value: float, rules: List[Dict[str, Any]]) -> int:
    for rule in rules:
        if rule["min"] <= value <= rule["max"]:
            return int(rule["points"])
    return 0


def validate_application(data: Dict[str, Any]) -> List[str]:
    errors = []
    if not 18 <= float(data.get("age", 0)) <= 75:
        errors.append("Age must be between 18 and 75.")
    if float(data.get("monthly_net_income", 0)) < 0:
        errors.append("Monthly net income cannot be negative.")
    if not 0 <= float(data.get("existing_obligations_ratio", 0)) <= 100:
        errors.append("Existing obligations ratio must be between 0 and 100.")
    if float(data.get("employment_tenure_months", 0)) < 0:
        errors.append("Employment tenure cannot be negative.")
    if float(data.get("residence_stability_months", 0)) < 0:
        errors.append("Residence stability cannot be negative.")
    if float(data.get("bank_account_vintage_months", 0)) < 0:
        errors.append("Bank account vintage cannot be negative.")
    return errors


def validate_batch_schema(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    missing = [c for c in required_columns if c not in df.columns]
    return [f"Missing required columns: {', '.join(missing)}"] if missing else []


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


def evaluate_hard_rejects(data: Dict[str, Any], hard_rules: Dict[str, Any]) -> List[str]:
    reasons = []
    if data["bvn_verification"] == "Not verified":
        reasons.append(hard_rules["bvn_not_verified"])
    if data["bureau_flag"] == "Serious delinquency":
        reasons.append(hard_rules["serious_delinquency"])
    if float(data["existing_obligations_ratio"]) > hard_rules["max_existing_obligations_ratio"]:
        reasons.append(f"Existing obligations ratio exceeds {hard_rules['max_existing_obligations_ratio']}% policy threshold.")
    return reasons


def build_recommendation(decision: str, reject_reasons: List[str]) -> str:
    if reject_reasons:
        return "Application failed one or more non-negotiable policy checks and should not proceed without exceptional governance approval."
    if decision == "Approve":
        return "Applicant meets policy expectations on affordability, stability, and behavioural indicators. Proceed to standard approval workflow."
    if decision == "Refer":
        return "Application is borderline and should be reviewed manually by a credit officer or committee before a final lending decision is made."
    return "Application score is below the policy cut-off and should be declined under current judgmental scorecard rules."


def compute_score(data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    hard_rejects = evaluate_hard_rejects(data, rules["hard_reject_rules"])
    sv = rules["score_variables"]
    component_scores = {
        "Age": score_band(float(data["age"]), sv["age"]),
        "Monthly net income": score_band(float(data["monthly_net_income"]), sv["monthly_net_income"]),
        "Employment type": sv["employment_type"].get(data["employment_type"], 0),
        "Employment tenure": score_band(float(data["employment_tenure_months"]), sv["employment_tenure_months"]),
        "Residence stability": score_band(float(data["residence_stability_months"]), sv["residence_stability_months"]),
        "Bureau flag": sv["bureau_flag"].get(data["bureau_flag"], 0),
        "Existing obligations ratio": score_band(float(data["existing_obligations_ratio"]), sv["existing_obligations_ratio"]),
        "Account turnover": sv["account_turnover_strength"].get(data["account_turnover_strength"], 0),
        "Savings behaviour": sv["savings_behaviour"].get(data["savings_behaviour"], 0),
        "BVN verification": sv["bvn_verification"].get(data["bvn_verification"], 0),
        "Bank account vintage": score_band(float(data["bank_account_vintage_months"]), sv["bank_account_vintage_months"]),
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
    return {
        "component_scores": component_scores,
        "total_score": total_score,
        "decision": decision,
        "risk_band": risk_band,
        "reject_reasons": hard_rejects,
        "recommendation": build_recommendation(decision, hard_rejects),
    }


def explain_result(component_scores: Dict[str, int], reject_reasons: List[str]) -> Dict[str, List[str]]:
    positive = [f"{k} contributed positively (+{v})" for k, v in component_scores.items() if v > 0]
    negative = [f"{k} reduced score ({v})" for k, v in component_scores.items() if v < 0]
    policy = reject_reasons if reject_reasons else ["No hard reject rule was triggered."]
    return {"positive_factors": positive, "negative_factors": negative, "policy_flags": policy}


def log_scoring_event(application: Dict[str, Any], result: Dict[str, Any], user_name: str, user_role: str, scorecard_version: str) -> None:
    audit_row = {
        "audit_id": f"AUD-{application['application_id']}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
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


def can_override(user_role: str) -> bool:
    return user_role in AUTHORIZED_OVERRIDE_ROLES


def apply_override_to_logs(application_id: str, original_decision: str, overridden_decision: str,
                           override_reason: str, override_user: str, override_user_role: str,
                           credit_officer_notes: str = "") -> Tuple[bool, str]:
    if not can_override(override_user_role):
        return False, "Current user role is not authorized to perform overrides."
    if not override_reason.strip():
        return False, "Override reason is mandatory."
    if original_decision == overridden_decision:
        return False, "Override decision must differ from the original decision."

    override_row = {
        "override_id": f"OVR-{application_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
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

    audit_df = load_table(AUDIT_LOG_FILE, AUDIT_COLUMNS)
    if not audit_df.empty:
        mask = audit_df["application_id"].astype(str) == str(application_id)
        if mask.any():
            latest_idx = audit_df.loc[mask].sort_values("event_timestamp").index[-1]
            audit_df.loc[latest_idx, "final_decision"] = overridden_decision
            audit_df.loc[latest_idx, "override_flag"] = "Yes"
            audit_df.loc[latest_idx, "override_reason"] = override_reason.strip()
            overwrite_table(AUDIT_LOG_FILE, audit_df, AUDIT_COLUMNS)

    scored_df = load_table(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
    if not scored_df.empty:
        mask = scored_df["application_id"].astype(str) == str(application_id)
        if mask.any():
            latest_idx = scored_df.loc[mask].sort_values("timestamp").index[-1]
            scored_df.loc[latest_idx, "final_decision"] = overridden_decision
            scored_df.loc[latest_idx, "override_flag"] = "Yes"
            overwrite_table(SCORED_APPLICATIONS_FILE, scored_df, SCORED_COLUMNS)

    return True, "Override recorded successfully and synchronized to the master records."


def process_batch(df: pd.DataFrame, rules: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    schema_errors = validate_batch_schema(df, REQUIRED_BATCH_COLUMNS)
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
            "notes": "Batch upload",
            "row_number": row_num,
            "total_score": result["total_score"],
            "decision": result["decision"],
            "risk_band": result["risk_band"],
            "reject_reasons": " | ".join(result["reject_reasons"]),
            "final_decision": result["decision"],
            "override_flag": "No",
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
        "average_score": round(float(scored_df["total_score"].mean()), 1) if not scored_df.empty else 0,
    }
    return scored_df, exceptions_df, summary

# -------------------------------
# CHARTS
# -------------------------------
def decision_donut(df: pd.DataFrame):
    if df.empty or "decision" not in df.columns:
        return px.pie(pd.DataFrame({"decision": ["No data"], "count": [1]}), names="decision", values="count")
    plot_df = df["decision"].astype(str).value_counts().reset_index()
    plot_df.columns = ["decision", "count"]
    fig = px.pie(plot_df, names="decision", values="count", hole=0.62,
                 color="decision", color_discrete_map=DECISION_COLORS)
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig


def score_histogram(df: pd.DataFrame):
    if df.empty or "total_score" not in df.columns:
        return px.histogram(pd.DataFrame({"total_score": []}), x="total_score")
    fig = px.histogram(df, x="total_score", nbins=15)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig


def employment_avg_score(df: pd.DataFrame):
    if df.empty or "employment_type" not in df.columns:
        return px.bar(pd.DataFrame({"employment_type": [], "total_score": []}), x="employment_type", y="total_score")
    plot_df = df.groupby("employment_type", as_index=False)["total_score"].mean().sort_values("total_score", ascending=False)
    fig = px.bar(plot_df, x="employment_type", y="total_score")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig


def score_gauge(score: int, approve_cutoff: int, refer_cutoff: int):
    fig = go.Figure(go.Indicator(
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
            "threshold": {"line": {"color": "#101828", "width": 4}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def decline_reason_bar(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"reason": [], "count": []}), x="reason", y="count")
    reasons = []
    for item in df["reject_reasons"].fillna(""):
        for part in [x.strip() for x in str(item).split("|") if x.strip()]:
            reasons.append(part)
    reason_df = pd.Series(reasons).value_counts().reset_index()
    if reason_df.empty:
        reason_df = pd.DataFrame({"reason": ["No recorded decline reasons"], "count": [0]})
    else:
        reason_df.columns = ["reason", "count"]
    fig = px.bar(reason_df, x="reason", y="count")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360, xaxis_title="Decline reason")
    return fig


def branch_approval_rate(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"branch": [], "approval_rate": []}), x="branch", y="approval_rate")
    tmp = df.copy()
    tmp["approved_flag"] = (tmp["final_decision"].fillna(tmp["decision"]) == "Approve").astype(int)
    plot_df = tmp.groupby("branch", as_index=False)["approved_flag"].mean()
    plot_df["approval_rate"] = (plot_df["approved_flag"] * 100).round(1)
    fig = px.bar(plot_df.sort_values("approval_rate", ascending=False), x="branch", y="approval_rate")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360, yaxis_title="Approval rate (%)")
    return fig


def bureau_mix_chart(df: pd.DataFrame):
    if df.empty:
        return px.histogram(pd.DataFrame({"bureau_flag": []}), x="bureau_flag")
    plot_df = df.groupby(["bureau_flag", "final_decision"], as_index=False).size()
    fig = px.bar(plot_df, x="bureau_flag", y="size", color="final_decision", barmode="group",
                 color_discrete_map=DECISION_COLORS)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360, yaxis_title="Applications")
    return fig


def override_by_user_chart(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"override_user": [], "count": []}), x="override_user", y="count")
    plot_df = df["override_user"].value_counts().reset_index()
    plot_df.columns = ["override_user", "count"]
    fig = px.bar(plot_df, x="override_user", y="count")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return fig

#
