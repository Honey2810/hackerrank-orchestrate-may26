import pandas as pd
import os

# Load input CSV
input_path = "support_tickets/support_tickets.csv"

if not os.path.exists(input_path):
    print(f"File not found: {input_path}")
    exit()

df = pd.read_csv(input_path)

results = []

# High-risk words requiring escalation
HIGH_RISK = [
    "fraud", "stolen", "unauthorized", "hacked",
    "scam", "chargeback", "illegal", "compromised",
    "secret call", "invisible transaction", "executive promise",
    "personally promised", "quantum", "mars"
]

# Process each support issue
for _, row in df.iterrows():
    issue = str(row.get("Issue", "")).lower()
    subject = str(row.get("Subject", "")).lower()
    company = str(row.get("Company", "")).lower()

    full_text = issue + " " + subject

    # PRODUCT AREA DETECTION
    if "hackerrank" in company or any(word in full_text for word in [
        "assessment", "mock interview", "recruiter", "submission", "hackerrank"
    ]):
        product_area = "HackerRank Support"

    elif "claude" in company or any(word in full_text for word in [
        "claude", "workspace", "subscription", "anthropic", "conversation"
    ]):
        product_area = "Claude Help Center"

    elif "visa" in company or any(word in full_text for word in [
        "visa", "card", "payment", "transaction", "charge"
    ]):
        product_area = "Visa Support"

    else:
        product_area = "General Support"

    # REQUEST TYPE
    if any(word in full_text for word in [
        "bug", "error", "not working", "failed", "stopped",
        "issue", "problem", "broken", "crash", "crashed"
    ]):
        request_type = "bug"

    elif any(word in full_text for word in [
        "feature", "request", "suggestion", "improve",
        "upgrade", "new", "add"
    ]):
        request_type = "feature_request"

    elif full_text.strip() == "":
        request_type = "invalid"

    elif any(word in full_text for word in [
        "personally promised", "quantum", "mars",
        "secret call", "invisible transaction", "executive promise",
        "delete all", "steal", "bypass", "exploit", "hack system"
    ]):
        request_type = "invalid"

    else:
        request_type = "product_issue"

    # STATUS
    if request_type == "bug":
        status = "replied"
        justification = "Bug report suitable for automated triage."
    
    elif request_type == "invalid":
        status = "replied"
        justification = "Invalid, unsupported, or malicious request."
    
    elif "visa" in company and any(word in full_text for word in HIGH_RISK):
        status = "escalated"
        justification = "Sensitive financial or security issue requires human support."

    elif any(word in full_text for word in HIGH_RISK):
        status = "escalated"
        justification = "Sensitive or high-risk issue requires human support."

    else:
        status = "replied"
        justification = "Low-risk issue suitable for automated triage."

    # RESPONSE
    if status == "escalated":
        response = f"This issue requires escalation to {product_area} human support."
    else:
        response = f"Based on {product_area} guidance, please follow troubleshooting steps."

    # CONFIDENCE SCORE
    if request_type == "invalid":
        confidence = 0.95
    elif status == "escalated":
        confidence = 0.90
    elif request_type == "bug":
        confidence = 0.88
    elif request_type == "feature_request":
        confidence = 0.87
    elif request_type == "product_issue" and product_area != "General Support":
        confidence = 0.89
    else:
        confidence = 0.85

    # SAVE RESULT
    results.append({
        "status": status,
        "product_area": product_area,
        "response": response,
        "justification": justification,
        "request_type": request_type,
        "confidence": confidence
    })

# Save predictions
output_df = pd.DataFrame(results)

output_path = "predictions.csv"
output_df.to_csv(output_path, index=False)

print(f"Done! Predictions saved to {output_path}")