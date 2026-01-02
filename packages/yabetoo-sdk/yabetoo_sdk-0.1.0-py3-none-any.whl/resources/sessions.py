from .base  import ResourceBase
from models.checkout import CreateCheckoutSession, CheckoutSession

class Sessions(ResourceBase):
    """Sessions resource for checkout sessions"""
    
    def create(self, data: CreateCheckoutSession) -> CheckoutSession:
        """
        Create a checkout session
        
        Args:
            data: Checkout session data
            
        Returns:
            Checkout session details
        """
        response = self._client.request('POST', '/sessions', data)
        return CheckoutSession(**response)