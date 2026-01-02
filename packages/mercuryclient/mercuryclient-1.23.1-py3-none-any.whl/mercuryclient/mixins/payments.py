import time
from typing import Tuple
import json

from mercuryclient.types.payments.enums import Endpoints
from mercuryclient.types.payments.request import (
    QRCodeDetails,
    CreatePlan,
    SubscriptionCreation,
    SubscriptionFetch,
    PaymentGateway,
    SubscriptionCharge,
    SubscriptionManage,
    PaymentLinkClosure,
    QRCodeClosure,
    EmandateRegistration,
    EmandatePaymentToken,
    EmandateOrder,
    EmandateRecurringPayment,
)


class PaymentsMixin:
    """
    Mixin for initiating payment
    """

    def initiate_payment_request(
        self, profile, provider, request_data, request_type
    ) -> str:
        api = "api/v1/payments/"
        try:
            endpoint = Endpoints.api_endpoints[request_type]
        except ValueError:
            raise Exception(f"{endpoint} is not a valid request_type")
        url = f"{api}{endpoint}"

        request_dict = json.loads(request_data.json(exclude_unset=True))
        request_dict["profile"] = profile
        request_dict["provider"] = provider
        request_id, r = self._post_json_http_request(
            url, data=request_dict, send_request_id=True, add_bearer_token=True
        )
        if r.status_code == 201:
            return request_id

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error while sending payment request. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_payment_response(self, request_id: str) -> Tuple[str, dict]:
        api = "api/v1/payments/result"

        request_id, r = self._get_json_http_request(
            api,
            headers={"X-Mercury-Request-Id": request_id},
            send_request_id=False,
            add_bearer_token=True,
        )

        if r.status_code == 200:
            result = r.json()
            return request_id, result

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error getting Payment Operation result. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_payment_result(
        self, mercury_request_id: str, max_attempts: int = 5, retry_backoff: int = 5
    ):
        """Retry mechanism for okyc response

        raises:
            Exception: After max attempts, response till remains in progress

        returns mercury_request_id,response from the vendor

        """

        for attempts in range(max_attempts):
            time.sleep(retry_backoff)
            mercury_request_id, result = self.get_payment_response(mercury_request_id)
            if result.get("status") != "IN_PROGRESS":
                return mercury_request_id, result

            retry_backoff *= 2

        raise Exception("Error getting Payment Operation result. Status: IN_PROGRESS")

    def generate_qr_code(
        self,
        request_obj: QRCodeDetails,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request for creating qr code.

        returns: mercury_request_id,qr code response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="generate_qr_code",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def qr_code_closure(
        self,
        request_obj: QRCodeClosure,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request for closing a qr code.

        returns: mercury_request_id,qr code response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="close_qr_code",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def generate_payment_plan(
        self,
        request_obj: CreatePlan,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request for payment plan.

        returns: mercury_request_id,plan id inside the response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="plan_creation",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def create_payment_subscription(
        self,
        request_obj: SubscriptionCreation,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request creating a payment subscription.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="subscription_creation",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def fetch_subscription(
        self,
        request_obj: SubscriptionFetch,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request fetching details of an existing subscription.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="subscription_fetch",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def generate_payment_link(
        self,
        request_obj: PaymentGateway,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request for generating a payment gateway link.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="payment_link_creation",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def cancel_payment_link(
        self,
        request_obj: PaymentLinkClosure,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request the closure of a payment gateway link.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="cancel_payment_link",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def charge_subscription(
        self,
        request_obj: SubscriptionCharge,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request fetching details of an existing subscription.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="charge_subscription",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def manage_subscription(
        self,
        request_obj: SubscriptionManage,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request fetching details of an existing subscription.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="manage_subscription",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def emandate_registration(
        self,
        request_obj: EmandateRegistration,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request to create an emandate registration link.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="emandate_registration",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def emandate_payment_token(
        self,
        request_obj: EmandatePaymentToken,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request to create an emandate payment token.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="emandate_payment_token",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def emandate_order(
        self,
        request_obj: EmandateOrder,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request to create an emandate payment token.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="emandate_order_creation",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)

    def emandate_recurring_payments(
        self,
        request_obj: EmandateRecurringPayment,
        profile: str,
        provider: str,
        max_attempts: int = 5,
        retry_backoff: int = 5,
    ):
        """Initiates the request to create an emandate payment token.

        returns: mercury_request_id,otp generation response from vendor
        """

        mercury_request_id = self.initiate_payment_request(
            profile=profile,
            provider=provider,
            request_data=request_obj,
            request_type="emandate_recurring_payments",
        )
        return self.get_payment_result(mercury_request_id, max_attempts, retry_backoff)
