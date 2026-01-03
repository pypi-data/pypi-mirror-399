from __future__ import annotations
from typing import Annotated
from pydantic import Field
from pydantic import Field
from . import (
    Event,
    NotificationId,
    ReportAdjustments,
    ReportDiscounts,
    ReportProductsPrices,
    ReportTransactions,
)


class Created(Event):
    notification_id: NotificationId | None = None
    data: (
        ReportAdjustments
        | ReportTransactions
        | ReportProductsPrices
        | ReportDiscounts
        | None
    ) = Field(None, description="New or changed entity.", title="Report Notification")


class Updated(Event):
    notification_id: NotificationId | None = None
    data: (
        ReportAdjustments
        | ReportTransactions
        | ReportProductsPrices
        | ReportDiscounts
        | None
    ) = Field(None, description="New or changed entity.", title="Report Notification")
