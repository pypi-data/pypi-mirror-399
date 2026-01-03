import httpx

from paddle.operations.customers import CustomerOperationsMixin
from paddle.operations.transactions import TransactionOperationsMixin


class Paddle(CustomerOperationsMixin, TransactionOperationsMixin):
    """A Paddle client."""

    client = httpx.AsyncClient()

    def __init__(self, token: str):
        """Initialize a Paddle client.

        Args:
            token (str): The API token for authentication.
        """

        self.token = token


class BearerAuth(httpx.Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request
