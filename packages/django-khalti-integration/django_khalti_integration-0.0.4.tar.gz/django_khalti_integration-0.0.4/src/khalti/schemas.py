from typing import List, Optional

from pydantic import BaseModel, HttpUrl, field_validator, model_validator

MIN_AMOUNT_PAISA = 10 * 100


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class AmountBreakdown(BaseModel):
    label: Optional[str] = None
    amount: Optional[int] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Breakdown amount must be greater than 0")
        return v


class ProductDetails(BaseModel):
    identity: Optional[str] = None
    name: Optional[str] = None
    total_price: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[int] = None


class KhaltiInitiatePaymentPayload(BaseModel):
    # Required Fields
    return_url: HttpUrl
    website_url: HttpUrl
    amount: int
    purchase_order_id: str
    purchase_order_name: str

    # Optional Fields
    customer_info: Optional[CustomerInfo] = None
    amount_breakdown: Optional[List[AmountBreakdown]] = None
    product_details: Optional[List[ProductDetails]] = None
    merchant_username: Optional[str] = None
    merchant_extra: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_minimum_10_rupees(cls, v: int) -> int:
        if v < MIN_AMOUNT_PAISA:
            raise ValueError(
                f"Amount must be at least NPR {MIN_AMOUNT_PAISA // 100} ({MIN_AMOUNT_PAISA} paisa)"
            )
        return v

    @model_validator(mode="after")
    def validate_amount_breakdown_total(self):
        if self.amount_breakdown:
            breakdown_total = sum(item.amount for item in self.amount_breakdown)  # type: ignore
            if breakdown_total != self.amount:
                raise ValueError(
                    f"Amount breakdown total ({breakdown_total}) "
                    f"does not match amount ({self.amount})"
                )
        return self


class KhaltiVerifyPaymentPayload(BaseModel):
    pidx: str
