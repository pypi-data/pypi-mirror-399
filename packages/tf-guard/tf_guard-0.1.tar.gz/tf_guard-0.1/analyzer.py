import os
from openai import OpenAI
import json

# This is the fixed structure that will never change
REPORT_TEMPLATE = """
# 🛡️ TF-GUARD RISK REPORT
---
## 📋 EXECUTIVE SUMMARY
{Brief overview of what is changing in plain English}

## ⚠️ RISK ASSESSMENT
| Resource | Action | Risk Level | Detail |
| :--- | :--- | :--- | :--- |
| {Resource Name} | {Create/Delete/Replace} | {Low/High} | {Reason for the risk} |

## 🔒 SECURITY & COMPLIANCE
- {Check for open ports, unencrypted disks, or IAM changes}

## 🚦 FINAL VERDICT
**Rating:** {SAFE | CAUTION | CRITICAL}
**Recommendation:** {One sentence advice}
---
"""

def analyze_plan(changes):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # We instruct the AI to use the template exactly
    prompt = f"""
    Analyze the following Terraform changes and fit your analysis EXACTLY into the Markdown template provided.
    
    CHANGES:
    {json.dumps(changes, indent=2)}

    TEMPLATE:
    {REPORT_TEMPLATE}
    
    IMPORTANT: Do not add extra conversational text. Only return the populated Markdown template.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a deterministic infrastructure auditor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2  # Lower temperature makes the AI more consistent/less creative
    )
    return response.choices[0].message.content