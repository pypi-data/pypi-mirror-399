from enum import Enum

from datetime import datetime

from pydantic import BaseModel

from paddle._schemas import CustomizationType, ArchiveStatus, ImportMeta
from paddle._schemas.ids import ProductID


class Product(BaseModel):
    id: ProductID

    name: str

    description: str | None

    type: "CustomizationType"

    tax_category: "TaxCategory"

    image_url: str | None

    custom_data: dict | None

    status: "ArchiveStatus"

    import_meta: "ImportMeta" | None

    created_at: datetime
    updated_at: datetime


class TaxCategory(str, Enum):
    DIGITAL_GOODS = "digital-goods"
    EBOOKS = "ebooks"
    IMPLEMENTATION_SERVICES = "implementation-services"
    PROFESSIONAL_SERVICES = "professional-services"
    SAAS = "saas"
    SOFTWARE_PROGRAMMING_SERVICES = "software-programming-services"
    STANDARD = "standard"
    TRAINING_SERVICES = "training-services"
    WEBSITE_HOSTING = "website-hosting"
