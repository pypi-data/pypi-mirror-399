"""Appt Field Defs client for Open Dental SDK."""

from typing import List, Union, Dict, Any
from ...base.resource import BaseResource
from .models import ApptFieldDef, CreateApptFieldDefRequest


class ApptFieldDefsClient(BaseResource):
    """
    Client for managing appointment field definitions in Open Dental.
    
    Appointment Field Defs allow you to organize notes specific to a patient's 
    appointment and are displayed in the bottom left of the Edit Appointment window.
    
    These are the definitions/schema for appointment fields. To set actual values
    for specific appointments, use the appt_fields resource.
    
    See: https://www.opendental.com/site/apiapptfielddefs.html
    Version Added: 21.4
    """
    
    def __init__(self, client):
        """Initialize the appt field defs client."""
        super().__init__(client, "apptfielddefs")
    
    def list(self) -> List[ApptFieldDef]:
        """
        Get a list of all appointment field definitions.
        
        Version Added: 21.4
        
        Returns:
            List[ApptFieldDef]: List of all appointment field definitions
            
        Example:
            # Get all appointment field definitions
            field_defs = client.appt_field_defs.list()
            for field_def in field_defs:
                print(f"{field_def.field_name}: {field_def.field_type}")
                if field_def.field_type == "PickList":
                    print(f"  Options: {field_def.pick_list}")
        """
        endpoint = self._build_endpoint()
        response = self._get(endpoint)
        return self._handle_list_response(response, ApptFieldDef)
    
    def create(
        self,
        field_def_data: Union[CreateApptFieldDefRequest, Dict[str, Any]]
    ) -> ApptFieldDef:
        """
        Create a new appointment field definition.
        
        The API supports creating both Text type and PickList type ApptFieldDefs.
        Duplicate ApptFieldDefs are not allowed.
        
        Version Added: 21.4
        
        Args:
            field_def_data: Appointment field definition data
                - FieldName: Required. Name of the field
                - FieldType: Optional. Either "Text" or "PickList". Default is "Text"
                - PickList: Optional. Only used if FieldType is "PickList". 
                           Items separated by \\r\\n
                           
        Returns:
            ApptFieldDef: The created appointment field definition
            
        Example:
            # Create a text field
            text_field = client.appt_field_defs.create({
                "FieldName": "Temperature"
            })
            
            # Create a pick list field
            picklist_field = client.appt_field_defs.create({
                "FieldName": "Patient a minor?",
                "FieldType": "PickList",
                "PickList": "Yes\\r\\nNo\\r\\nUnknown"
            })
        """
        endpoint = self._build_endpoint()
        
        if isinstance(field_def_data, dict):
            data = field_def_data
        else:
            data = field_def_data.model_dump(exclude_none=True, by_alias=True)
        
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, ApptFieldDef)
    
    def create_text_field(self, field_name: str) -> ApptFieldDef:
        """
        Create a text-type appointment field definition.
        
        This is a convenience method for creating a simple text field.
        Users will be able to enter any free-form text in the Edit Appointment window.
        
        Args:
            field_name: Name of the field
            
        Returns:
            ApptFieldDef: The created appointment field definition
            
        Example:
            field_def = client.appt_field_defs.create_text_field("Temperature")
        """
        return self.create({
            "FieldName": field_name,
            "FieldType": "Text"
        })
    
    def create_picklist_field(
        self,
        field_name: str,
        options: List[str]
    ) -> ApptFieldDef:
        """
        Create a pick-list type appointment field definition.
        
        This is a convenience method for creating a pick list field.
        Users will select from the provided list of items in the Edit Appointment window.
        
        Args:
            field_name: Name of the field
            options: List of options to display in the pick list
            
        Returns:
            ApptFieldDef: The created appointment field definition
            
        Example:
            field_def = client.appt_field_defs.create_picklist_field(
                field_name="Patient a minor?",
                options=["Yes", "No", "Unknown"]
            )
        """
        pick_list = "\\r\\n".join(options)
        return self.create({
            "FieldName": field_name,
            "FieldType": "PickList",
            "PickList": pick_list
        })

