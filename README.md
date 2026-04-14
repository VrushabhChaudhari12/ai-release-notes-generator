# AI Release Notes Generator

> **Raw Git commits → structured, stakeholder-ready release notes in seconds.** Categorizes every deployment by type (FEATURE, HOTFIX, INFRA, SECURITY), extracts impact and rollback instructions, and fires a Slack notification — automatically.

---

## The Problem This Solves

After every CodePipeline deployment, someone has to manually write release notes: parse commits, assess impact, draft rollback steps. This takes 15–30 minutes per release. This tool reduces that to a single command and eliminates human error in risk assessment.

```bash
# Before: 20 minutes of manual documentation
# After:
python main.py --pipelines backend_api frontend_app
```

---

## Output Format

Each deployment produces a structured JSON release note:

```json
{
  "VERSION": "v2.4.1",
  "DATE": "2024-01-15",
  "TYPE": "HOTFIX",
  "SUMMARY": "Critical fix for payment service timeout in production",
  "CHANGES": ["Fixed DB connection pool exhaustion", "Increased timeout from 30s to 60s"],
  "TECHNICAL": "Connection pool size increased from 10 to 50 in pg_config.py",
  "IMPACT": "HIGH",
  "ROLLBACK": "Revert commit abc123, restart payment-service pods"
}
```

---

## Release Types

| Type | Trigger | Risk |
|------|---------|------|
| `FEATURE` | New functionality merged to main | LOW/MEDIUM |
| `HOTFIX` | Critical bug fixed in production | HIGH |
| `INFRA` | Infrastructure or deployment changes | MEDIUM |
| `SECURITY` | Security patches and hardening | HIGH |

---

## Architecture

```
CodePipeline trigger
        |
        v
  mock_commits.py  ──── Simulates commit payload per pipeline
        |
        v
  prompts.py  ─────── System prompt + context-aware user message
        |
        v
  generator.py  ───── LLM call (Ollama/GPT-4)
        +── JSON parse & validate (all 8 required fields)
        +── Loop detection + exponential backoff retry
        |
        v
  slack_notifier.py  ── POST to Slack webhook
        |
        v
  Structured release note (JSON) + Slack alert
```

---

## Engineering Quality

| Feature | Implementation |
|---------|---------------|
| Config management | `config.py` — all settings via env vars with typed defaults |
| Structured logging | Python `logging` — timestamp, level, module |
| Output validation | 8 required JSON fields validated on every response |
| JSON parsing | Strips markdown fences, handles partial JSON |
| Retry logic | Exponential backoff (2^n seconds), max 3 retries |
| Loop detection | Deduplicates identical outputs |
| CLI interface | `argparse` — `--pipelines`, `--output-json`, `--no-slack` |
| Error isolation | Per-pipeline try/except, continues on failures |
| Slack integration | Webhook POST with release type color coding |

---

## Quick Start

### 1. Install Ollama + model
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3.2
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the generator
```bash
# All pipelines
python main.py

# Specific pipelines
python main.py --pipelines backend_api frontend_app

# Skip Slack, export JSON
python main.py --no-slack --output-json results.json
```

### 4. Configure Slack (optional)
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
export LOG_LEVEL=DEBUG
```

---

## Project Structure

```
ai-release-notes-generator/
├── main.py              # CLI entry point — argparse, orchestration
├── generator.py         # LLM call, JSON validation, retry + loop detection
├── prompts.py           # System prompt + context-aware message builder
├── config.py            # Centralized config with env var overrides
├── mock_commits.py      # Simulated commit payloads per pipeline
├── slack_notifier.py    # Slack webhook integration
└── requirements.txt     # openai
```

---

## Why This Matters (Resume Context)

This project demonstrates an AIOps use case that replaces manual release documentation:
- **JSON schema enforcement**: LLM output is parsed and validated for all 8 required fields — fails fast on partial output
- **Real DevOps integration**: Slack webhook with message color coding by release type (HOTFIX = red, FEATURE = green)
- **Production safety**: retry with backoff, loop detection, per-pipeline error isolation
- **Stakeholder-ready output**: SUMMARY for product managers, TECHNICAL for engineers, ROLLBACK for on-call SREs
- **LLM-agnostic**: swap Ollama → GPT-4 or Claude via two env vars
