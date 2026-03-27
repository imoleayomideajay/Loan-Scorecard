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
APP_NAME = "Credit Decisioning Platform"
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

PRIVACY_CONFIG = {
    "store_personal_data": False,
    "anonymize_outputs": True,
    "log_minimum_required": True,
}

DATA_RETENTION_DAYS = 90
AUTHORIZED_OVERRIDE_ROLES = ["approver", "admin"]

REQUIRED_BATCH_COLUMNS = [
    "application_id",
    "branch_code",
    "officer_id",
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
    "application_id", "branch_code", "officer_id", "age", "monthly_net_income", "employment_type",
    "employment_tenure_months", "residence_stability_months", "bureau_flag", "existing_obligations_ratio",
    "account_turnover_strength", "savings_behaviour", "bvn_verification", "bank_account_vintage_months",
    "notes", "total_score", "decision", "risk_band", "reject_reasons", "final_decision",
    "override_flag", "timestamp"
]

AUDIT_COLUMNS = [
    "audit_id", "event_timestamp", "event_type", "application_id", "user_id", "user_role",
    "scorecard_version", "original_decision", "final_decision", "risk_band", "total_score",
    "reject_reasons", "override_flag", "override_reason", "input_payload_json", "component_scores_json", "notes"
]

OVERRIDE_COLUMNS = [
    "override_id", "override_timestamp", "application_id", "override_user_id", "override_user_role",
    "original_decision", "overridden_decision", "override_reason", "underwriter_notes"
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
    if not str(data.get("application_id", "")).strip():
        errors.append("Application ID is required.")
    if not str(data.get("branch_code", "")).strip():
        errors.append("Branch code is required.")
    if not str(data.get("officer_id", "")).strip():
        errors.append("Officer ID is required.")
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


def ethical_ai_check(application: Dict[str, Any]) -> List[str]:
    warnings = []
    if application.get("bureau_flag") == "No bureau history":
        warnings.append("Thin-file customer detected. Review for possible exclusion risk and ensure proportional human judgment.")
    if float(application.get("monthly_net_income", 0)) < 50000:
        warnings.append("Low-income applicant detected. Confirm affordability logic is being applied consistently and not unfairly.")
    if float(application.get("age", 0)) < 21:
        warnings.append("Younger applicant detected. Confirm the final outcome is policy-based and free from age-related overreach.")
    warnings.append("This tool is decision support only. Final lending action should remain under accountable human oversight.")
    return warnings


def sanitize_application_payload(application: Dict[str, Any]) -> Dict[str, Any]:
    allowed_keys = {
        "application_id", "branch_code", "officer_id", "age", "monthly_net_income", "employment_type",
        "employment_tenure_months", "residence_stability_months", "bureau_flag", "existing_obligations_ratio",
        "account_turnover_strength", "savings_behaviour", "bvn_verification", "bank_account_vintage_months", "notes"
    }
    return {k: application.get(k, "") for k in allowed_keys}


def log_scoring_event(application: Dict[str, Any], result: Dict[str, Any], user_id: str, user_role: str, scorecard_version: str) -> None:
    safe_application = sanitize_application_payload(application)
    audit_row = {
        "audit_id": f"AUD-{application['application_id']}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "event_timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": "score_application",
        "application_id": application["application_id"],
        "user_id": user_id,
        "user_role": user_role,
        "scorecard_version": scorecard_version,
        "original_decision": result["decision"],
        "final_decision": result["decision"],
        "risk_band": result["risk_band"],
        "total_score": result["total_score"],
        "reject_reasons": " | ".join(result["reject_reasons"]),
        "override_flag": "No",
        "override_reason": "",
        "input_payload_json": json.dumps(safe_application, default=str),
        "component_scores_json": json.dumps(result["component_scores"], default=str),
        "notes": application.get("notes", ""),
    }
    append_row(AUDIT_LOG_FILE, audit_row, AUDIT_COLUMNS)


def can_override(user_role: str) -> bool:
    return user_role in AUTHORIZED_OVERRIDE_ROLES


def apply_override_to_logs(application_id: str, original_decision: str, overridden_decision: str,
                           override_reason: str, override_user_id: str, override_user_role: str,
                           underwriter_notes: str = "") -> Tuple[bool, str]:
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
        "override_user_id": override_user_id,
        "override_user_role": override_user_role,
        "original_decision": original_decision,
        "overridden_decision": overridden_decision,
        "override_reason": override_reason.strip(),
        "underwriter_notes": underwriter_notes,
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
        fig = px.histogram(pd.DataFrame({"total_score": []}), x="total_score")
        fig.update_yaxes(dtick=1, rangemode="tozero")
        return fig
    fig = px.histogram(df, x="total_score", nbins=15)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    fig.update_yaxes(dtick=1, rangemode="tozero", tickformat=",d")
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
        fig = px.bar(pd.DataFrame({"reason": [], "count": []}), x="reason", y="count")
        fig.update_yaxes(dtick=1, rangemode="tozero")
        return fig
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
    fig.update_yaxes(dtick=1, rangemode="tozero", tickformat=",d")
    return fig


def branch_approval_rate(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"branch": [], "approval_rate": []}), x="branch", y="approval_rate")
    tmp = df.copy()
    tmp["approved_flag"] = (tmp["final_decision"].fillna(tmp["decision"]) == "Approve").astype(int)
    plot_df = tmp.groupby("branch_code", as_index=False)["approved_flag"].mean()
    plot_df["approval_rate"] = (plot_df["approved_flag"] * 100).round(1)
    fig = px.bar(plot_df.sort_values("approval_rate", ascending=False), x="branch_code", y="approval_rate")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360, yaxis_title="Approval rate (%)")
    return fig


