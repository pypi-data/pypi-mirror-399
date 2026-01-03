# analyzer.py
from openai import OpenAI
import json


def analyze_plan(changes, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a professional SRE and cloud security auditor.

Analyze the Terraform changes below.

You MUST return ONE risk entry per resource change.
Do NOT omit resources, even if there is no risk.

Return ONLY valid JSON in the following structure:

{{
  "summary": "<executive summary covering all changes>",
  "risks": [
    {{
      "resource": "<terraform address>",
      "action": "<create|update|delete|destroy>",
      "what": "<plain-English description of what is being created or changed>",
      "description": "<risk explanation or 'No significant risk identified'>",
      "severity": "<None|Low|Medium|High|Critical>"
    }}
  ],
  "rating": "<overall rating>",
  "recommendation": "<final recommendation>"
}}

Rules:
- There must be exactly ONE risks[] entry per resource in the input
- The 'what' field must describe the resource purpose (example: 'Azure Front Door WAF policy in Detection mode')
- Severity must be one of: None, Low, Medium, High, Critical
- Use 'None' or 'Low' for safe resource creations
- Do NOT summarize multiple resources into one entry
- Do NOT return Markdown
- Do NOT add commentary outside JSON

DATA:
{json.dumps(changes, indent=2)}
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": "You are a senior cloud security auditor."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.output_text
