"""InsVerifies client for Open Dental SDK."""

from typing import Optional, Union, List
from datetime import datetime
from ...base.resource import BaseResource
from .models import (
    InsVerify,
    UpdateInsVerifyRequest,
    InsVerifyListResponse
)
from .types import VerifyType


class InsVerifiesClient(BaseResource):
    """
    Client for managing insurance verifications in Open Dental.
    
    InsVerifies track insurance verification status for both patient eligibility
    and insurance plan benefits. Historical entries are retained in insverifyhist.
    
    Version Added: 21.1 (PUT), 23.2.23 (GET)
    Reference: https://www.opendental.com/site/apiinsverifies.html
    """
    
    def __init__(self, client):
        """Initialize the insurance verifications client."""
        super().__init__(client, "insverifies")
    
    def get(self, ins_verify_num: Union[int, str]) -> InsVerify:
        """
        Get a single insurance verification by ID.
        
        Version Added: 23.2.23
        
        Args:
            ins_verify_num: The insurance verification number (primary key)
            
        Returns:
            InsVerify: The insurance verification object
            
        Example:
            ins_verify = client.ins_verifies.get(12)
        """
        ins_verify_num = self._validate_id(ins_verify_num)
        endpoint = self._build_endpoint(ins_verify_num)
        response = self._get(endpoint)
        return self._handle_response(response, InsVerify)
    
    def list(
        self,
        verify_type: Optional[Union[str, VerifyType]] = None,
        f_key: Optional[int] = None,
        sec_date_t_edit: Optional[Union[str, datetime]] = None
    ) -> InsVerifyListResponse:
        """
        List insurance verifications with optional filtering.
        
        Version Added: 23.2.23
        
        Args:
            verify_type: Optional. Filter by verification type (required if f_key is specified)
            f_key: Optional. FK to patplan.PatPlanNum or insplan.PlanNum (requires verify_type)
            sec_date_t_edit: Optional. Only include records modified after this date/time
                            Can be a datetime object or string in "yyyy-MM-dd HH:mm:ss" format
            
        Returns:
            InsVerifyListResponse: List of insurance verifications
            
        Examples:
            # Get all verifications
            result = client.ins_verifies.list()
            
            # Get verifications for a specific patient plan
            result = client.ins_verifies.list(
                verify_type="PatientEnrollment",
                f_key=10
            )
            
            # Get verifications modified after a specific date
            result = client.ins_verifies.list(
                sec_date_t_edit="2024-03-25 05:30:00"
            )
        """
        params = {}
        
        if verify_type is not None:
            # Convert enum to string if needed
            if isinstance(verify_type, VerifyType):
                params["VerifyType"] = verify_type.value
            else:
                params["VerifyType"] = verify_type
        
        if f_key is not None:
            if verify_type is None:
                raise ValueError("verify_type is required when f_key is specified")
            params["FKey"] = f_key
        
        if sec_date_t_edit is not None:
            # Convert datetime to string if needed
            if isinstance(sec_date_t_edit, datetime):
                params["SecDateTEdit"] = sec_date_t_edit.strftime("%Y-%m-%d %H:%M:%S")
            else:
                params["SecDateTEdit"] = sec_date_t_edit
        
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        # API returns a list directly
        if isinstance(response, list):
            ins_verifies = [InsVerify(**item) for item in response]
            return InsVerifyListResponse(
                ins_verifies=ins_verifies,
                total=len(ins_verifies)
            )
        
        return InsVerifyListResponse(ins_verifies=[], total=0)
    
    def update(self, ins_verify_data: UpdateInsVerifyRequest) -> InsVerify:
        """
        Update or create an insurance verification.
        
        This method sets the 'Eligibility Last Verified' or 'Benefits Last Verified'
        fields as seen on the Insurance Plan window. Historical entries are retained
        in the insverifyhist table.
        
        Version Added: 21.1
        
        Args:
            ins_verify_data: The insurance verification data
            
        Returns:
            InsVerify: The created/updated insurance verification
            
        Raises:
            ValueError: If required fields are missing or invalid
            
        Examples:
            # Verify patient enrollment
            from opendental.resources.ins_verifies.types import VerifyType
            
            verify = UpdateInsVerifyRequest(
                date_last_verified="2024-03-27",
                verify_type=VerifyType.PATIENT_ENROLLMENT,
                f_key=325,  # PatPlanNum
                def_num=721,
                note="Need additional pat info"
            )
            result = client.ins_verifies.update(verify)
            
            # Verify insurance benefits
            verify = UpdateInsVerifyRequest(
                date_last_verified="2024-03-27",
                verify_type=VerifyType.INSURANCE_BENEFIT,
                f_key=45,  # PlanNum
                note="Benefits confirmed"
            )
            result = client.ins_verifies.update(verify)
        """
        endpoint = self._build_endpoint()
        data = ins_verify_data.model_dump(by_alias=True, exclude_none=True)
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, InsVerify)
    
    def verify_patient_enrollment(
        self,
        pat_plan_num: int,
        date_last_verified: Optional[str] = None,
        def_num: Optional[int] = None,
        note: Optional[str] = None
    ) -> InsVerify:
        """
        Convenience method to verify a patient's insurance eligibility.
        
        Args:
            pat_plan_num: Patient plan number (patplan.PatPlanNum)
            date_last_verified: Date in yyyy-MM-dd format (optional)
            def_num: Definition number for verification status (optional)
            note: Status note (optional)
            
        Returns:
            InsVerify: The created/updated insurance verification
            
        Example:
            result = client.ins_verifies.verify_patient_enrollment(
                pat_plan_num=325,
                date_last_verified="2024-03-27",
                note="Eligibility confirmed"
            )
        """
        request = UpdateInsVerifyRequest(
            verify_type=VerifyType.PATIENT_ENROLLMENT.value,
            f_key=pat_plan_num,
            date_last_verified=date_last_verified,
            def_num=def_num,
            note=note
        )
        return self.update(request)
    
    def verify_insurance_benefit(
        self,
        plan_num: int,
        date_last_verified: Optional[str] = None,
        def_num: Optional[int] = None,
        note: Optional[str] = None
    ) -> InsVerify:
        """
        Convenience method to verify an insurance plan's benefits.
        
        Args:
            plan_num: Insurance plan number (insplan.PlanNum)
            date_last_verified: Date in yyyy-MM-dd format (optional)
            def_num: Definition number for verification status (optional)
            note: Status note (optional)
            
        Returns:
            InsVerify: The created/updated insurance verification
            
        Example:
            result = client.ins_verifies.verify_insurance_benefit(
                plan_num=45,
                date_last_verified="2024-03-27",
                note="Benefits verified"
            )
        """
        request = UpdateInsVerifyRequest(
            verify_type=VerifyType.INSURANCE_BENEFIT.value,
            f_key=plan_num,
            date_last_verified=date_last_verified,
            def_num=def_num,
            note=note
        )
        return self.update(request)
    
    def get_by_patient_plan(self, pat_plan_num: int) -> List[InsVerify]:
        """
        Get all insurance verifications for a specific patient plan.
        
        Args:
            pat_plan_num: Patient plan number
            
        Returns:
            List[InsVerify]: List of verifications for the patient plan
            
        Example:
            verifications = client.ins_verifies.get_by_patient_plan(325)
        """
        result = self.list(verify_type=VerifyType.PATIENT_ENROLLMENT, f_key=pat_plan_num)
        return result.ins_verifies
    
    def get_by_insurance_plan(self, plan_num: int) -> List[InsVerify]:
        """
        Get all insurance verifications for a specific insurance plan.
        
        Args:
            plan_num: Insurance plan number
            
        Returns:
            List[InsVerify]: List of verifications for the insurance plan
            
        Example:
            verifications = client.ins_verifies.get_by_insurance_plan(45)
        """
        result = self.list(verify_type=VerifyType.INSURANCE_BENEFIT, f_key=plan_num)
        return result.ins_verifies

