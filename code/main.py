import pandas as pd
import os

# Load input CSV
input_path = "data/support_issues.csv"

if not os.path.exists(input_path):
    print(f"File not found: {input_path}")
    exit()

df = pd.read_csv(input_path)

results = []

# High-risk words that require escalation
HIGH_RISK = [
    "fraud", "stolen", "unauthorized", "hacked",
    "scam", "chargeback", "legal", "compromised"
]

# Process each support issue
for _, row in df.iterrows():

    issue = str(row.get("issue", "")).lower()
    subject = str(row.get("subject", "")).lower()
    company = str(row.get("company", "")).lower()

    full_text = issue + " " + subject

    # PRODUCT AREA DETECTION
    if "hackerrank" in company:
        product_area = "HackerRank Support"
    elif "claude" in company:
        product_area = "Claude Help Center"
    elif "visa" in company:
        product_area = "Visa Support"
    else:
        if any(word in full_text for word in ["assessment", "coding", "test"]):
            product_area = "HackerRank Support"
        elif any(word in full_text for word in ["subscription", "billing", "claude"]):
            product_area = "Claude Help Center"
        elif any(word in full_text for word in ["card", "payment", "visa"]):
            product_area = "Visa Support"
        else:
            product_area = "General Support"

    # REQUEST TYPE CLASSIFICATION
    if any(word in full_text for word in ["feature", "request", "add"]):
        request_type = "feature_request"
    elif any(word in full_text for word in ["bug", "error", "crash", "not working", "failed"]):
        request_type = "bug"
    elif full_text.strip() == "":
        request_type = "invalid"
    else:
        request_type = "product_issue"

    # STATUS + RESPONSE
    if any(word in full_text for word in HIGH_RISK):
        status = "escalated"
        response = "This issue may involve sensitive security, billing, or fraud concerns and should be escalated to human support."
        justification = "High-risk or sensitive keywords detected."
    elif request_type == "invalid":
        status = "replied"
        response = "This request appears out of scope or lacks actionable support information."
        justification = "Invalid or irrelevant request."
    else:
        status = "replied"
        response = f"Based on {product_area} support guidance, please follow the relevant troubleshooting or account support steps."
        justification = "Low-risk issue suitable for automated triage."

    # Save result
    results.append({
        "status": status,
        "product_area": product_area,
        "response": response,
        "justification": justification,
        "request_type": request_type
    })

# Save predictions
output_df = pd.DataFrame(results)

output_path = "predictions.csv"
output_df.to_csv(output_path, index=False)

print(f"Done! Predictions saved to {output_path}")
