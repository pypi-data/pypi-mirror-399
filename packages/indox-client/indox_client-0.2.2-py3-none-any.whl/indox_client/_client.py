"""Main Indox client."""

from __future__ import annotations

import os
from typing import Optional

from ._base import BaseClient
from .resources import Fonts

DEFAULT_BASE_URL = "https://indox.org"


class Indox:
    """
    Indox API client.

    Usage:
        >>> from indox_client import Indox
        >>> client = Indox(api_key="your-api-key")
        >>>
        >>> # Font conversion
        >>> client.fonts.formats.list()
        >>> client.fonts.convert_file("./font.ttf", target_format="woff2")
        >>>
        >>> # With context manager
        >>> with Indox(api_key="xxx") as client:
        ...     client.fonts.convert_and_download(
        ...         "./font.ttf",
        ...         target_format="woff2",
        ...         output_path="./font.woff2"
        ...     )

    Attributes:
        fonts: Font conversion API
        # images: Image conversion API (coming soon)
        # videos: Video conversion API (coming soon)
    """

    fonts: Fonts
    # images: Images
    # videos: Videos

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[tuple[float, float]] = None,
    ) -> None:
        """
        Initialize the Indox client.

        Args:
            api_key: API key. Falls back to INDOX_API_KEY env var.
            base_url: Base URL. Falls back to INDOX_BASE_URL env var or https://indox.org.
            timeout: Request timeout as (connect, read) tuple.

        Raises:
            ValueError: If api_key is not provided.
        """
        key = (api_key or os.getenv("INDOX_API_KEY") or "").strip()
        if not key:
            raise ValueError("api_key is required. Pass it directly or set INDOX_API_KEY.")

        url = (base_url or os.getenv("INDOX_BASE_URL") or DEFAULT_BASE_URL).strip().rstrip("/")

        self._http = BaseClient(base_url=url, api_key=key, timeout=timeout)

        # Initialize resources
        self.fonts = Fonts(self)
        # self.images = Images(self)  # Coming soon
        # self.videos = Videos(self)  # Coming soon

    @property
    def base_url(self) -> str:
        """Return the base URL."""
        return self._http.base_url

    def close(self) -> None:
        """Close the HTTP session."""
        self._http.close()

    def __enter__(self) -> "Indox":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Indox(base_url={self.base_url!r})"
