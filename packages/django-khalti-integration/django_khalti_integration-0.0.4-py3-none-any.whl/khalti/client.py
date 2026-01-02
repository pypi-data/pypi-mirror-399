import requests

from khalti.config import KHALTI_ENDPOINTS
from khalti.responses import KhaltiInitiatePaymentResponse, KhaltiVerifyPaymentResponse
from khalti.schemas import KhaltiInitiatePaymentPayload, KhaltiVerifyPaymentPayload
from khalti.settings import KHALTI_BASE_URL, LIVE_SECRET_KEY


class KhaltiClient:
    def __init__(self):
        if not LIVE_SECRET_KEY:
            raise ValueError("KHALTI_LIVE_SECRET_KEY is not set in settings.")
        self.base_url = KHALTI_BASE_URL
        self.secret_key = LIVE_SECRET_KEY

    @property
    def headers(self):
        return {
            "Authorization": f"Key {self.secret_key}",
        }

    def initiate_payment(self, payload):
        payload = KhaltiInitiatePaymentPayload.model_validate(payload)

        api_response = requests.post(
            url=f"{self.base_url}{KHALTI_ENDPOINTS['initiate_payment']}",
            json=payload.model_dump(),
            headers=self.headers,
        )

        api_response.raise_for_status()

        response = KhaltiInitiatePaymentResponse.model_validate(api_response.json())

        return response

    def verify_payment(self, payment_id: str):
        payload = KhaltiVerifyPaymentPayload.model_validate({"pidx": payment_id})

        api_response = requests.post(
            url=f"{self.base_url}{KHALTI_ENDPOINTS['verify_payment']}",
            json=payload.model_dump(),
            headers=self.headers,
        )

        api_response.raise_for_status()

        response = KhaltiVerifyPaymentResponse.model_validate(api_response.json())

        return response
