# FTL-TF
**AI-Powered Risk Analysis for Terraform Plans**

FTL-TF is a CLI tool designed to bridge the gap between `terraform plan` and manual code review. It uses OpenAI's GPT models to analyze infrastructure changes, identify security risks, and provide a human-readable safety audit before you hit apply.

---

## Features
- **AI Security Audit**: Automatically analyzes resource deletions, replacements, and security group openings.
- **Smart Variable Discovery**: Automatically finds your `.tfvars` files in the root or `/vars` subdirectories.
- **Rich Output**: Beautiful, scannable terminal reports powered by the `rich` library.
- **Lightning Fast**: Optimized JSON parsing to minimize token usage and latency.

---

## Quick Start

### Installation
```bash
pip install ftltf