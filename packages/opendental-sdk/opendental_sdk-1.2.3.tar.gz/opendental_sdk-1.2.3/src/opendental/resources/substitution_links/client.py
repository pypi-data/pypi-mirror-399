"""Substitution Links client for Open Dental SDK."""

from typing import List, Optional, Union
from ...base.resource import BaseResource
from .models import (
    SubstitutionLink,
    CreateSubstitutionLinkRequest,
    UpdateSubstitutionLinkRequest,
    SubstitutionLinkListResponse,
    SubstitutionLinkSearchRequest
)


class SubstitutionLinksClient(BaseResource):
    """
    Client for managing insurance procedure code substitutions/downgrades.
    
    Substitution links define when insurance companies substitute one procedure 
    code for another (typically a less expensive alternative). Also known as 
    "downgrades" in dental insurance.
    """
    
    def __init__(self, client):
        """Initialize the substitution links client."""
        super().__init__(client, "substitutionlinks")
    
    def get(self, substitution_link_num: Union[int, str]) -> SubstitutionLink:
        """
        Get a substitution link by ID.
        
        Args:
            substitution_link_num: Substitution link number
            
        Returns:
            SubstitutionLink object
        """
        substitution_link_num = self._validate_id(substitution_link_num)
        endpoint = self._build_endpoint(substitution_link_num)
        response = self._get(endpoint)
        return self._handle_response(response, SubstitutionLink)
    
    def list(self, plan_num: Optional[int] = None, page: int = 1, per_page: int = 50) -> SubstitutionLinkListResponse:
        """
        List substitution links, optionally filtered by insurance plan.
        
        Per API spec: GET /substitutionlinks?PlanNum=33
        
        Args:
            plan_num: Optional insurance plan number to filter by
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            SubstitutionLinkListResponse with list of substitution links
        """
        params = {"page": page, "per_page": per_page}
        if plan_num is not None:
            params["PlanNum"] = plan_num
            
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return SubstitutionLinkListResponse(**response)
        elif isinstance(response, list):
            return SubstitutionLinkListResponse(
                substitution_links=[SubstitutionLink(**item) for item in response],
                total=len(response), page=page, per_page=per_page
            )
        return SubstitutionLinkListResponse(substitution_links=[], total=0, page=page, per_page=per_page)
    
    def create(self, request: CreateSubstitutionLinkRequest) -> SubstitutionLink:
        """
        Create a new substitution link (downgrade rule).
        
        Per API spec: POST /substitutionlinks
        Required fields: PlanNum, CodeNum, SubstitutionCode, SubstOnlyIf
        
        Args:
            request: CreateSubstitutionLinkRequest with all required fields
            
        Returns:
            Created SubstitutionLink object
            
        Example:
            >>> # Create a downgrade rule for an insurance plan
            >>> request = CreateSubstitutionLinkRequest(
            ...     plan_num=34,
            ...     code_num=6,
            ...     substitution_code="D3002",
            ...     subst_only_if="Molar"
            ... )
            >>> link = client.substitution_links.create(request)
        """
        endpoint = self._build_endpoint()
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, SubstitutionLink)
    
    def update(self, substitution_link_num: Union[int, str], request: UpdateSubstitutionLinkRequest) -> SubstitutionLink:
        """
        Update an existing substitution link.
        
        Per API spec: PUT /substitutionlinks/34
        Optional fields: SubstitutionCode, SubstOnlyIf
        
        Args:
            substitution_link_num: Substitution link number
            request: UpdateSubstitutionLinkRequest with fields to update
            
        Returns:
            Updated SubstitutionLink object
        """
        substitution_link_num = self._validate_id(substitution_link_num)
        endpoint = self._build_endpoint(substitution_link_num)
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, SubstitutionLink)
    
    def delete(self, substitution_link_num: Union[int, str]) -> bool:
        """
        Delete a substitution link.
        
        Per API spec: DELETE /substitutionlinks/25
        
        Args:
            substitution_link_num: Substitution link number
            
        Returns:
            True if successful
        """
        substitution_link_num = self._validate_id(substitution_link_num)
        endpoint = self._build_endpoint(substitution_link_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def search(self, search_params: SubstitutionLinkSearchRequest) -> SubstitutionLinkListResponse:
        """
        Search for substitution links by procedure codes or plan.
        
        Args:
            search_params: SubstitutionLinkSearchRequest with search criteria
            
        Returns:
            SubstitutionLinkListResponse with matching substitution links
        """
        endpoint = self._build_endpoint("search")
        params = search_params.model_dump(by_alias=True, exclude_none=True)
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return SubstitutionLinkListResponse(**response)
        elif isinstance(response, list):
            return SubstitutionLinkListResponse(
                substitution_links=[SubstitutionLink(**item) for item in response],
                total=len(response), page=search_params.page, per_page=search_params.per_page
            )
        return SubstitutionLinkListResponse(
            substitution_links=[], total=0, page=search_params.page, per_page=search_params.per_page
        )
    
    def get_by_procedure_code(self, code_num: int) -> List[SubstitutionLink]:
        """
        Get all substitution links for a specific procedure code.
        
        Args:
            code_num: Procedure code number (CodeNum)
            
        Returns:
            List of SubstitutionLink objects
        """
        search_params = SubstitutionLinkSearchRequest(code_num=code_num, per_page=1000)
        result = self.search(search_params)
        return result.substitution_links
    
    def get_by_plan(self, plan_num: int) -> List[SubstitutionLink]:
        """
        Get all substitution links for a specific insurance plan.
        
        Per API spec: GET /substitutionlinks?PlanNum=33
        
        Args:
            plan_num: Insurance plan number (FK to InsPlan.PlanNum)
            
        Returns:
            List of SubstitutionLink objects
        """
        # Use the list method with plan_num filter as per API spec
        result = self.list(plan_num=plan_num, per_page=1000)
        return result.substitution_links

