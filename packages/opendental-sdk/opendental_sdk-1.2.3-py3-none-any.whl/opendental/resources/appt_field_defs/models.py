"""Appt Field Def models for Open Dental SDK."""

from typing import Optional
from pydantic import Field

from ...base.models import BaseModel


class ApptFieldDef(BaseModel):
    """
    ApptFieldDef model matching Open Dental API specification.
    
    Appointment Field Defs allow you to organize notes specific to a patient's 
    appointment and are displayed in the bottom left of the Edit Appointment window.
    
    Version Added: 21.4
    """
    
    appt_field_def_num: int = Field(..., alias="ApptFieldDefNum", description="Primary key")
    field_name: str = Field(..., alias="FieldName", description="Name of the field")
    field_type: str = Field("Text", alias="FieldType", description="Either 'Text' or 'PickList'")
    pick_list: str = Field("", alias="PickList", description="Pick list items separated by \\r\\n (only used if FieldType is 'PickList')")


class CreateApptFieldDefRequest(BaseModel):
    """
    Request model for creating an appointment field definition.
    
    The API supports creating both Text type and PickList type ApptFieldDefs.
    Duplicate ApptFieldDefs are not allowed.
    """
    
    field_name: str = Field(..., alias="FieldName", description="Name of the field (required)")
    field_type: Optional[str] = Field(None, alias="FieldType", description="Either 'Text' or 'PickList'. Default is 'Text'")
    pick_list: Optional[str] = Field(None, alias="PickList", description="Only used if FieldType is 'PickList'. Items separated by \\r\\n")

