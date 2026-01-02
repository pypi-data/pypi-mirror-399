"""Substitution Links types and enums for Open Dental SDK."""

from enum import Enum


class SubstitutionCondition(str, Enum):
    """
    Substitution conditions per Open Dental API spec.
    
    These define when an insurance company will substitute one procedure 
    code for another (typically a less expensive alternative).
    """
    ALWAYS = "Always"  # Always substitute
    MOLAR = "Molar"  # Only substitute for molar teeth
    SECOND_MOLAR = "SecondMolar"  # Only substitute for second molars
    NEVER = "Never"  # Never substitute
    POSTERIOR = "Posterior"  # Only substitute for posterior (back) teeth

