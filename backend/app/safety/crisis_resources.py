"""Crisis resources — regional hotline data and the standard crisis response.

Surfaced by the Safe Set layer and the frontend crisis interrupt.
"""

from __future__ import annotations

# Region key -> list of (label, contact)
CRISIS_RESOURCES: dict[str, list[tuple[str, str]]] = {
    "US": [
        ("Suicide & Crisis Lifeline", "988"),
        ("Crisis Text Line", "Text HOME to 741741"),
        ("Emergency", "911"),
    ],
    "UK": [
        ("Samaritans", "116 123"),
        ("Crisis Text Line", "Text SHOUT to 85258"),
        ("Emergency", "999"),
    ],
    "CA": [
        ("Talk Suicide Canada", "1-833-456-4566"),
        ("Crisis Text Line", "Text CONNECT to 686868"),
        ("Emergency", "911"),
    ],
    "AU": [
        ("Lifeline", "13 11 14"),
        ("Emergency", "000"),
    ],
    "EU": [
        ("EU Emergency", "112"),
        ("Emotional support", "116 123"),
    ],
}

# Specialized resources by concern. Kept accurate per behaviour rules
# (e.g. eating disorders -> National Alliance for Eating Disorders, NOT NEDA,
# whose helpline is permanently disconnected).
SPECIALIZED_RESOURCES: dict[str, list[tuple[str, str]]] = {
    "eating_disorder": [
        ("National Alliance for Eating Disorders", "1-866-662-1235"),
    ],
    "substance_use": [
        ("SAMHSA National Helpline", "1-800-662-4357"),
    ],
    "domestic_violence": [
        ("National Domestic Violence Hotline", "1-800-799-7233"),
    ],
}

# Short inline block used inside text fallbacks (provider-independent).
CRISIS_RESPONSE = (
    "I'm really glad you said it out loud. Please contact live support now: 988 in the US, "
    "116 123 in the UK, 13 11 14 in Australia, or text HOME to 741741. If you can, reach out "
    "to someone near you too."
)


def crisis_resource_block() -> str:
    """One-line crisis contacts for embedding in safe-fallback text."""
    return (
        "Please contact live support now: 988 in the US, 116 123 in the UK, 13 11 14 in "
        "Australia, or text HOME to 741741. If someone nearby can be with you, reach out to them too."
    )


def all_resources() -> dict[str, dict[str, list[dict[str, str]]]]:
    """Structured form for the API / frontend crisis interrupt."""
    def shape(d):
        return {k: [{"label": l, "contact": c} for l, c in v] for k, v in d.items()}
    return {"regional": shape(CRISIS_RESOURCES), "specialized": shape(SPECIALIZED_RESOURCES)}
