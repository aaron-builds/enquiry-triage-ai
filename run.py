"""
run.py — Entry point for the enquiry triage system.

Usage:
    python run.py sample_input.json      # triage a message from a file
    python run.py                        # triage a hardcoded test message

The result is printed to the console and appended to the results log.
"""

import json
import os
import sys
from datetime import datetime, timezone

from triage import triage
from config import RESULTS_FILE


def load_message(path: str) -> str:
    """Read the enquiry text from a JSON file with a 'message' key."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["message"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Could not load message from {path}: {e}") from e


def log_result(message: str, result: dict) -> None:
    """Append the triaged result to the JSONL results file."""
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_preview": message[:120],  # first 120 chars for reference
        **result,
    }
    try:
        with open(RESULTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        print(f"Warning: could not write to results log: {e}")


def print_summary(result: dict) -> None:
    """Print a clean, readable summary of the triage result."""
    print("\n" + "=" * 50)
    print("  ENQUIRY TRIAGE RESULT")
    print("=" * 50)
    print(f"  Category : {result['category'].upper()}")
    print(f"  Urgency  : {result['urgency'].upper()}")
    print(f"  Summary  : {result['summary']}")
    print("-" * 50)
    print("  Draft Response:")
    print()
    # Indent each line of the draft response for readability.
    for line in result["draft_response"].splitlines():
        print(f"    {line}")
    print("=" * 50 + "\n")


def main():
    # If a file path is passed as an argument, load the message from it.
    # Otherwise fall back to a built-in test message.
    if len(sys.argv) > 1:
        message = load_message(sys.argv[1])
        print(f"Loaded message from: {sys.argv[1]}")
    else:
        message = (
            "Hi, I saw your website and I'm interested in getting a quote "
            "for building a customer portal for my business. We have about "
            "50 staff and need something that integrates with Salesforce. "
            "Can you let me know your rates and typical timelines?"
        )
        print("Using built-in test message.")

    print("Sending to Anthropic API for triage...")

    try:
        result = triage(message)
    except (RuntimeError, ValueError) as e:
        print(f"\nError: {e}")
        sys.exit(1)

    print_summary(result)
    log_result(message, result)
    print(f"Result logged to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
