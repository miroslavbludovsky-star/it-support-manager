from app.config import get_settings
from app.models.email import EmailCategory

import re

# Pattern for JIRA ticket key: PROJECT-SUBPROJECT-NUMBER (e.g., UDR-MMMB-2626)
JIRA_KEY_PATTERN = re.compile(r"[A-Z]+-[A-Z0-9]+-\d+")


def classify_email(sender_email: str, body_text: str) -> EmailCategory:
    """Classify email as JIRA notification, internal, or external.

    Rules:
    - sender == jira_sender AND body contains JIRA structure → "jira"
    - sender domain == "marbes.cz" → "internal"
    - else → "external"
    """
    settings = get_settings()
    jira_sender = settings.jira_sender.lower()
    sender = sender_email.lower().strip()

    # Check for JIRA notification
    if sender == jira_sender and JIRA_KEY_PATTERN.search(body_text):
        return EmailCategory.JIRA

    # Check for internal email
    if sender.endswith("@marbes.cz"):
        return EmailCategory.INTERNAL

    return EmailCategory.EXTERNAL
