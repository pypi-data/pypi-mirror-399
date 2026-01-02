from pydantic import BaseModel, Field
from typing import Union , Optional, Dict, Any
from datetime import datetime 
from .payment import PaymentMethodData

class CreateRemittanceRequest(BaseModel):
    amount: Union[int, str]
    currency: str
    first_name: str
    last_name: str
    payment_method_data: PaymentMethodData
    metadata: Optional[Dict[str, Any]] = None

class CreateRemittanceResponse(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    


class Remittance(BaseModel):
    id: str
    object: str
    wallet_id: str = Field(alias="walletId")
    financial_transaction_id: str = Field(alias="financialTransactionId")
    transaction_id: str = Field(alias="transactionId")
    amount: int
    currency: str
    status: str
    failure_code: Optional[str] = Field(alias="failureCode")
    failure_message: Optional[str] = Field(alias="failureMessage")
    external_id: str = Field(alias="externalId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    executed_at: datetime = Field(alias="executedAt")
    should_executed_at: datetime = Field(alias="shouldExecutedAt")
    otp: Optional[str]
    phone: str
    country: str
    operator_name: str = Field(alias="operatorName")
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    type: int

    class Config:
        validate_by_name= True
        use_enum_values = True
