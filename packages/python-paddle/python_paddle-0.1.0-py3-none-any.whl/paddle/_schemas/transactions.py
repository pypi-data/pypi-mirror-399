from enum import Enum

from datetime import datetime

from pydantic import BaseModel

from paddle._schemas import CurrencyCode, CollectionMode, BillingDetails, BillingPeriod
from paddle._schemas.ids import (
    AddressID,
    BusinessID,
    CustomerID,
    DiscountID,
    PriceID,
    SubscriptionID,
    TransactionID,
)
from paddle._schemas.prices import Price


class Transaction(BaseModel):
    id: TransactionID

    status: "TransactionStatus"

    customer_id: CustomerID | None
    address_id: AddressID | None
    business_id: BusinessID | None
    subscription_id: SubscriptionID | None
    discount_id: DiscountID | None

    custom_data: dict | None

    currency_code: CurrencyCode

    origin: "TransactionOrigin"

    # invoice_id is deprecated, we don't add it here for that reason
    invoice_number: str | None

    collection_mode: CollectionMode

    billing_details: BillingDetails | None
    billing_period: BillingPeriod | None

    items: list["Item"]


class TransactionStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    BILLED = "billed"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELED = "canceled"
    PAST_DUE = "past_due"


class TransactionOrigin(str, Enum):
    API = "api"
    SUBSCRIPTION_CHARGE = "subscription_charge"
    SUBSCRIPTION_PAYMENT_METHOD_CHANGE = "subscription_payment_method_change"
    SUBSCRIPTION_RECURRING = "subscription_recurring"
    SUBSCRIPTION_UPDATE = "subscription_update"
    WEB = "web"


class Item(BaseModel):
    price_id: PriceID
    price: Price

    quantity: int

    proration: "Proration"


class Proration(BaseModel):
    rate: str
    billing_period: BillingPeriod


class Details(BaseModel):
    tax_rates_used: list["TaxRate"]

    totals: "Totals"
    adjusted_totals: "AdjustedTotals"
    payout_totals: "PayoutTotals" | None
    adjusted_payout_totals: "AdjustedPayoutTotals" | None
    
    line_items: list["LineItem"]


class TaxRate(BaseModel):
    tax_rate: str

    totals: "TaxRateTotals"


class TaxRateTotals(BaseModel):
    subtotal: str
    discount: str
    tax: str
    total: str


class Totals(BaseModel):
    subtotal: str
    discount: str
    tax: str
    total: str
    credit: str
    credit_to_balance: str
    balance: str
    grand_total: str
    fee: str | None
    earnings: str | None
    currency_code: CurrencyCode


class AdjustedTotals(BaseModel):
    subtotal: str
    tax: str
    total: str
    grand_total: str
    fee: str | None
    retained_fee: str
    earnings: str | None
    currency_code: CurrencyCode


class PayoutTotals(BaseModel):
    subtotal: str
    discount: str
    tax: str
    total: str
    credit: str
    credit_to_balance: str
    balance: str
    grand_total: str
    fee: str
    earnings: str
    currency_code: CurrencyCode
    exchange_rate: str
    fee_rate: str


class AdjustedPayoutTotals(BaseModel):
    subtotal: str
    tax: str
    total: str
    fee: str
    retained_fee: str
    chargeback_fee: "ChargebackFee"
    earnings: str
    currency_code: CurrencyCode
    exchange_rate: str


class ChargebackFee(BaseModel):
    amount: str
    original: "ChargebackFeeOriginal"


class ChargebackFeeOriginal(BaseModel):
    amount: str
    currency_code: CurrencyCode


class LineItem(BaseModel):
    