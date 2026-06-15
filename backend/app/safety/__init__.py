"""Safe Set — Stillframe's safety & crisis layer.

Ported from the foundation repo's deterministic wellness safety supervisor.
No provider call may bypass this layer.
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
