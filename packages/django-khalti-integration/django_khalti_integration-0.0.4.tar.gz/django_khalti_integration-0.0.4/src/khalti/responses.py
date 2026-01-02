from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class KhaltiPaymentStatus(str, Enum):
    COMPLETED = "Completed"
    PENDING = "Pending"
    INITIATED = "Initiated"
    REFUNDED = "Refunded"
    EXPIRED = "Expired"
    USER_CANCELED = "User canceled"


class KhaltiInitiatePaymentResponse(BaseModel):
    pidx: str
    payment_url: HttpUrl
    expires_at: datetime
    expires_in: int


class KhaltiVerifyPaymentResponse(BaseModel):
    pidx: str
    total_amount: int
    status: KhaltiPaymentStatus
    transaction_id: Optional[str] = None
    fee: int
    refunded: bool
