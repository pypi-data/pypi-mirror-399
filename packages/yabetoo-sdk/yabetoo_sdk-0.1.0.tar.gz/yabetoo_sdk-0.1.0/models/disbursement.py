from pydantic import BaseModel, Field
from .payment import PaymentMethodData
from pydantic import BaseModel, Field
from datetime import datetime
class CreateDisbursementRequest(BaseModel):
    amount: float
    currency: str
    first_name: str
    last_name: str
    payment_method_data: PaymentMethodData
    



class Disbursement(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    operator_name: str = Field(alias="operatorName")
    country: str
    phone: str
    object: str
    type: int
    should_executed_at: datetime = Field(alias="shouldExecutedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        validate_by_name = True
        use_enum_values = True
