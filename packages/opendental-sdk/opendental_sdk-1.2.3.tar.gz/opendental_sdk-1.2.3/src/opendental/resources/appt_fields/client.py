"""Appt Fields client for Open Dental SDK."""

from typing import Union, Dict, Any
from ...base.resource import BaseResource
from .models import ApptField, SetApptFieldRequest


class ApptFieldsClient(BaseResource):
    """
    Client for managing appointment fields in Open Dental.
    
    ApptFields are highly customizable fields that show on appointments.
    Before using the API, the field must be set up in Open Dental UI under:
    Setup > Appointments > Appointment Field Defs
    
    Additional configuration may be needed to show the field in Appt Views and/or Appt Bubble.
    
    See: https://www.opendental.com/site/apiapptfields.html
    Version Added: 21.1
    """
    
    def __init__(self, client):
        """Initialize the appt fields client."""
        super().__init__(client, "apptfields")
    
    def get(self, apt_num: Union[int, str], field_name: str) -> ApptField:
        """
        Get an appointment field value.
        
        If an ApptField exists for the appointment, returns the value.
        If an ApptField does not exist, returns an empty string for FieldValue.
        
        Version Added: 21.1
        
        Args:
            apt_num: Appointment number (AptNum)
            field_name: Name of the field (must match field defined in Open Dental UI)
            
        Returns:
            ApptField: The appointment field with its value
            
        Example:
            # Get insurance verification status
            field = client.appt_fields.get(
                apt_num=101,
                field_name="Ins Verified"
            )
            print(f"Insurance verified: {field.field_value}")
        """
        apt_num = self._validate_id(apt_num)
        
        params = {
            "AptNum": apt_num,
            "FieldName": field_name
        }
        
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        return self._handle_response(response, ApptField)
    
    def set(
        self,
        apt_num: Union[int, str],
        field_name: str,
        field_value: str
    ) -> None:
        """
        Set an appointment field value.
        
        If an ApptField already exists for the appointment, it will be updated with the new value.
        If an ApptField does not yet exist, a new one will be created.
        
        Version Added: 21.1
        
        Args:
            apt_num: Appointment number (AptNum)
            field_name: Name of the field (must match field defined in Open Dental UI)
            field_value: Value to set for the field
            
        Example:
            # Mark insurance as verified
            client.appt_fields.set(
                apt_num=101,
                field_name="Ins Verified",
                field_value="Yes"
            )
            
            # Add special instructions
            client.appt_fields.set(
                apt_num=101,
                field_name="Special Instructions",
                field_value="Patient needs wheelchair access"
            )
        """
        apt_num = self._validate_id(apt_num)
        
        data = {
            "AptNum": apt_num,
            "FieldName": field_name,
            "FieldValue": field_value
        }
        
        endpoint = self._build_endpoint()
        self._put(endpoint, json_data=data)
    
    def set_field(
        self,
        apt_data: Union[SetApptFieldRequest, Dict[str, Any]]
    ) -> None:
        """
        Set an appointment field value using a request model or dictionary.
        
        This is an alternative method that accepts a model or dictionary instead of
        individual parameters.
        
        Version Added: 21.1
        
        Args:
            apt_data: SetApptFieldRequest model or dictionary with:
                - AptNum: Required. Appointment number
                - FieldName: Required. Name of the field
                - FieldValue: Required. Value to set
                
        Example:
            # Using a dictionary
            client.appt_fields.set_field({
                "AptNum": 101,
                "FieldName": "Ins Verified",
                "FieldValue": "Yes"
            })
            
            # Using a model
            from opendental.resources.appt_fields import SetApptFieldRequest
            request = SetApptFieldRequest(
                apt_num=101,
                field_name="Ins Verified",
                field_value="Yes"
            )
            client.appt_fields.set_field(request)
        """
        if isinstance(apt_data, dict):
            data = apt_data
        else:
            data = apt_data.model_dump(exclude_none=True, by_alias=True)
        
        endpoint = self._build_endpoint()
        self._put(endpoint, json_data=data)
    
    def clear(
        self,
        apt_num: Union[int, str],
        field_name: str
    ) -> None:
        """
        Clear an appointment field value by setting it to an empty string.
        
        Args:
            apt_num: Appointment number (AptNum)
            field_name: Name of the field to clear
            
        Example:
            # Clear insurance verification status
            client.appt_fields.clear(
                apt_num=101,
                field_name="Ins Verified"
            )
        """
        self.set(apt_num, field_name, "")

