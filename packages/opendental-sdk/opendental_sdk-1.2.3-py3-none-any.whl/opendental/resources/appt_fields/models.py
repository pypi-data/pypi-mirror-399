"""Appt Field models for Open Dental SDK."""

from typing import Optional
from pydantic import Field

from ...base.models import BaseModel


class ApptField(BaseModel):
    """
    ApptField model matching Open Dental API specification.
    
    An ApptField is a highly customizable field that shows on appointments.
    Fields must be set up in Open Dental UI under Setup > Appointments > Appointment Field Defs
    before they can be used via the API.
    
    Version Added: 21.1
    """
    
    field_name: str = Field(..., alias="FieldName", description="Name of the appointment field")
    apt_num: int = Field(..., alias="AptNum", description="FK to appointment.AptNum")
    field_value: str = Field("", alias="FieldValue", description="Value of the appointment field")


class SetApptFieldRequest(BaseModel):
    """
    Request model for setting an appointment field value.
    
    If the ApptField already exists, it will be updated with the new value.
    If the ApptField does not exist, it will be created.
    """
    
    field_name: str = Field(..., alias="FieldName", description="Name of the appointment field")
    apt_num: int = Field(..., alias="AptNum", description="FK to appointment.AptNum")
    field_value: str = Field(..., alias="FieldValue", description="Value to set for the appointment field")

