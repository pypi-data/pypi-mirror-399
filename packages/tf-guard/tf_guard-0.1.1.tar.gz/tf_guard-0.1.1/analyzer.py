from openai import OpenAI
import json

REPORT_TEMPLATE = """
# 🛡️ TF-GUARD RISK REPORT
---
## 📋 EXECUTIVE SUMMARY
{summary}

## ⚠️ RISK ASSESSMENT
{risk_table}

## 🚦 FINAL VERDICT
**Rating:** {rating}
**Recommendation:** {recommendation}
---
"""

def analyze_plan(changes, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Analyze these Terraform changes for security risks and destructive actions.
    Fit your analysis EXACTLY into this Markdown template:
    {REPORT_TEMPLATE}

    DATA:
    {json.dumps(changes, indent=2)}
    
    Focus on: Deletions, replacements, and wide-open security groups.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional SRE and cloud security auditor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content