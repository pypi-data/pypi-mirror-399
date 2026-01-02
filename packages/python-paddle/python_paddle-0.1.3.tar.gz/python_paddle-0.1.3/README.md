# Unofficial Paddle Billing Python SDK

A small Paddle Billing SDK. It uses pydantic for schemas derived from the Paddle Billing OpenAPI
file.

## Installation

To install the package, install it from pypi:

```sh
uv add python-paddle
# or
pip install python-paddle
```

Or your favorite package manager.

## Usage

Currently, the SDK does not provide functions to call the API. It does provide two things:

1. API schemas as Pydantic models
2. Webhook validation

The schemas can be found under `paddle.schemas`, like `paddle.schemas.Transaction`.

Webhooks can be validated using `paddle.webhooks.verify`. For example:

```py
from paddle import webhooks

webhooks.verify(
    secret="YOUR_WEBHOOK_SECRET",
    signature="YOUR_WEBHOOK_SIGNATURE",  # Extract this value from the `Paddle-Signature` in the webhook request
    body="THE_REQUEST_BODY",
)
```

It'll raise a `paddle.webhooks.exceptions.ValidationError` if the webhook could not be verified,
otherwise it'll return `True`.

To instead get a `bool` returned from the function, without an error raised on failure, pass the
`error=False` argument.

```py
from paddle import webhooks

is_valid = webhooks.verify(
    secret="YOUR_WEBHOOK_SECRET",
    signature="YOUR_WEBHOOK_SIGNATURE",  # Extract this value from the `Paddle-Signature` in the webhook request
    body="THE_REQUEST_BODY",
    error=False,
)

if is_valid:
    print("Great!")

else:
    print("Damn")
```

### Exceptions

All exceptions raised by this library inherit from `paddle.exceptions.PaddleException`.
