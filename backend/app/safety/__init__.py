"""Safe Set — Stillframe's deterministic safety & crisis layer.

Always on, provider-agnostic, primary. No provider call may bypass it. When a
strong cloud model (e.g. Claude) is configured, it can act as an added safety
reviewer, but this deterministic layer never depends on a third party.
"""

from .supervisor import (
    WellnessSafetySupervisor,
    StreamSafetyBuffer,
    UserSafetyDecision,
    AssistantSafetyDecision,
    detect_crisis,
)

__all__ = [
    "WellnessSafetySupervisor",
    "StreamSafetyBuffer",
    "UserSafetyDecision",
    "AssistantSafetyDecision",
    "detect_crisis",
]