def bureau_mix_chart(df: pd.DataFrame):
    if df.empty:
        fig = px.histogram(pd.DataFrame({"bureau_flag": []}), x="bureau_flag")
        fig.update_yaxes(dtick=1, rangemode="tozero")
        return fig
    plot_df = df.groupby(["bureau_flag", "final_decision"], as_index=False).size()
    fig = px.bar(plot_df, x="bureau_flag", y="size", color="final_decision", barmode="group",
                 color_discrete_map=DECISION_COLORS)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360, yaxis_title="Applications")
    fig.update_yaxes(dtick=1, rangemode="tozero", tickformat=",d")
    return fig


def override_by_user_chart(df: pd.DataFrame):
    if df.empty:
        fig = px.bar(pd.DataFrame({"override_user_id": [], "count": []}), x="override_user_id", y="count")
        fig.update_yaxes(dtick=1, rangemode="tozero")
        return fig
    plot_df = df["override_user_id"].value_counts().reset_index()
    plot_df.columns = ["override_user_id", "count"]
    fig = px.bar(plot_df, x="override_user_id", y="count")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    fig.update_yaxes(dtick=1, rangemode="tozero", tickformat=",d")
    return fig

# -------------------------------
# INITIALIZE STORAGE
# -------------------------------
ensure_file(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
ensure_file(AUDIT_LOG_FILE, AUDIT_COLUMNS)
ensure_file(OVERRIDE_LOG_FILE, OVERRIDE_COLUMNS)
ensure_file(BATCH_SCORED_OUTPUT_FILE, SCORED_COLUMNS + ["row_number", "recommendation"])
ensure_file(BATCH_EXCEPTION_OUTPUT_FILE, REQUIRED_BATCH_COLUMNS + ["row_number", "error_type", "error_details"])

# Seed a few records once
scored_df_existing = load_table(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
if scored_df_existing.empty:
    seed_rows = [
        {
            "application_id": "APP-0901", "branch_code": "BR-001", "officer_id": "OF-001", "age": 32,
            "monthly_net_income": 180000, "employment_type": "Private salaried", "employment_tenure_months": 28,
            "residence_stability_months": 24, "bureau_flag": "Clean", "existing_obligations_ratio": 22,
            "account_turnover_strength": "Strong", "savings_behaviour": "Regular", "bvn_verification": "Verified and consistent",
            "bank_account_vintage_months": 30, "notes": "", "total_score": 104, "decision": "Approve", "risk_band": "Low Risk",
            "reject_reasons": "", "final_decision": "Approve", "override_flag": "No", "timestamp": "2026-03-25T09:12:00"
        },
        {
            "application_id": "APP-0902", "branch_code": "BR-002", "officer_id": "OF-002", "age": 24,
            "monthly_net_income": 70000, "employment_type": "Informal business", "employment_tenure_months": 8,
            "residence_stability_months": 10, "bureau_flag": "Minor issues", "existing_obligations_ratio": 35,
            "account_turnover_strength": "Moderate", "savings_behaviour": "Irregular", "bvn_verification": "Verified and consistent",
            "bank_account_vintage_months": 12, "notes": "", "total_score": 58, "decision": "Decline", "risk_band": "High Risk",
            "reject_reasons": "", "final_decision": "Decline", "override_flag": "No", "timestamp": "2026-03-25T10:03:00"
        },
        {
            "application_id": "APP-0905", "branch_code": "BR-003", "officer_id": "OF-003", "age": 35,
            "monthly_net_income": 120000, "employment_type": "Private salaried", "employment_tenure_months": 18,
            "residence_stability_months": 20, "bureau_flag": "No bureau history", "existing_obligations_ratio": 28,
            "account_turnover_strength": "Moderate", "savings_behaviour": "Regular", "bvn_verification": "Verified with minor mismatch",
            "bank_account_vintage_months": 20, "notes": "", "total_score": 81, "decision": "Refer", "risk_band": "Medium Risk",
            "reject_reasons": "", "final_decision": "Refer", "override_flag": "No", "timestamp": "2026-03-25T14:05:00"
        },
    ]
    overwrite_table(SCORED_APPLICATIONS_FILE, pd.DataFrame(seed_rows), SCORED_COLUMNS)

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "New Application", "Batch Scoring", "Decision Audit", "Advanced Analytics"],
)

