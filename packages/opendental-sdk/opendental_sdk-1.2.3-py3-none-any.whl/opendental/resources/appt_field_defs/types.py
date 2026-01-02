"""Types for Appt Field Defs resource."""

from enum import Enum


class ApptFieldType(str, Enum):
    """Appointment field types."""
    
    TEXT = "Text"
    PICK_LIST = "PickList"

