"""Types for Appt Fields resource."""

from enum import Enum


class ApptFieldType(str, Enum):
    """Common appointment field types (examples)."""
    
    INS_VERIFIED = "Ins Verified"
    REMINDER_SENT = "Reminder Sent"
    CONFIRMED_BY = "Confirmed By"
    SPECIAL_INSTRUCTIONS = "Special Instructions"

