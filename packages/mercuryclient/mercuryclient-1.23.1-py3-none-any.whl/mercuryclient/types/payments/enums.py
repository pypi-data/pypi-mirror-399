from enum import Enum


class Endpoints:
    api_endpoints = {
        "generate_qr_code": "generate/qr/code",
        "plan_creation": "plan/create",
        "subscription_creation": "subscription/create",
        "subscription_fetch": "subscription/fetch",
        "payment_link_creation": "payment/link/create",
        "cancel_payment_link": "payment/link/cancel",
        "close_qr_code": "qr/code/closure",
        "charge_subscription": "subscription/charge",
        "manage_subscription": "subscription/manage",
        "emandate_registration": "emandate/registration/create",
        "emandate_payment_token": "emandate/payment/token",
        "emandate_order_creation": "emandate/order/creation",
        "emandate_recurring_payments": "emandate/recurring/payments",
    }


class PlanType(Enum):
    PERIODIC = "PERIODIC"
    ON_DEMAND = "ON_DEMAND"


class SubscriptionActionType(Enum):
    CANCEL = "CANCEL"
    PAUSE = "PAUSE"
    ACTIVATE = "ACTIVATE"
    CHNAGE_PLAN = "CHANGE_PLAN"
    RESUME = "RESUME"


class EmandateMethod(Enum):
    EMANDATE = "emandate"


class AuthType(Enum):
    NETBANKING = "netbanking"
    AADHAAR = "aadhaar"
    DEBITCARD = "debitcard"


class Currency(Enum):
    INR = "INR"


class TokenRequestType(Enum):
    PAYMENTID = "PAYMENT_ID"
    CUSTOMERID = "CUSTOMER_ID"
