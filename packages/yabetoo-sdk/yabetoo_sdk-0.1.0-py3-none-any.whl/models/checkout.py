from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Dict, List, Optional, Any


class CheckoutItem(BaseModel):
    product_id: str = Field(alias="productId")
    quantity: int
    price: int
    product_name: str = Field(alias="productName")

    class Config:
       validate_by_name = True



class CreateCheckoutSession(BaseModel):
    account_id: str = Field(alias="accountId")  
    total: float
    currency: str
    success_url: str = Field(alias="successUrl")
    cancel_url: str = Field(alias="cancelUrl")
    metadata: Optional[Dict[str, Any]] = None
    items: Optional[List[CheckoutItem]] = None

    class Config:
        validate_by_name = True
        
class CheckoutSession(BaseModel):
    account_id: str = Field(alias="accountId")
    success_url: HttpUrl = Field(alias="successUrl")
    cancel_url: HttpUrl = Field(alias="cancelUrl")
    url: HttpUrl = Field(alias="url")
    order_id: str = Field(alias="orderId")
    expires_at: datetime = Field(alias="expiresAt")
    session_id: str = Field(alias="id")
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
       validate_by_name = True
