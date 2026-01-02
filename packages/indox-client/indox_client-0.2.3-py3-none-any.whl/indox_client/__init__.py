"""
Indox Python SDK

Usage:
    >>> from indox_client import Indox
    >>> client = Indox(api_key="your-api-key")
    >>>
    >>> # List supported formats
    >>> client.fonts.formats.list()
    >>>
    >>> # Convert font file
    >>> job = client.fonts.convert_file("./font.ttf", target_format="woff2")
    >>> client.fonts.conversions.wait(job["id"])
    >>> client.fonts.conversions.download(job["id"], "./font.woff2")
    >>>
    >>> # Or all-in-one
    >>> client.fonts.convert_and_download(
    ...     "./font.ttf",
    ...     target_format="woff2",
    ...     output_path="./font.woff2"
    ... )
"""

from ._client import Indox
from ._exceptions import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConversionError,
    ConversionTimeoutError,
    IndoxError,
    InternalServerError,
    NotFoundError,
    PaymentRequiredError,
    PermissionDeniedError,
    RateLimitError,
)
from ._version import __version__

__all__ = [
    "__version__",
    "Indox",
    # Exceptions
    "IndoxError",
    "APIConnectionError",
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "PaymentRequiredError",
    "PermissionDeniedError",
    "NotFoundError",
    "RateLimitError",
    "InternalServerError",
    "ConversionError",
    "ConversionTimeoutError",
]
