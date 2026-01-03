from typing import Literal

from httpx import AsyncClient

from pydantic import ValidationError as PydanticValidationError

from paddle.client import BearerAuth
from paddle.schemas import (
    Status,
    Customer1,
    CustomerCreate,
    CustomerUpdate,
    CurrencyCode,
    CreditBalance,
    CustomerAuthenticationToken,
)
from paddle.schemas.response import Response, PaginatedResponse
from paddle.exceptions import ValidationError, ApiError


OrderBy = Literal[
    "id[ASC]",
    "id[DESC]",
]


class CustomerOperationsMixin:
    token: str
    client: AsyncClient

    async def list_customers(
        self,
        *,
        after: str = ...,
        email: list[str] = ...,
        id: list[str] = ...,
        order_by: OrderBy = ...,
        per_page: int = 30,
        search: str = ...,
        status: Status = ...,
    ) -> PaginatedResponse[Customer1]:
        """List customers."""

        url = "https://api.paddle.com/customers"

        query = {}

        if after is not ...:
            query["after"] = after

        if email is not ...:
            query["email"] = ",".join(email)

        if id is not ...:
            query["id"] = ",".join(id)

        if order_by is not ...:
            query["order_by"] = order_by

        if per_page is not ...:
            query["per_page"] = per_page

        if search is not ...:
            query["search"] = search

        if status is not ...:
            query["status"] = status.value

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
            return PaginatedResponse[Customer1].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def create_customer(
        self,
        customer: CustomerCreate,
    ) -> Response[Customer1]:
        """Create a new customer."""

        url = "https://api.paddle.com/customers"

        try:
            response = await self.client.post(
                url,
                json=customer.model_dump(mode="json"),
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[Customer1].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def get_customer(
        self,
        customer_id: str,
    ) -> Response[Customer1]:
        """Retrieve a specific customer by ID."""

        url = f"https://api.paddle.com/customers/{customer_id}"

        try:
            response = await self.client.get(
                url,
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[Customer1].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def update_customer(
        self,
        customer_id: str,
        customer: CustomerUpdate,
    ) -> Response[Customer1]:
        """Update a specific customer by ID."""

        url = f"https://api.paddle.com/customers/{customer_id}"

        try:
            response = await self.client.put(
                url,
                json=customer.model_dump(mode="json"),
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[Customer1].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def get_customer_credit_balances(
        self,
        customer_id: str,
        *,
        currency_codes: list[CurrencyCode] = ...,
    ) -> Response[CreditBalance]:
        """Retrieve credit balances for a specific customer."""

        url = f"https://api.paddle.com/customers/{customer_id}/credit-balances"

        query = {}

        if currency_codes is not ...:
            query["currency_codes"] = ",".join([code.value for code in currency_codes])

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
            return Response[CreditBalance].model_validate_json(response.text)

        except PydanticValidationError as e:
            raise ValidationError from e

    async def create_customer_authentication_token(
        self,
        customer_id: str,
    ) -> Response[CustomerAuthenticationToken]:
        """Create an authentication token for a specific customer."""

        url = f"https://api.paddle.com/customers/{customer_id}/auth-token"

        try:
            response = await self.client.post(
                url,
                auth=BearerAuth(self.token),
            )

            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return Response[CustomerAuthenticationToken].model_validate_json(
                response.text
            )

        except PydanticValidationError as e:
            raise ValidationError from e
