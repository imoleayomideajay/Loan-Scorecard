# Credit Decisioning Platform

Single-file Streamlit app for:
- judgmental scorecarding
- batch scoring
- override workflow
- audit trail
- advanced analytics

## Run locally
```bash
pip install -r requirements.txt
streamlit run Judgmental_Scorecard_App.py


# Data Privacy and Ethical AI

This project has been designed with privacy-by-design and ethical AI principles in mind.

### GDPR Compliance Principles
- No personally identifiable information (PII) is stored
- All records use anonymized identifiers
- Only data strictly necessary for decisioning is processed
- Audit logs exclude sensitive personal data

### Ethical AI Considerations
- The system is fully explainable (rule-based scoring)
- Decisions are transparent and auditable
- Override functionality ensures human control
- The system highlights potential bias risks

### Disclaimer
This tool is a decision-support system and does not replace human credit judgment.