st.sidebar.markdown("---")
st.sidebar.caption(f"{APP_NAME}\nVersion: {APP_VERSION}")

# -------------------------------
# PAGE: DASHBOARD
# -------------------------------
if page == "Dashboard":
    page_header(
    "Portfolio Dashboard",
    "Executive summary of scored applications, decisions, overrides, and portfolio mix."
)

st.markdown("<br>", unsafe_allow_html=True)  # adds vertical space
    df = load_table(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
    overrides_df = load_table(OVERRIDE_LOG_FILE, OVERRIDE_COLUMNS)

    if df.empty:
        st.warning("No scored applications found yet. Score an application to populate the dashboard.")
    else:
        total_apps = len(df)
        approvals = int((df["final_decision"].fillna(df["decision"]) == "Approve").sum())
        referrals = int((df["final_decision"].fillna(df["decision"]) == "Refer").sum())
        declines = int((df["final_decision"].fillna(df["decision"]) == "Decline").sum())
        avg_score = round(pd.to_numeric(df["total_score"], errors="coerce").mean(), 1)
        override_rate = f"{round((len(overrides_df) / total_apps) * 100, 1) if total_apps else 0}%"

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: kpi_card("Applications", f"{total_apps:,}")
        with c2: kpi_card("Approvals", f"{approvals:,}")
        with c3: kpi_card("Referrals", f"{referrals:,}")
        with c4: kpi_card("Declines", f"{declines:,}")
        with c5: kpi_card("Override rate", override_rate)
        with c6: kpi_card("Average score", f"{avg_score}")

        left, right = st.columns(2)
        with left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Decision distribution")
            dd = df.copy()
            dd["decision"] = dd["final_decision"].fillna(dd["decision"])
            st.plotly_chart(decision_donut(dd), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Score distribution")
            st.plotly_chart(score_histogram(df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        left2, right2 = st.columns(2)
        with left2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Average score by employment type")
            st.plotly_chart(employment_avg_score(df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with right2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Recent applications")
            show_cols = ["application_id", "branch_code", "officer_id", "employment_type", "total_score", "final_decision", "timestamp"]
            recent_df = df.sort_values("timestamp", ascending=False).head(10)[show_cols].copy()
            recent_df["final_decision"] = recent_df["final_decision"].apply(lambda x: decision_badge(str(x)))
            st.write(recent_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# PAGE: NEW APPLICATION
# -------------------------------
elif page == "New Application":
    page_header("New Application Scoring", "Capture applicant information, run policy checks, record audit events, and manage overrides.")
    rules = DEFAULT_RULES
    score_vars = rules["score_variables"]
    cutoffs = rules["decision_cutoffs"]
    scorecard_version = rules["metadata"]["version"]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.caption("Workflow progress")
    st.progress(67, text="Phase 4 build: scoring, override control, audit logging, and analytics-ready storage")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("new_application_form"):
        identity_col1, identity_col2 = st.columns(2)
        current_user = identity_col1.text_input("Logged-in user ID", value="USR-001")
        current_role = identity_col2.selectbox("User role", USER_ROLES, index=1)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Personal Details", "Income & Employment", "Credit Exposure", "Behaviour & Verification"
        ])

        with tab1:
            c1, c2, c3 = st.columns(3)
            application_id = c1.text_input("Application ID", value=f"APP-{datetime.now().strftime('%H%M%S')}")
            branch_code = c2.text_input("Branch Code", value="BR-001")
            officer_id = c3.text_input("Officer ID", value="OF-001")
            age = st.number_input("Age", min_value=18, max_value=75, value=31)
            residence_stability_months = st.number_input("Residence stability (months)", min_value=0, max_value=600, value=18)

        with tab2:
            c1, c2 = st.columns(2)
            monthly_net_income = c1.number_input("Monthly net income", min_value=0, value=150000, step=5000)
            employment_type = c2.selectbox("Employment type", list(score_vars["employment_type"].keys()))
            employment_tenure_months = st.number_input("Employment tenure (months)", min_value=0, max_value=600, value=24)

        with tab3:
            c1, c2 = st.columns(2)
            bureau_flag = c1.selectbox("Credit bureau flag", list(score_vars["bureau_flag"].keys()))
            existing_obligations_ratio = c2.slider("Existing obligations ratio (%)", min_value=0, max_value=100, value=25)

        with tab4:
            c1, c2, c3 = st.columns(3)
            account_turnover_strength = c1.selectbox("Account turnover strength", list(score_vars["account_turnover_strength"].keys()))
            savings_behaviour = c2.selectbox("Savings behaviour", list(score_vars["savings_behaviour"].keys()))
            bvn_verification = c3.selectbox("BVN verification", list(score_vars["bvn_verification"].keys()))
            bank_account_vintage_months = st.number_input("Bank account vintage (months)", min_value=0, max_value=600, value=18)

        notes = st.text_area("Credit officer notes")
        submit = st.form_submit_button("Run scorecard")

    if submit:
        application = {
            "application_id": application_id,
            "branch_code": branch_code,
            "officer_id": officer_id,
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
            existing = load_table(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
            if not existing.empty and application_id in existing["application_id"].astype(str).tolist():
                st.warning("Duplicate application ID detected. Review whether this is a resubmission or a duplicate entry.")

            result = compute_score(application, rules)
            explanations = explain_result(result["component_scores"], result["reject_reasons"])
            log_scoring_event(application, result, current_user, current_role, scorecard_version)

            append_row(SCORED_APPLICATIONS_FILE, {
                **application,
                "total_score": result["total_score"],
                "decision": result["decision"],
                "risk_band": result["risk_band"],
                "reject_reasons": " | ".join(result["reject_reasons"]),
                "final_decision": result["decision"],
                "override_flag": "No",
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }, SCORED_COLUMNS)

            left, right = st.columns([1.1, 0.9])
            with left:
                result_summary_card(result["total_score"], result["decision"], result["risk_band"], result["recommendation"])
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("Component score breakdown")
                breakdown_df = pd.DataFrame({"Component": list(result["component_scores"].keys()), "Points": list(result["component_scores"].values())})
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with right:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("Score visualization")
                st.plotly_chart(score_gauge(result["total_score"], cutoffs["approve"], cutoffs["refer"]), use_container_width=True)
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
            override_allowed = can_override(current_role)
            override_decision = st.selectbox("Override decision", ["Approve", "Refer", "Decline"], index=["Approve", "Refer", "Decline"].index(result["decision"]), key="ov_decision")
            override_reason = st.text_area("Override reason", key="ov_reason")
            if st.button("Record override", disabled=not override_allowed):
                success, message = apply_override_to_logs(
                    application_id=application_id,
                    original_decision=result["decision"],
                    overridden_decision=override_decision,
                    override_reason=override_reason,
                    override_user_id=current_user,
                    override_user_role=current_role,
                    underwriter_notes=notes,
                )
                status_banner(message, "success" if success else "error")
            if not override_allowed:
                st.info("Current role is read-only for overrides. Switch role to approver or admin to test override workflow.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Privacy, GDPR, and Ethical AI")
            st.write("• No direct personal identifiers are stored in this application.")
            st.write("• Only pseudonymous operational identifiers are retained for accountability.")
            st.write("• BVN status is assessed, but BVN values themselves are not stored.")
            st.write("• This tool is decision support only and does not replace accountable human lending judgment.")
            st.write(f"• Indicative retention setting: {DATA_RETENTION_DAYS} days.")
            ethical_flags = ethical_ai_check(application)
            st.caption("Fairness and ethics prompts")
            for flag in ethical_flags:
                st.write(f"• {flag}")
            st.info("This decision is based on a transparent rule-based scorecard and should support, not replace, accountable human judgment.")
            st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# PAGE: BATCH SCORING
# -------------------------------
elif page == "Batch Scoring":
    page_header("Batch Scoring", "Upload multiple loan applications, validate rows, score valid cases, and generate exception reports.")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Upload input file")
    st.write("Supported formats: CSV and Excel (.xlsx). For Excel support, install openpyxl.")
    uploaded_file = st.file_uploader("Select batch file", type=["csv", "xlsx"])
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("View required input schema", expanded=False):
        st.dataframe(pd.DataFrame({"required_column": REQUIRED_BATCH_COLUMNS}), use_container_width=True, hide_index=True)

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
                scored_df, exceptions_df, summary = process_batch(batch_df, DEFAULT_RULES)
                overwrite_table(BATCH_SCORED_OUTPUT_FILE, scored_df, list(scored_df.columns) if not scored_df.empty else SCORED_COLUMNS)
                overwrite_table(BATCH_EXCEPTION_OUTPUT_FILE, exceptions_df, list(exceptions_df.columns) if not exceptions_df.empty else REQUIRED_BATCH_COLUMNS + ["row_number", "error_type", "error_details"])

                existing_store = load_table(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
                existing_ids = set(existing_store["application_id"].astype(str).tolist()) if not existing_store.empty else set()
                for _, r in scored_df.iterrows():
                    if str(r["application_id"]) not in existing_ids:
                        append_row(SCORED_APPLICATIONS_FILE, {
                            "application_id": r["application_id"],
                            "branch_code": r["branch_code"],
                            "officer_id": r["officer_id"],
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
                            "final_decision": r["decision"],
                            "override_flag": "No",
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                        }, SCORED_COLUMNS)
                        existing_ids.add(str(r["application_id"]))

                c1, c2, c3, c4, c5, c6 = st.columns(6)
                with c1: kpi_card("Rows uploaded", f"{summary['rows_uploaded']:,}")
                with c2: kpi_card("Rows scored", f"{summary['rows_scored']:,}")
                with c3: kpi_card("Rows failed", f"{summary['rows_failed']:,}")
                with c4: kpi_card("Approvals", f"{summary['approvals']:,}")
                with c5: kpi_card("Referrals", f"{summary['referrals']:,}")
                with c6: kpi_card("Average score", f"{summary['average_score']}")

                if not scored_df.empty:
                    left, right = st.columns(2)
                    with left:
                        st.markdown('<div class="section-card">', unsafe_allow_html=True)
                        st.subheader("Batch decision distribution")
                        tmp = scored_df.copy()
                        tmp["decision"] = tmp["final_decision"]
                        st.plotly_chart(decision_donut(tmp), use_container_width=True)
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
                    st.download_button("Download scored output CSV", scored_df.to_csv(index=False).encode("utf-8"), "batch_scored_output.csv", "text/csv")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("Exception report")
                if exceptions_df.empty:
                    st.success("No row-level exceptions were detected.")
                else:
                    st.dataframe(exceptions_df, use_container_width=True)
                    st.download_button("Download exception report CSV", exceptions_df.to_csv(index=False).encode("utf-8"), "batch_exceptions_output.csv", "text/csv")
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Batch processing failed: {str(e)}")

# -------------------------------
# PAGE: DECISION AUDIT
# -------------------------------
elif page == "Decision Audit":
    page_header("Decision Audit & Search", "Search scored decisions, inspect audit records, and review overrides for governance control.")
    audit_df = load_table(AUDIT_LOG_FILE, AUDIT_COLUMNS)
    overrides_df = load_table(OVERRIDE_LOG_FILE, OVERRIDE_COLUMNS)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Audit events", f"{len(audit_df):,}")
    with c2: kpi_card("Overrides", f"{len(overrides_df):,}")
    with c3: kpi_card("Audited approvals", f"{int((audit_df['final_decision'] == 'Approve').sum()) if not audit_df.empty else 0:,}")
    with c4: kpi_card("Audited declines", f"{int((audit_df['final_decision'] == 'Decline').sum()) if not audit_df.empty else 0:,}")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Search historical decisions")
    search_application = st.text_input("Search by application ID")
    search_user = st.text_input("Search by user ID")
    decision_filter = st.multiselect("Filter by final decision", ["Approve", "Refer", "Decline"], default=["Approve", "Refer", "Decline"])
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_audit = audit_df.copy()
    if not filtered_audit.empty:
        if search_application.strip():
            filtered_audit = filtered_audit[filtered_audit["application_id"].astype(str).str.contains(search_application.strip(), case=False, na=False)]
        if search_user.strip():
            filtered_audit = filtered_audit[filtered_audit["user_id"].astype(str).str.contains(search_user.strip(), case=False, na=False)]
        filtered_audit = filtered_audit[filtered_audit["final_decision"].isin(decision_filter)]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Audit trail")
    if filtered_audit.empty:
        st.info("No audit records found for the selected filters.")
    else:
        audit_display = filtered_audit[[
            "event_timestamp", "application_id", "user_id", "user_role", "scorecard_version",
            "original_decision", "final_decision", "risk_band", "total_score", "override_flag", "override_reason"
        ]].copy()
        audit_display["final_decision"] = audit_display["final_decision"].apply(lambda x: decision_badge(str(x)))
        st.write(audit_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.download_button("Download filtered audit log CSV", filtered_audit.to_csv(index=False).encode("utf-8"), "filtered_audit_log.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Override register")
    if overrides_df.empty:
        st.info("No overrides have been recorded yet.")
    else:
        st.dataframe(overrides_df.sort_values("override_timestamp", ascending=False), use_container_width=True)
        st.download_button("Download override log CSV", overrides_df.to_csv(index=False).encode("utf-8"), "override_log.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# PAGE: ADVANCED ANALYTICS (PHASE 4)
# -------------------------------
elif page == "Advanced Analytics":
    page_header("Advanced Analytics", "Portfolio intelligence across decisions, branches, bureau segments, decline reasons, and overrides.")
    df = load_table(SCORED_APPLICATIONS_FILE, SCORED_COLUMNS)
    audit_df = load_table(AUDIT_LOG_FILE, AUDIT_COLUMNS)
    overrides_df = load_table(OVERRIDE_LOG_FILE, OVERRIDE_COLUMNS)

    if df.empty:
        st.warning("No scored application data is available yet.")
    else:
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["total_score"] = pd.to_numeric(df["total_score"], errors="coerce")
        df["final_decision"] = df["final_decision"].fillna(df["decision"])

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Analytics filters")
        f1, f2, f3, f4 = st.columns(4)
        decision_filter = f1.multiselect("Decision", sorted(df["final_decision"].dropna().unique().tolist()), default=sorted(df["final_decision"].dropna().unique().tolist()))
        branch_filter = f2.multiselect("Branch Code", sorted(df["branch_code"].dropna().unique().tolist()), default=sorted(df["branch_code"].dropna().unique().tolist()))
        employment_filter = f3.multiselect("Employment type", sorted(df["employment_type"].dropna().unique().tolist()), default=sorted(df["employment_type"].dropna().unique().tolist()))
        score_range = f4.slider("Score range", 0, 120, (0, 120))
        st.markdown('</div>', unsafe_allow_html=True)

        filt = df[
            df["final_decision"].isin(decision_filter)
            & df["branch_code"].isin(branch_filter)
            & df["employment_type"].isin(employment_filter)
            & df["total_score"].between(score_range[0], score_range[1], inclusive="both")
        ].copy()

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: kpi_card("Filtered apps", f"{len(filt):,}")
        with c2: kpi_card("Approval rate", f"{round((filt['final_decision'] == 'Approve').mean()*100,1) if len(filt) else 0}%")
        with c3: kpi_card("Average score", f"{round(filt['total_score'].mean(),1) if len(filt) else 0}")
        with c4: kpi_card("Median score", f"{round(filt['total_score'].median(),1) if len(filt) else 0}")
        with c5: kpi_card("Overrides", f"{int(filt['override_flag'].fillna('No').eq('Yes').sum()):,}")
        with c6: kpi_card("Branches", f"{filt['branch_code'].nunique() if len(filt) else 0}")

        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Decision mix")
            tmp = filt.copy()
            tmp["decision"] = tmp["final_decision"]
            st.plotly_chart(decision_donut(tmp), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with row1_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Score distribution")
            st.plotly_chart(score_histogram(filt), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Branch approval rates")
            st.plotly_chart(branch_approval_rate(filt), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with row2_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Bureau mix by final decision")
            st.plotly_chart(bureau_mix_chart(filt), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        row3_left, row3_right = st.columns(2)
        with row3_left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Decline reason frequency")
            decline_df = filt[filt["final_decision"] == "Decline"]
            st.plotly_chart(decline_reason_bar(decline_df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with row3_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Overrides by user")
            override_filt = overrides_df.copy()
            if not override_filt.empty:
                relevant_ids = set(filt["application_id"].astype(str).tolist())
                override_filt = override_filt[override_filt["application_id"].astype(str).isin(relevant_ids)]
            st.plotly_chart(override_by_user_chart(override_filt), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Filtered portfolio detail")
        detail_cols = [
            "application_id", "branch_code", "officer_id", "employment_type", "bureau_flag",
            "total_score", "decision", "final_decision", "override_flag", "timestamp"
        ]
        st.dataframe(filt[detail_cols].sort_values("timestamp", ascending=False), use_container_width=True)
        st.download_button(
            "Download filtered analytics dataset CSV",
            filt.to_csv(index=False).encode("utf-8"),
            "analytics_filtered_dataset.csv",
            "text/csv",
        )
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption(
    "Ready-to-run single-file build. Install: streamlit, pandas, plotly. For Excel upload support also install openpyxl. "
    "This GDPR-aware version excludes direct personal names and uses pseudonymous operational identifiers only. "
    "Run with: streamlit run Judgmental_Scorecard_App.py"
)
