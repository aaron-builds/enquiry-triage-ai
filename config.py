# ============================================================
# CLIENT CONFIGURATION — change these for each new client
# All business-specific values live here, never in the logic.
# ============================================================

# The model to use. Swappable without touching triage logic.
MODEL = "claude-sonnet-4-6"

# One sentence describing what this business does.
# Used in the system prompt so Claude has context.
BUSINESS_CONTEXT = (
    "We are a UK-based software consultancy that builds web apps, "
    "APIs, and AI tools for small and medium businesses."
)

# The categories Claude must choose from.
# Edit this list for any client — sales, billing, hr, legal, etc.
CATEGORIES = ["sales", "support", "billing", "spam", "other"]

# Urgency levels — usually fine to leave as-is.
URGENCY_LEVELS = ["high", "medium", "low"]

# Where to append classification results.
RESULTS_FILE = "results/log.jsonl"
