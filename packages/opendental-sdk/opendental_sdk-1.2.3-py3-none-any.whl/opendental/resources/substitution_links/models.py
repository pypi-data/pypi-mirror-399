"""Substitution Links models for Open Dental SDK."""

from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class SubstitutionLink(BaseModel):
    """
    Substitution Link model.
    
    Represents insurance procedure code substitutions/downgrades.
    When an insurance company substitutes one procedure code for another 
    (typically a less expensive alternative).
    """
    
    # Primary identifier
    id: int = Field(..., alias="SubstitutionLinkNum", description="Substitution link number (primary key)")
    
    # Required fields per API spec
    plan_num: int = Field(..., alias="PlanNum", description="FK to InsPlan.PlanNum")
    code_num: int = Field(..., alias="CodeNum", description="FK to ProcedureCode.CodeNum")
    substitution_code: str = Field(..., alias="SubstitutionCode", description="FK to ProcedureCode.ProcCode (case-sensitive)")
    subst_only_if: str = Field(..., alias="SubstOnlyIf", description="Condition: Always, Molar, SecondMolar, Never, or Posterior")


class CreateSubstitutionLinkRequest(BaseModel):
    """Request model for creating a new substitution link."""
    
    # Required fields per API spec
    plan_num: int = Field(..., alias="PlanNum", description="FK to InsPlan.PlanNum (required)")
    code_num: int = Field(..., alias="CodeNum", description="FK to ProcedureCode.CodeNum (required)")
    substitution_code: str = Field(..., alias="SubstitutionCode", description="FK to ProcedureCode.ProcCode - case-sensitive (required)")
    subst_only_if: str = Field(..., alias="SubstOnlyIf", description="Either 'Always', 'Molar', 'SecondMolar', 'Never', or 'Posterior' (required)")


class UpdateSubstitutionLinkRequest(BaseModel):
    """Request model for updating an existing substitution link."""
    
    # Optional fields per API spec - only SubstitutionCode and SubstOnlyIf can be updated
    substitution_code: Optional[str] = Field(None, alias="SubstitutionCode", description="FK to ProcedureCode.ProcCode - case-sensitive")
    subst_only_if: Optional[str] = Field(None, alias="SubstOnlyIf", description="Either 'Always', 'Molar', 'SecondMolar', 'Never', or 'Posterior'")


class SubstitutionLinkListResponse(BaseModel):
    """Response model for substitution link list operations."""
    
    substitution_links: List[SubstitutionLink]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None


class SubstitutionLinkSearchRequest(BaseModel):
    """Request model for searching substitution links."""
    
    # Search parameters per API spec
    plan_num: Optional[int] = Field(None, alias="PlanNum", description="FK to InsPlan.PlanNum")
    code_num: Optional[int] = Field(None, alias="CodeNum", description="FK to ProcedureCode.CodeNum")
    substitution_code: Optional[str] = Field(None, alias="SubstitutionCode", description="Procedure code string")
    
    # Pagination
    page: Optional[int] = 1
    per_page: Optional[int] = 50

