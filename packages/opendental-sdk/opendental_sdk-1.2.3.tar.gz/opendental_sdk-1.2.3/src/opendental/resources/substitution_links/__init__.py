"""Substitution Links resource module."""

from .client import SubstitutionLinksClient
from .models import (
    SubstitutionLink,
    CreateSubstitutionLinkRequest,
    UpdateSubstitutionLinkRequest,
    SubstitutionLinkListResponse,
    SubstitutionLinkSearchRequest,
)
from .types import SubstitutionCondition

__all__ = [
    "SubstitutionLinksClient",
    "SubstitutionLink",
    "CreateSubstitutionLinkRequest",
    "UpdateSubstitutionLinkRequest",
    "SubstitutionLinkListResponse",
    "SubstitutionLinkSearchRequest",
    "SubstitutionCondition",
]

