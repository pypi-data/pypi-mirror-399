from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


from mercuryclient.types.common import NormalizedString
from mercuryclient.types.payments.enums import (
    PlanType,
    SubscriptionActionType,
    EmandateMethod,
    AuthType,
    Currency,
    TokenRequestType,
)


class CustomerDetails(BaseModel):

    """
    Customer Details
    """

    name: NormalizedString = Field(max_length=100)
    email: NormalizedString = Field(max_length=100)
    contact: NormalizedString = Field(max_length=15)


class NotesField(BaseModel):
    """
    Notes Field Details
    """

    purpose: Optional[NormalizedString] = Field(max_length=250)
    note_key_1: Optional[NormalizedString] = Field(max_length=250)
    note_key_2: Optional[NormalizedString] = Field(max_length=250)


class BankDetails(BaseModel):
    """
    Bank Details
    """

    account_holder_name: Optional[NormalizedString] = Field()
    account_number: Optional[NormalizedString] = Field()
    account_type: Optional[NormalizedString] = Field()
    account_bank_code: Optional[NormalizedString] = Field()
    beneficiary_name: Optional[NormalizedString] = Field()
    ifsc_code: Optional[NormalizedString] = Field()


class ItemField(BaseModel):
    """
    Item Field Details
    """

    name: NormalizedString = Field(max_length=80)
    amount: float = Field()
    currency: NormalizedString = Field(max_length=8)
    description: NormalizedString = Field(max_length=250)


class QRCodeDetails(BaseModel):
    """
    QR Code details
    """

    type: NormalizedString = Field(max_length=20)
    name: NormalizedString = Field(max_length=80)
    usage: NormalizedString = Field(max_length=25)
    fixed_amount: bool = Field()
    payment_amount: float = Field()
    description: NormalizedString = Field(max_length=250)
    notes: Optional[NotesField]


class QRCodeClosure(BaseModel):
    """
    QR Code Closure details
    """

    qr_id: NormalizedString = Field(max_length=100)


class PlanDetails(BaseModel):
    plan_name: Optional[NormalizedString] = Field(max_length=20)
    plan_type: Optional[PlanType]
    plan_currency: Optional[NormalizedString] = Field(max_length=20, default="INR")
    max_amount: Optional[float]
    plan_note: Optional[NormalizedString] = Field(max_length=20)
    plan_recurring_amount: Optional[float] = Field()


class CreatePlan(PlanDetails):
    """
    Payment Plan Details
    """

    period: NormalizedString = Field(max_length=20)
    interval: int = Field()
    item: Optional[ItemField]

    plan_id: Optional[NormalizedString] = Field(max_length=20)


class SubscriptionCreation(BaseModel):

    """
    Subscription Creation Details
    """

    plan_id: Optional[NormalizedString] = Field(max_length=100)
    subscription_id: Optional[NormalizedString] = Field(max_length=100)

    total_count: Optional[int] = Field()
    quantity: Optional[int] = Field()
    customer_notify: Optional[bool] = Field(default=False)
    customer_details: Optional[CustomerDetails]
    expiry_time: Optional[datetime] = Field()
    first_charge_time: Optional[datetime] = Field()
    note: Optional[NormalizedString] = Field(max_length=100)
    bank_details: Optional[BankDetails]
    plan_details: Optional[PlanDetails]


class SubscriptionFetch(BaseModel):

    """
    Serializer for subscription fetch
    """

    subscription_id: NormalizedString = Field(max_length=100)


class Notify(BaseModel):

    """
    Notify Details
    """

    sms: bool = Field()
    email: bool = Field()


class PaymentGateway(BaseModel):
    """
    Payment Gateway Link Details
    """

    amount: float = Field()
    currency: NormalizedString = Field(max_length=10)
    accept_partial: bool = Field()
    description: NormalizedString = Field(max_length=250)
    notes: Optional[NotesField]
    customer: CustomerDetails
    notify: Optional[Notify]
    reminder_enable: bool = Field()


class PaymentLinkClosure(BaseModel):
    """
    Payment Link Closure Details
    """

    link_id: NormalizedString = Field(max_length=100)


class SubscriptionCharge(BaseModel):

    """
    Serializer for subscription Charge
    """

    subscription_id: NormalizedString = Field(max_length=100)
    payment_id: NormalizedString = Field(max_length=100)
    payment_amount: float
    payment_schedule_date: datetime


class SubscriptionManage(BaseModel):

    """
    Serializer for subscription manage
    """

    subscription_id: NormalizedString = Field(max_length=40)
    action: SubscriptionActionType
    next_scheduled_time: Optional[NormalizedString]
    plan_id: Optional[NormalizedString]
    cancel_at_cycle_end: Optional[int] = Field()
    pause_at: Optional[NormalizedString] = Field(max_length=250)
    resume_at: Optional[NormalizedString] = Field(max_length=250)


class EmandateSubscription(BaseModel):
    method: EmandateMethod
    auth_type: AuthType
    max_amount: int = Field()
    expire_at: Optional[int] = Field()
    bank_account: BankDetails


class EmandateRegistration(BaseModel):
    customer: CustomerDetails
    type: NormalizedString = Field()
    amount: int = Field()
    currency: Currency
    description: NormalizedString = Field()
    subscription_registration: EmandateSubscription
    sms_notify: Optional[bool] = Field()
    email_notify: Optional[bool] = Field()
    expire_by: Optional[int] = Field()
    receipt: Optional[NormalizedString] = Field()
    notes: Optional[NotesField]


class EmandatePaymentToken(BaseModel):
    payment_cust_id: NormalizedString = Field()
    request_type: TokenRequestType


class EmandateOrder(BaseModel):
    amount: int = Field()
    currency: Currency
    payment_capture: bool = Field()
    receipt: Optional[NormalizedString] = Field()
    notes: Optional[NotesField]


class EmandateRecurringPayment(BaseModel):
    email: NormalizedString = Field()
    contact: int = Field()
    currency: Currency
    amount: int = Field()
    order_id: NormalizedString = Field()
    customer_id: NormalizedString = Field()
    token: NormalizedString = Field()
    recurring: bool = Field()
    description: Optional[NormalizedString] = Field()
    notes: Optional[NotesField]
