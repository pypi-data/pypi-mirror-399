"""
Epistemic Personality Profiles

Different AI behavior patterns implemented through vector thresholds.
Same architecture, different routing thresholds = different personalities.
"""

from typing import Dict


class PersonalityProfile:
    """Base personality configuration"""
    
    def __init__(self, name: str, thresholds: Dict[str, float], description: str):
        self.name = name
        self.thresholds = thresholds
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "thresholds": self.thresholds,
            "description": self.description
        }


# ============================================================================
# Personality Profiles
# ============================================================================

CAUTIOUS_RESEARCHER = PersonalityProfile(
    name="cautious_researcher",
    thresholds={
        "uncertainty_tolerance": 0.4,  # Low tolerance - investigate early
        "context_threshold": 0.6,      # High requirement - need deep context
        "know_threshold": 0.8,          # High bar for confidence
        "clarity_threshold": 0.7        # Need very clear requirements
    },
    description="Low uncertainty tolerance, investigates early and often, high confidence bar"
)

PRAGMATIC_IMPLEMENTER = PersonalityProfile(
    name="pragmatic_implementer",
    thresholds={
        "uncertainty_tolerance": 0.7,  # High tolerance - move forward with some doubt
        "context_threshold": 0.4,      # Low requirement - minimal context OK
        "know_threshold": 0.6,          # Lower bar for confidence
        "clarity_threshold": 0.5        # OK with moderate clarity
    },
    description="Action-oriented, tolerates uncertainty, implements with partial knowledge"
)

BALANCED_ARCHITECT = PersonalityProfile(
    name="balanced_architect",
    thresholds={
        "uncertainty_tolerance": 0.6,  # Moderate tolerance
        "context_threshold": 0.5,      # Moderate context requirement
        "know_threshold": 0.7,          # Moderate confidence bar
        "clarity_threshold": 0.6        # Moderate clarity requirement
    },
    description="Balanced approach, systematic but not overly cautious, standard defaults"
)

ADAPTIVE_LEARNER = PersonalityProfile(
    name="adaptive_learner",
    thresholds={
        "uncertainty_tolerance": 0.5,  # Starts moderate
        "context_threshold": 0.5,      # Starts moderate
        "know_threshold": 0.7,          # Starts moderate
        "clarity_threshold": 0.6        # Starts moderate
    },
    description="Learns optimal thresholds from outcomes, adapts behavior over time"
)


# ============================================================================
# Personality Registry
# ============================================================================

PERSONALITIES = {
    "cautious_researcher": CAUTIOUS_RESEARCHER,
    "pragmatic_implementer": PRAGMATIC_IMPLEMENTER,
    "balanced_architect": BALANCED_ARCHITECT,
    "adaptive_learner": ADAPTIVE_LEARNER
}


def get_personality(name: str) -> PersonalityProfile:
    """Get personality by name, default to balanced_architect"""
    return PERSONALITIES.get(name, BALANCED_ARCHITECT)


def list_personalities() -> Dict[str, Dict]:
    """List all available personalities"""
    return {
        name: profile.to_dict()
        for name, profile in PERSONALITIES.items()
    }
