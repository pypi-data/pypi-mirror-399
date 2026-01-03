from typing import Literal

from datetime import datetime

from httpx import AsyncClient

from pydantic import BaseModel, ValidationError as PydanticValidationError

from paddle.client import BearerAuth
from paddle.schemas import (
    TransactionCreate,
    TransactionIncludes,
    TransactionUpdate,
    TransactionPreview,
    TransactionPreviewCreate,
    TransactionRevise,
    CollectionMode,
    OriginTransaction1,
    StatusTransaction,
    Transaction,
)
from paddle.schemas.response import Response, PaginatedResponse
from paddle.exceptions import ValidationError, ApiError


Includes = Literal[
    "address",
    "adjustments",
    "adjustments_totals",
    "available_payment_methods",
    "business",
    "customer",
    "discount",
]

OrderBy = Literal[
    "id[ASC]",
    "id[DESC]",
    "billed_at[ASC]",
    "billed_at[DESC]",
    "created_at[ASC]",
    "created_at[DESC]",
    "updated_at[ASC]",
    "updated_at[DESC]",
]

Disposition = Literal[
    "inline",
    "attachment",
]


class InvoiceUrl(BaseModel):
    url: str


class TransactionOperationsMixin:
    token: str
    client: AsyncClient

    async def list_transactions(
        self,
        *,
        after: str = ...,
        billed_at: datetime = ...,
        billed_at__lt: datetime = ...,
        billed_at__lte: datetime = ...,
        billed_at__gt: datetime = ...,
        billed_at__gte: datetime = ...,
        collection_mode: CollectionMode = ...,
        created_at: datetime = ...,
        created_at__lt: datetime = ...,
        created_at__lte: datetime = ...,
        created_at__gt: datetime = ...,
        created_at__gte: datetime = ...,
        customer_id: list[str] = ...,
        id: list[str] = ...,
        include: list[Includes] = ...,
        invoice_number: list[str] = ...,
        origins: list[OriginTransaction1] = ...,
        order_by: OrderBy = ...,
        status: list[StatusTransaction] = ...,
        subscription_id: list[str] = ...,
        per_page: int = 30,
        updated_at: datetime = ...,
        updated_at__lt: datetime = ...,
        updated_at__lte: datetime = ...,
        updated_at__gt: datetime = ...,
        updated_at__gte: datetime = ...,
    ) -> PaginatedResponse[TransactionIncludes]:
        """List all transactions."""

        url = "https://api.paddle.com/transactions"

        query = {}

        if after is not ...:
            query["after"] = after

        if billed_at is not ...:
            query["billed_at"] = billed_at.isoformat()
        elif billed_at__lt is not ...:
            query["billed_at[LT]"] = billed_at__lt.isoformat()
        elif billed_at__lte is not ...:
            query["billed_at[LTE]"] = billed_at__lte.isoformat()
        elif billed_at__gt is not ...:
            query["billed_at[GT]"] = billed_at__gt.isoformat()
        elif billed_at__gte is not ...:
            query["billed_at[GTE]"] = billed_at__gte.isoformat()

        if collection_mode is not ...:
            query["collection_mode"] = collection_mode

        if created_at is not ...:
            query["created_at"] = created_at.isoformat()
        elif created_at__lt is not ...:
            query["created_at[LT]"] = created_at__lt.isoformat()
        elif created_at__lte is not ...:
            query["created_at[LTE]"] = created_at__lte.isoformat()
        elif created_at__gt is not ...:
            query["created_at[GT]"] = created_at__gt.isoformat()
        elif created_at__gte is not ...:
            query["created_at[GTE]"] = created_at__gte.isoformat()

        if customer_id is not ...:
            query["customer_id"] = ",".join(customer_id)

        if id is not ...:
            query["id"] = ",".join(id)

        if include is not ...:
            query["include"] = ",".join(include)

        if invoice_number is not ...:
            query["invoice_number"] = ",".join(invoice_number)

        if origins is not ...:
            query["origins"] = ",".join(origins)

        if order_by is not ...:
            query["order_by"] = order_by

        if status is not ...:
            query["status"] = ",".join([s.value for s in status])

        if subscription_id is not ...:
            query["subscription_id"] = ",".join(subscription_id)

        if per_page is not ...:
            query["per_page"] = str(per_page)

        if updated_at is not ...:
            query["updated_at"] = updated_at.isoformat()
        elif updated_at__lt is not ...:
            query["updated_at[LT]"] = updated_at__lt.isoformat()
        elif updated_at__lte is not ...:
            query["updated_at[LTE]"] = updated_at__lte.isoformat()
        elif updated_at__gt is not ...:
            query["updated_at[GT]"] = updated_at__gt.isoformat()
        elif updated_at__gte is not ...:
            query["updated_at[GTE]"] = updated_at__gte.isoformat()

        try:
            response = await self.client.get(
                url,
                params=query,
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return PaginatedResponse[TransactionIncludes].model_validate_json(
                response.text
            )

        except PydanticValidationError as e:
            raise ValidationError from e

    async def create_transaction(
        self,
        transaction: TransactionCreate,
        *,
        include: list[Includes] = ...,
    ) -> Response[TransactionIncludes]:
        """Create a transaction."""

        url = "https://api.paddle.com/transactions"

        query = {}

        if include is not ...:
            query["include"] = ",".join(include)

        json = transaction.model_dump_json()

        try:
            response = await self.client.post(
                url,
                params=query,
                auth=BearerAuth(self.token),
                data=json,
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return TransactionIncludes.model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def get_transaction(
        self,
        transaction_id: str,
        *,
        include: list[Includes] = ...,
    ) -> Response[TransactionIncludes]:
        """Retrieve a specific transaction."""

        url = f"https://api.paddle.com/transactions/{transaction_id}"

        query = {}

        if include is not ...:
            query["include"] = ",".join(include)

        try:
            response = await self.client.get(
                url,
                params=query,
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[TransactionIncludes].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def update_transaction(
        self,
        transaction_id: str,
        transaction: TransactionUpdate,
        *,
        include: list[Includes] = ...,
    ) -> Response[TransactionIncludes]:
        """Update a specific transaction."""

        url = f"https://api.paddle.com/transactions/{transaction_id}"

        query = {}

        if include is not ...:
            query["include"] = ",".join(include)

        json = transaction.model_dump_json()

        try:
            response = await self.client.patch(
                url,
                params=query,
                auth=BearerAuth(self.token),
                data=json,
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[TransactionIncludes].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def preview_transaction(
        self,
        transaction: TransactionPreviewCreate,
    ) -> Response[TransactionPreview]:
        """Preview a transaction."""

        url = "https://api.paddle.com/transactions/preview"

        json = transaction.model_dump_json()

        try:
            response = await self.client.post(
                url,
                auth=BearerAuth(self.token),
                data=json,
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[TransactionPreview].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def get_transaction_invoice(
        self,
        transaction_id: str,
        *,
        disposition: Disposition = "attachment",
    ) -> Response[InvoiceUrl]:
        """Get the invoice URL for a specific transaction."""

        url = f"https://api.paddle.com/transactions/{transaction_id}/invoice"

        query = {}

        if disposition is not ...:
            query["disposition"] = disposition

        try:
            response = await self.client.get(
                url,
                params=query,
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[InvoiceUrl].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def revise_transaction_customer_information(
        self,
        transaction_id: str,
        revision: TransactionRevise,
    ) -> Response[Transaction]:
        """Revise customer information for a specific transaction."""

        url = f"https://api.paddle.com/transactions/{transaction_id}/revise"

        json = revision.model_dump_json()

        try:
            response = await self.client.post(
                url,
                auth=BearerAuth(self.token),
                data=json,
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[Transaction].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e
