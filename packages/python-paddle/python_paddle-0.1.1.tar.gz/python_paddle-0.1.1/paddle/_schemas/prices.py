from enum import Enum

from datetime import datetime

from pydantic import BaseModel, Field

from paddle._schemas import (
    ArchiveStatus,
    ImportMeta,
    BillingCycle,
    CustomizationType,
    CurrencyCode,
    CountryCode,
)
from paddle._schemas.ids import PriceID, ProductID


class Price(BaseModel):
    id: PriceID

    product_id: ProductID

    description: str

    type: "CustomizationType"

    name: str | None

    billing_cycle: "BillingCycle"

    trial_period: "TrialPeriod" | None

    tax_mode: "TaxMode"

    unit_price: "UnitPrice"
    unit_price_overrides: list["UnitPriceOverride"]

    quantity: "Quantity"

    status: "ArchiveStatus"

    custom_data: dict | None

    import_meta: "ImportMeta" | None

    created_at: datetime
    updated_at: datetime


class TrialPeriod(BillingCycle):
    requires_payment_method: bool


class TaxMode(str, Enum):
    ACCOUNT_SETTING = "account_setting"
    EXTERNAL = "external"
    INTERNAL = "internal"
    LOCATION = "location"


class UnitPrice(BaseModel):
    amount: int
    currency_code: "CurrencyCode"


class UnitPriceOverride(BaseModel):
    country_codes: list["CountryCode"]
    unit_price: "UnitPrice"


class Quantity(BaseModel):
    minimum: int
    maximum: int
