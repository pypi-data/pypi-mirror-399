"""Fonts formats sub-resource: client.fonts.formats"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ..._client import Indox


class Formats:
    """
    Access font format information.

    Usage:
        client.fonts.formats.list()
        client.fonts.formats.get("ttf")
    """

    def __init__(self, client: "Indox") -> None:
        self._client = client

    def list(self) -> dict[str, Any]:
        """
        Get all engines with their supported formats.

        Returns:
            Dict with engines and their input/output format mappings.

        Example:
            >>> formats = client.fonts.formats.list()
            >>> print(formats)
        """
        return cast(dict[str, Any], self._client._http.get("/docs/api/v1/fonts/formats/"))

    def get(self, input_format: str) -> dict[str, Any]:
        """
        Get available output formats for a specific input format.

        Args:
            input_format: Input format (e.g., "ttf", "otf", "woff")

        Returns:
            Dict with available output formats and engines.

        Example:
            >>> outputs = client.fonts.formats.get("ttf")
            >>> print(outputs)
        """
        fmt = _normalize_format(input_format)
        if not fmt:
            raise ValueError("input_format is required")
        return cast(dict[str, Any], self._client._http.get(f"/docs/api/v1/fonts/formats/{fmt}/"))


def _normalize_format(fmt: str) -> str:
    """Normalize format string: lowercase, no leading dot."""
    return (fmt or "").strip().lower().lstrip(".")
