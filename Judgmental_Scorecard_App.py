import io
from dataclasses import dataclass
from typing import Dict, Any, List

import pandas as pd
import streamlit as st


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Judgmental Credit Scorecard",
    page_icon="📊",
    layout="wide",
)


# -----------------------------
# Scorecard definition
# -----------------------------
# This is a judgmental scorecard: points are assigned using business rules,
# not learned statistically from historical default data.
SCORECARD = {
    "age": [
        {"label": "18-24", "min": 18, "max": 24, "points": 4},
        {"label": "25-35", "min": 25, "max": 35, "points": 10},
        {"label": "36-50", "min": 36, "max": 50, "points": 14},
        {"label": "51+", "min": 51, "max": 120, "points": 8},
    ],
    "monthly_net_income": [
        {"label": "< 50,000", "min": 0, "max": 49_999, "points": 3},
        {"label": "50,000-99,999", "min": 50_000, "max": 99_999, "points": 8},
        {"label": "100,000-199,999", "min": 100_000, "max": 199_999, "points": 14},
        {"label": "200,000+", "min": 200_000, "max": 10_000_000, "points": 20},
    ],
    "employment_type": {
        "Unemployed": 0,
        "Informal business": 6,
        "Self-employed formal": 10,
        "Private salaried": 14,
        "Government salaried": 18,
    },
    "employment_tenure_months": [
        {"label": "< 6", "min": 0, "max": 5, "points": 2},
        {"label": "6-11", "min": 6, "max": 11, "points": 5},
        {"label": "12-23", "min": 12, "max": 23, "points": 9},
        {"label": "24+", "min": 24, "max": 600, "points": 14},
    ],
    "residence_stability_months": [
        {"label": "< 6", "min": 0, "max": 5, "points": 1},
        {"label": "6-11", "min": 6, "max": 11, "points": 4},
        {"label": "12-23", "min": 12, "max": 23, "points": 7},
        {"label": "24+", "min": 24, "max": 600, "points": 10},
    ],
    "bureau_flag": {
        "Clean": 18,
        "Minor issues": 8,
        "Serious delinquency": -20,
        "No bureau history": 5,
    },
    "existing_obligations_ratio": [
        {"label": "0-20%", "min": 0, "max": 20, "points": 15},
        {"label": "21-40%", "min": 21, "max": 40, "points": 8},
        {"label": "41-60%", "min": 41, "max": 60, "points": 2},
        {"label": ">60%", "min": 61, "max": 100, "points": -10},
    ],
    "account_turnover_score": {
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
}

CUT_OFFS = {
    "Approve": 85,
    "Refer": 65,
}

REJECT_RULES = {
    "min_age": 18,
    "max_dsti": 60,
}


# -----------------------------
# Helper functions
# -----------------------------
def score_band(value: float, rules: List[Dict[str, Any]]) -> int:
    for rule in rules:
        if rule["min"] <= value <= rule["max"]:
            return rule["points"]
    return 0


def compute_score(inputs: Dict[str, Any]) -> Dict[str, Any]:
    reject_reasons = []

    if inputs["age"] < REJECT_RULES["min_age"]:
        reject_reasons.append("Applicant is below the minimum age policy threshold.")
    if inputs["existing_obligations_ratio"] > REJECT_RULES["max_dsti"]:
        reject_reasons.append("Existing obligations ratio exceeds policy limit.")
    if inputs["bvn_verification"] == "Not verified":
        reject_reasons.append("BVN could not be verified.")
    if inputs["bureau_flag"] == "Serious delinquency":
        reject_reasons.append("Credit bureau shows serious delinquency.")

    component_scores = {
        "Age": score_band(inputs["age"], SCORECARD["age"]),
        "Monthly net income": score_band(inputs["monthly_net_income"], SCORECARD["monthly_net_income"]),
        "Employment type": SCORECARD["employment_type"].get(inputs["employment_type"], 0),
        "Employment tenure": score_band(inputs["employment_tenure_months"], SCORECARD["employment_tenure_months"]),
        "Residence stability": score_band(inputs["residence_stability_months"], SCORECARD["residence_stability_months"]),
        "Bureau flag": SCORECARD["bureau_flag"].get(inputs["bureau_flag"], 0),
        "Existing obligations ratio": score_band(inputs["existing_obligations_ratio"], SCORECARD["existing_obligations_ratio"]),
        "Account turnover": SCORECARD["account_turnover_score"].get(inputs["account_turnover_score"], 0),
        "Savings behaviour": SCORECARD["savings_behaviour"].get(inputs["savings_behaviour"], 0),
        "BVN verification": SCORECARD["bvn_verification"].get(inputs["bvn_verification"], 0),
    }

    total_score = sum(component_scores.values())

    if reject_reasons:
        decision = "Decline"
        risk_band = "High risk"
    elif total_score >= CUT_OFFS["Approve"]:
        decision = "Approve"
        risk_band = "Low risk"
    elif total_score >= CUT_OFFS["Refer"]:
        decision = "Refer"
        risk_band = "Medium risk"
    else:
        decision = "Decline"
        risk_band = "High risk"

    return {
        "component_scores": component_scores,
        "total_score": total_score,
        "decision": decision,
        "risk_band": risk_band,
        "reject_reasons": reject_reasons,
    }


def build_result_row(applicant_id: str, inputs: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "applicant_id": applicant_id,
        **inputs,
        **result["component_scores"],
        "total_score": result["total_score"],
        "risk_band": result["risk_band"],
        "decision": result["decision"],
        "reject_reasons": " | ".join(result.get("reject_reasons", [])),
    }


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


# -----------------------------
# Session state
# -----------------------------
if "results" not in st.session_state:
    st.session_state.results = []


# -----------------------------
# App UI
# -----------------------------
st.title("📊 Judgmental Credit Scorecard")
st.caption("Transparent, rule-based applicant scoring for quick credit assessment.")

with st.expander("How this app works", expanded=False):
    st.markdown(
        """
        This app applies a **judgmental scorecard** tailored to a microfinance lending workflow. Each applicant
        characteristic is assigned points using predefined business rules. The total score is then mapped to a decision:

        - **Approve**: score ≥ 85
        - **Refer**: score 65-84
        - **Decline**: score < 65

        The app also includes **hard reject rules**, such as failed BVN verification, serious delinquency,
        and excessive existing obligations. In production, you would calibrate these points and cut-offs using
        policy reviews, portfolio performance, and governance approval.
        """
    )

left, right = st.columns([1.2, 1])

with left:
    with st.form("scorecard_form"):
        st.subheader("Applicant information")

        applicant_id = st.text_input("Applicant ID", value="APP-001")
        age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        monthly_net_income = st.number_input("Monthly net income", min_value=0, value=120000, step=5000)
        employment_type = st.selectbox(
            "Employment type",
            options=list(SCORECARD["employment_type"].keys()),
            index=3,
        )
        employment_tenure_months = st.number_input("Employment tenure (months)", min_value=0, max_value=600, value=24, step=1)
        residence_stability_months = st.number_input("Residence stability (months)", min_value=0, max_value=600, value=18, step=1)
        bureau_flag = st.selectbox(
            "Credit bureau flag",
            options=list(SCORECARD["bureau_flag"].keys()),
            index=0,
        )
        existing_obligations_ratio = st.slider("Existing obligations ratio (%)", min_value=0, max_value=100, value=25, step=1)
        account_turnover_score = st.selectbox(
            "Account turnover strength",
            options=list(SCORECARD["account_turnover_score"].keys()),
            index=1,
        )
        savings_behaviour = st.selectbox(
            "Savings behaviour",
            options=list(SCORECARD["savings_behaviour"].keys()),
            index=1,
        )
        bvn_verification = st.selectbox(
            "BVN verification status",
            options=list(SCORECARD["bvn_verification"].keys()),
            index=0,
        )

        submitted = st.form_submit_button("Score applicant")

    if submitted:
        applicant_inputs = {
            "age": age,
            "monthly_net_income": monthly_net_income,
            "employment_type": employment_type,
            "employment_tenure_months": employment_tenure_months,
            "residence_stability_months": residence_stability_months,
            "bureau_flag": bureau_flag,
            "existing_obligations_ratio": existing_obligations_ratio,
            "account_turnover_score": account_turnover_score,
            "savings_behaviour": savings_behaviour,
            "bvn_verification": bvn_verification,
        }

        result = compute_score(applicant_inputs)
        row = build_result_row(applicant_id, applicant_inputs, result)
        st.session_state.results.append(row)
        st.session_state.latest_result = result
        st.session_state.latest_inputs = applicant_inputs
        st.session_state.latest_applicant_id = applicant_id

with right:
    st.subheader("Latest scoring result")

    if "latest_result" in st.session_state:
        latest = st.session_state.latest_result
        st.metric("Total score", latest["total_score"])
        st.metric("Decision", latest["decision"])
        st.metric("Risk band", latest["risk_band"])

        breakdown = pd.DataFrame(
            {
                "Component": list(latest["component_scores"].keys()),
                "Points": list(latest["component_scores"].values()),
            }
        )
        st.dataframe(breakdown, use_container_width=True, hide_index=True)

        if latest.get("reject_reasons"):
            st.error("Hard reject rule triggered:")
            for reason in latest["reject_reasons"]:
                st.write(f"- {reason}")
    else:
        st.info("Submit the form to see the first score.")

st.divider()
st.subheader("Scored applicants")

if st.session_state.results:
    results_df = pd.DataFrame(st.session_state.results)
    st.dataframe(results_df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)

    with c1:
        decision_summary = results_df["decision"].value_counts().rename_axis("decision").reset_index(name="count")
        st.bar_chart(decision_summary.set_index("decision"))

    with c2:
        st.download_button(
            label="Download results as CSV",
            data=dataframe_to_csv_bytes(results_df),
            file_name="judgmental_scorecard_results.csv",
            mime="text/csv",
        )
else:
    st.warning("No applicants have been scored yet.")

st.divider()
with st.expander("Suggested next enhancements", expanded=False):
    st.markdown(
        """
        1. Add a **policy rules page** so credit policy users can edit points without changing code.  
        2. Separate **hard reject rules** from score-based rules in a governed configuration file.  
        3. Add **override logging** for branch or credit committee review.  
        4. Add **portfolio monitoring** to compare score bands with realised repayment outcomes.  
        5. Move scorecard rules into SQL, Excel, or YAML for version control and governance.  
        6. Add **champion-challenger testing** when a statistical scorecard becomes available.
        """
    )
