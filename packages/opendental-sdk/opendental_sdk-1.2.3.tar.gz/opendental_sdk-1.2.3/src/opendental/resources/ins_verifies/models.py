"""InsVerify models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class InsVerify(BaseModel):
    """
    Insurance Verification model matching Open Dental API specification.
    
    InsVerify tracks insurance verification status for both patient eligibility
    and insurance plan benefits.
    
    Reference: https://www.opendental.com/site/apiinsverifies.html
    Version Added: 21.1
    """
    
    # Primary key
    ins_verify_num: int = Field(..., alias="InsVerifyNum", description="Insurance verification number (primary key)")
    
    # Verification details
    date_last_verified: Optional[date] = Field(None, alias="DateLastVerified", description="Date last verified")
    user_num: int = Field(0, alias="UserNum", description="User who performed the verification")
    verify_type: str = Field(..., alias="VerifyType", description="Type: PatientEnrollment or InsuranceBenefit")
    f_key: int = Field(..., alias="FKey", description="FK to patplan.PatPlanNum or insplan.PlanNum depending on VerifyType")
    def_num: int = Field(0, alias="DefNum", description="FK to definition.DefNum where Category=38")
    note: Optional[str] = Field("", alias="Note", description="Status note for this insurance verification")
    date_last_assigned: Optional[date] = Field(None, alias="DateLastAssigned", description="Date last assigned")
    
    # Timestamp
    sec_date_t_edit: Optional[datetime] = Field(None, alias="SecDateTEdit", description="Last edit timestamp")


class UpdateInsVerifyRequest(BaseModel):
    """
    Request model for updating/creating an insurance verification.
    
    The Open Dental API uses PUT for both creating and updating InsVerifies.
    Historical entries are retained in the insverifyhist table.
    """
    
    # Verification date (optional after v24.1.17)
    date_last_verified: Optional[str] = Field(None, alias="DateLastVerified", description="Date in yyyy-MM-dd format")
    
    # Required fields
    verify_type: str = Field(..., alias="VerifyType", description="PatientEnrollment or InsuranceBenefit")
    f_key: int = Field(..., alias="FKey", description="PatPlanNum (PatientEnrollment) or PlanNum (InsuranceBenefit)")
    
    # Optional fields
    def_num: Optional[int] = Field(None, alias="DefNum", description="Definition number where Category=38")
    note: Optional[str] = Field(None, alias="Note", description="Status note")
    
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        populate_by_name = True


class InsVerifyListResponse(BaseModel):
    """Response model for insurance verification list operations."""
    
    ins_verifies: List[InsVerify] = Field(default_factory=list, description="List of insurance verifications")
    total: int = Field(0, description="Total number of verifications")
    page: Optional[int] = Field(None, description="Current page")
    per_page: Optional[int] = Field(None, description="Items per page")

