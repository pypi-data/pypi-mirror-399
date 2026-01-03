# analyzer.py
from openai import OpenAI
import json

REPORT_TEMPLATE = """
FTL-TF RISK REPORT
==================================================

EXECUTIVE SUMMARY
--------------------------------------------------
{summary}

RISK ASSESSMENT
--------------------------------------------------
{risk_table}

FINAL VERDICT
--------------------------------------------------
Rating: {rating}
Recommendation: {recommendation}

==================================================
"""


def analyze_plan(changes, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You MUST output only the following Markdown template.
    Do not add, remove, rename, or reorder any sections.
    Do not add commentary outside the template.
    If information is missing, write "N/A" where appropriate.
    {REPORT_TEMPLATE}

    DATA:
    {json.dumps(changes, indent=2)}
    
    Focus strictly on:
        - Resource deletions
        - Resource replacements
        - Security group ingress/egress risks
    """
    
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": "You are a professional SRE and cloud security auditor."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )
    return response.output_text
    

    