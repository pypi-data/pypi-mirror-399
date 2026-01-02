from enum import Enum

from datetime import datetime

from pydantic import BaseModel

from paddle._schemas import (
    ImportMeta,
    CurrencyCode,
    BillingCycle,
    CollectionMode,
    BillingDetails,
    BillingPeriod,
)
from paddle._schemas.ids import (
    SubscriptionID,
    CustomerID,
    AddressID,
    BusinessID,
    DiscountID,
)
from paddle._schemas.prices import Price
from paddle._schemas.products import Product


class Subscription(BaseModel):
    id: SubscriptionID

    status: "SubscriptionStatus"

    customer_id: CustomerID
    address_id: AddressID
    business_id: BusinessID | None

    currency_code: "CurrencyCode"

    created_at: datetime
    updated_at: datetime

    first_billed_at: datetime | None
    next_billed_at: datetime | None

    paused_at: datetime | None
    canceled_at: datetime | None

    discount: "Discount" | None

    collection_mode: "CollectionMode"

    billing_details: "BillingDetails" | None

    current_billing_period: "BillingPeriod" | None

    billing_cycle: "BillingCycle"

    scheduled_change: "ScheduledChange" | None

    management_urls: "ManagementURLs"

    items: list["Item"]

    custom_data: dict | None

    import_meta: "ImportMeta" | None


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    TRIALING = "trialing"


class Discount(BaseModel):
    id: DiscountID

    starts_at: datetime
    ends_at: datetime | None


class ScheduledChange(BaseModel):
    action: "ScheduledChangeAction"

    effective_at: datetime
    resume_at: datetime | None


class ScheduledChangeAction(str, Enum):
    PAUSE = "pause"
    CANCEL = "cancel"
    RESUME = "resume"


class ManagementURLs(BaseModel):
    update_payment_method: str | None
    cancel: str | None


class Item(BaseModel):
    status: "ItemStatus"
    quantity: int
    recurring: bool

    created_at: datetime
    updated_at: datetime

    previously_billed_at: datetime | None
    next_billed_at: datetime | None

    trial_dates: "TrialDates" | None

    price: "Price"

    product: "Product"


class ItemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIALING = "trialing"


class TrialDates(BaseModel):
    starts_at: datetime
    ends_at: datetime
