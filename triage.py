"""
triage.py — Core enquiry triage logic.

Sends an enquiry to the Anthropic API using tool-calling so the
response is always structured JSON, never free text we have to parse.
"""

import json
import os

import anthropic
from dotenv import load_dotenv

from config import BUSINESS_CONTEXT, CATEGORIES, MODEL, URGENCY_LEVELS

# Load ANTHROPIC_API_KEY from .env into the environment.
load_dotenv()

# ============================================================
# PROMPT TEMPLATES
# Kept here, clearly labelled, so they're easy to edit.
# ============================================================

SYSTEM_PROMPT = f"""You are an expert customer communications triage assistant for the following business:

{BUSINESS_CONTEXT}

Your job is to read incoming enquiries and classify them accurately.
Always call the triage_enquiry function with your assessment.
Be concise. The summary must be one sentence. The draft response must be professional and friendly."""

# The tool definition tells Claude exactly what JSON shape to return.
# Claude is forced to call this tool — so we always get structured output.
TRIAGE_TOOL = {
    "name": "triage_enquiry",
    "description": "Classify an incoming enquiry and draft a first response.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": CATEGORIES,
                "description": "The best-fit category for this enquiry.",
            },
            "urgency": {
                "type": "string",
                "enum": URGENCY_LEVELS,
                "description": "How urgently this needs a response.",
            },
            "summary": {
                "type": "string",
                "description": "One sentence summarising what the sender wants.",
            },
            "draft_response": {
                "type": "string",
                "description": "A short, professional first-draft reply to the sender.",
            },
        },
        "required": ["category", "urgency", "summary", "draft_response"],
    },
}


def triage(message: str) -> dict:
    """
    Triage a single enquiry message.

    Args:
        message: The raw text of the enquiry (email body, form text, etc.)

    Returns:
        A dict with keys: category, urgency, summary, draft_response.

    Raises:
        ValueError: If the API does not return a tool call (unexpected response).
        RuntimeError: If the API call itself fails.
    """
    # Build the Anthropic client. It reads ANTHROPIC_API_KEY from the environment.
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            # tool_choice forces Claude to call our tool, not reply in plain text.
            tool_choice={"type": "any"},
            tools=[TRIAGE_TOOL],
            messages=[
                {
                    "role": "user",
                    "content": f"Please triage this enquiry:\n\n{message}",
                }
            ],
        )
    except anthropic.APIError as e:
        # Surface a clear message rather than a raw stack trace.
        raise RuntimeError(f"Anthropic API call failed: {e}") from e

    # Walk the response content blocks to find the tool_use block.
    # Claude may return multiple blocks; we want the one that is our tool call.
    for block in response.content:
        if block.type == "tool_use" and block.name == "triage_enquiry":
            # block.input is already a Python dict — no JSON parsing needed.
            return block.input

    # If we reach here, Claude replied without calling our tool.
    raise ValueError(
        f"Expected a tool_use response but got: {response.content}"
    )
 
if __name__ == "__main__": 
    test_message = "Hi, I was double charged and need this fixed urgently." 
    result = triage(test_message) 
    print(result) 
