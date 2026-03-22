# AI Release Notes Generator

An AI-powered generator that converts raw Git commits from CodePipeline into business-readable release notes with technical details.

## Overview

This project uses a local LLM (Ollama with llama3.2) to analyze Git commits and generate structured release notes. The generated notes include:

- **Auto-categorization**: FEATURE, HOTFIX, INFRA, or SECURITY
- **Business Summary**: Plain-English summary for non-technical stakeholders
- **Technical Details**: Engineer-focused technical changes
- **Impact Assessment**: LOW, MEDIUM, or HIGH risk rating
- **Rollback Instructions**: How to revert if needed

## Supported Release Types

1. **FEATURE**: New functionality releases
2. **HOTFIX**: Critical production bug fixes
3. **INFRA**: Infrastructure and deployment changes
4. **SECURITY**: Security patches and hardening

## Stack

- **Language**: Python 3.10+
- **LLM**: Ollama (localhost:11434) with llama3.2 model
- **Dependencies**: openai

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with the llama3.2 model:

```bash
ollama serve
# In another terminal:
ollama pull llama3.2
```

## Usage

Run the generator for all four commit batches:

```bash
py main.py
```

This will:
1. Process each of the four commit batches
2. Generate structured release notes
3. Display raw release notes output
4. Print Slack-style release announcements

## Output Format

The generator outputs release notes in this exact format:

```
VERSION:    v1.3.0
DATE:       2024-03-15
TYPE:       FEATURE
SUMMARY:    2-3 sentence summary for business stakeholders
CHANGES:    1. Change 1
            2. Change 2
            3. Change 3
TECHNICAL:  1. Technical detail 1
            2. Technical detail 2
IMPACT:     MEDIUM
ROLLBACK:   One sentence on rollback procedure
```

## Slack Integration

The tool generates Slack-style announcements with:
- Channel based on environment (#releases-prod, #releases-staging)
- Special formatting for URGENT (HOTFIX/SECURITY) releases
- Celebration formatting for FEATURE releases
- Clear sections for summary, changes, technical details, and rollback

## Example

Input (Commits):
```
[a1b2c3d] feat(payments): add Stripe payment integration (alice@company.com)
[e4f5g6h] fix(api): resolve null pointer in payment callback (bob@company.com)
```

Output:
```
VERSION:    v1.3.0
DATE:       2024-03-15
TYPE:       FEATURE
SUMMARY:    This release adds Stripe payment integration for checkout and fixes a null pointer issue in the payment callback handler. Users will experience improved checkout reliability.
CHANGES:    1. Added Stripe payment integration
            2. Fixed null pointer in payment callback
            3. Updated stripe library to v24.0.0
TECHNICAL:  1. Added src/payments/stripe_client.py
            2. Fixed callback handling in src/payments/callbacks.py
            3. Updated requirements.txt with stripe>=24.0.0
IMPACT:     MEDIUM
ROLLBACK:   Revert the commit in CodePipeline to roll back.
```

## Features

- **Four-Layer Termination Safety**:
  1. Checks all 8 required fields are present
  2. Maximum 3 retries with exponential backoff
  3. 90-second timeout per request
  4. Loop detection to break on repeated outputs

- **Auto-categorization**: Determines release type from commit messages

- **Environment-aware**: Generates appropriate Slack channel based on environment

## License

MIT