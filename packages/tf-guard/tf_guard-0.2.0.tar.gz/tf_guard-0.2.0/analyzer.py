# analyzer.py
from openai import OpenAI
import json


def analyze_plan(changes, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a professional SRE and cloud security auditor.

Analyze the Terraform changes below.

Return ONLY valid JSON in the following structure:

{{
  "summary": "<executive summary>",
  "risks": [
    {{
      "resource": "<terraform address>",
      "action": "<create|update|delete|destroy>",
      "description": "<risk explanation>",
      "severity": "<Low|Medium|High|Critical>"
    }}
  ],
  "rating": "<overall rating>",
  "recommendation": "<final recommendation>"
}}

Rules:
- Do NOT return Markdown
- Do NOT include commentary outside JSON
- Severity must be one of: Low, Medium, High, Critical

DATA:
{json.dumps(changes, indent=2)}
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": "You are a senior cloud security auditor."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.output_text
