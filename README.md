# Enquiry Triage System

Automatically classifies incoming customer messages (emails, contact forms, support tickets) by category, urgency, and intent — then drafts a first response. Powered by the Anthropic API with structured output so the JSON is always reliable.

## The business problem it solves

Every business drowns in unstructured inbound messages. Triaging them manually wastes time and causes slow responses to urgent issues. This system reads each message and instantly returns a structured classification that can route tickets, prioritise queues, or draft responses — without a human reading every one first.

## Tech stack

- Python 3.11+
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- `python-dotenv` for secret management

## Configuring for a new client

Open `config.py` and change three things:

| Variable | What to change |
|---|---|
| `BUSINESS_CONTEXT` | One sentence about what the client's business does |
| `CATEGORIES` | The list of categories that match their workflow |
| `MODEL` | Swap to a different Claude model if needed |

No other files need to change. The prompt and tool schema pick up your config automatically.

## Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd enquiry-triage

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install anthropic python-dotenv

# 4. Add your API key
cp .env.example .env
# Edit .env and paste your Anthropic API key

# 5. Run with the sample input
python run.py sample_input.json

# Or run with the built-in test message
python run.py
```

## Output

Results are printed to the console and appended to `results/log.jsonl`. Each line is a JSON record with a timestamp, message preview, and all four classification fields.

## How it works (for interviews)

1. `run.py` loads the message and calls `triage()` in `triage.py`
2. `triage.py` sends the message to Claude with a **tool definition** — a JSON schema describing exactly what fields to return
3. `tool_choice: any` forces Claude to call the tool rather than reply in plain text, so the output is always valid structured JSON
4. The result is extracted from `response.content` — no text parsing needed
5. `run.py` prints a summary and logs the result to `results/log.jsonl`
