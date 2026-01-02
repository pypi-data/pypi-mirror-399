from models.remittance import CreateRemittanceRequest, CreateRemittanceResponse, Remittance
from resources.base import ResourceBase


class Remittances(ResourceBase):
    """Remittances resource"""
    
    def create(self, data: CreateRemittanceRequest) -> CreateRemittanceResponse:
        """
        Create a remittance
        
        Args:
            data: Remittance data
            
        Returns:
            Remittance details
        """
        response = self._client.request('POST', '/remittance', data)
        return CreateRemittanceResponse(**response)

    def retrieve(self, remittance_id: str) -> Remittance:
        """
        Get a remittance by ID
        
        Args:
            remittance_id: Remittance ID
            
        Returns:
            Remittance details
        """
        response = self._client.request('GET', f'/remittance/{remittance_id}')
        return Remittance(**response)