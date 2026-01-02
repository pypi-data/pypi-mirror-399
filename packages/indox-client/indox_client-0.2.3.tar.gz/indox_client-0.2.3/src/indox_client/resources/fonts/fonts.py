"""Fonts resource: client.fonts"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, cast

from .conversions import Conversions
from .formats import Formats
from ..._exceptions import IndoxError

if TYPE_CHECKING:
    from ..._client import Indox


class Fonts:
    """
    Font conversion API.

    Sub-resources:
        - formats: List and query supported formats
        - conversions: Get status, wait, download

    Direct methods:
        - upload(): Upload font file to S3
        - convert(): Start conversion from S3 key
        - validate(): Validate conversion without executing

    Convenience methods:
        - convert_file(): Upload + convert in one call
        - convert_and_download(): Full pipeline

    Example:
        >>> from indox_client import Indox
        >>> client = Indox(api_key="xxx")
        >>>
        >>> # Check formats
        >>> client.fonts.formats.list()
        >>> client.fonts.formats.get("ttf")
        >>>
        >>> # Convert a file
        >>> result = client.fonts.convert_file("./font.ttf", target_format="woff2")
        >>> client.fonts.conversions.wait(result["id"])
        >>> client.fonts.conversions.download(result["id"], "./font.woff2")
    """

    def __init__(self, client: "Indox") -> None:
        self._client = client
        self.formats = Formats(client)
        self.conversions = Conversions(client)

    def upload(self, file_path: str | os.PathLike[str]) -> dict[str, Any]:
        """
        Upload font file to S3.

        Args:
            file_path: Path to font file.

        Returns:
            Dict with s3_key, filename, format, size_bytes.

        Example:
            >>> result = client.fonts.upload("./myfont.ttf")
            >>> print(result["s3_key"])
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with path.open("rb") as fh:
            files = {"file": (path.name, fh)}
            return cast(dict[str, Any], self._client._http.post("/docs/api/v1/fonts/upload/", data={}, files=files))

    def convert(
        self,
        s3_key: str,
        *,
        target_format: str,
        filename: Optional[str] = None,
        external_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Start conversion for uploaded file.

        Args:
            s3_key: S3 key from upload().
            target_format: Output format (e.g., "woff2", "otf").
            filename: Optional original filename.
            external_token: Optional tracking token.

        Returns:
            Dict with id, status, download_url.

        Example:
            >>> upload = client.fonts.upload("./font.ttf")
            >>> job = client.fonts.convert(upload["s3_key"], target_format="woff2")
            >>> print(job["id"])
        """
        fmt = _normalize_format(target_format)
        if not fmt:
            raise ValueError("target_format is required")
        if not s3_key:
            raise ValueError("s3_key is required")

        payload: dict[str, Any] = {"s3_key": s3_key, "target_format": fmt}
        if filename:
            payload["filename"] = filename
        if external_token:
            payload["external_token"] = external_token

        return cast(dict[str, Any], self._client._http.post("/docs/api/v1/fonts/convert/", json_body=payload))

    def validate(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Validate conversion without executing.

        Args:
            file_path: Path to font file.
            target_format: Optional target format to validate.

        Returns:
            Dict with valid flag, input/output formats, engine, credits.

        Example:
            >>> result = client.fonts.validate("./font.ttf", target_format="woff2")
            >>> if result["valid"]:
            ...     print(f"Will use {result['engine']}")
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        params = {}
        if target_format:
            params["target_format"] = _normalize_format(target_format)

        with path.open("rb") as fh:
            files = {"file": (path.name, fh)}
            return cast(dict[str, Any], self._client._http.post(
                "/docs/api/v1/fonts/validate/", data={}, files=files, params=params
            ))

    # ------------------------------------------------------------------ #
    # Convenience methods
    # ------------------------------------------------------------------ #

    def convert_file(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: str,
        external_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Upload and convert in one call.

        Args:
            file_path: Path to font file.
            target_format: Output format.
            external_token: Optional tracking token.

        Returns:
            Conversion result with id and status.

        Example:
            >>> job = client.fonts.convert_file("./font.ttf", target_format="woff2")
            >>> print(job["id"])
        """
        upload_result = self.upload(file_path)
        return self.convert(
            upload_result["s3_key"],
            target_format=target_format,
            filename=upload_result.get("filename"),
            external_token=external_token,
        )

    def convert_and_download(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: str,
        output_path: str | Path,
        external_token: Optional[str] = None,
        timeout: float = 60.0,
        poll_interval: float = 0.5,
    ) -> Path:
        """
        Full pipeline: upload, convert, wait, download.

        Args:
            file_path: Path to font file.
            target_format: Output format.
            output_path: Where to save converted file.
            external_token: Optional tracking token.
            timeout: Max wait time in seconds.
            poll_interval: Poll interval in seconds.

        Returns:
            Path to downloaded file.

        Example:
            >>> path = client.fonts.convert_and_download(
            ...     "./font.ttf",
            ...     target_format="woff2",
            ...     output_path="./font.woff2"
            ... )
        """
        job = self.convert_file(
            file_path, target_format=target_format, external_token=external_token
        )
        self.conversions.wait(job["id"], timeout=timeout, poll_interval=poll_interval)
        return self.conversions.download(job["id"], output_path)


def _normalize_format(fmt: str) -> str:
    """Normalize format string: lowercase, no leading dot."""
    return (fmt or "").strip().lower().lstrip(".")
