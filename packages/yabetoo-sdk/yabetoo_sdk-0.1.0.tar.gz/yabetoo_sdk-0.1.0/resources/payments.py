from typing import Any, Dict, List, Optional
from models.paginated_response import PaginatedResponse
from models.payment import ConfirmIntentRequest, ConfirmIntentResponse, CreateIntentRequest, CreateIntentResponse, PaymentFiltersRequest, PaymentIntent
from resources.base import ResourceBase


class Payments(ResourceBase):
    """Payments resource for interacting with payment intents"""

    def create(self, data: CreateIntentRequest) -> CreateIntentResponse:
        """
        Create a payment intent

        Args:
            data: Payment intent data

        Returns:
            Payment intent details
        """
        response = self._client.request('POST', '/payment-intents', data)
        return CreateIntentResponse(**response)

    def confirm(self, payment_id: str, data: ConfirmIntentRequest) -> ConfirmIntentResponse:
        """
        Confirm a payment intent

        Args:
            payment_id: Payment intent ID
            data: Confirmation data

        Returns:
            Confirmed payment intent details
        """
        response = self._client.request(
            'POST', f'/payment-intents/{payment_id}/confirm', data)
       

        return ConfirmIntentResponse(**response)

    def retrieve(self, payment_id: str) -> PaymentIntent:
        """
        Get a payment intent by ID

        Args:
            payment_id: Payment intent ID

        Returns:
            Payment intent details
        """
        response = self._client.request(
            'GET', f'/payment-intents/{payment_id}')
        return PaymentIntent(**response)

    
    def all(self, params: Optional[PaymentFiltersRequest] = None) -> PaginatedResponse[PaymentIntent]:
        """
        List all payment intents with pagination support
        
        Args:
            params: Filter and pagination parameters
            
        Returns:
            Paginated response containing payment intents
        """
        query_params = {}
        
        
        
        response = self._client.request('GET', '/payment-intents', params=params.to_query_params())
        return PaginatedResponse({'data': response}, PaymentIntent)
    
    def get_page(self, page: int, per_page: Optional[int] = None, 
                 sorting: Optional[List[Dict[str, Any]]] = None) -> PaginatedResponse[PaymentIntent]:
        """
        Convenient method to get a specific page of payment intents
        
        Args:
            page: Page number to retrieve (starting from 1)
            per_page: Number of items per page
            sorting: Optional sorting criteria
            
        Returns:
            Paginated response containing payment intents
        """
        filters = PaymentFiltersRequest(page=page, per_page=per_page)
        
        if sorting:
            from models.payment import Sorting
            sorting_objects = [Sorting(**sort) for sort in sorting]
            filters.sorting = sorting_objects
            
        return self.all(filters)