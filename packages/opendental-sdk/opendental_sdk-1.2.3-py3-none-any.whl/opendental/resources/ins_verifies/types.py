"""Insurance Verification types for Open Dental SDK."""

from enum import Enum


class VerifyType(str, Enum):
    """
    Insurance verification type enumeration.
    
    Specifies whether the verification is for a patient's insurance eligibility
    or an insurance plan's benefits.
    """
    
    PATIENT_ENROLLMENT = "PatientEnrollment"
    """Verify a patient's insurance eligibility"""
    
    INSURANCE_BENEFIT = "InsuranceBenefit"
    """Verify an insurance plan's benefits"""

