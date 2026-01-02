from models.disbursement import CreateDisbursementRequest, Disbursement
from resources.base import ResourceBase


class Disbursements(ResourceBase):
    """Disbursements resource"""
    
    def create(self, data: CreateDisbursementRequest) -> Disbursement:
        """
        Create a disbursement
        
        Args:
            data: Disbursement data
            
        Returns:
            Disbursement details
        """
        
        response =  self._client.request('POST', '/disbursements', data)
        return Disbursement(**response)
    
    def retrieve(self, disbursement_id: str) -> Disbursement:
        """
        Get a disbursement by ID
        
        Args:
            disbursement_id: Disbursement ID
            
        Returns:
            Disbursement details
        """
        response = self._client.request('GET', f'/disbursements/{disbursement_id}')
        return Disbursement(**response)