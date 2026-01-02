"""Fonts conversions sub-resource: client.fonts.conversions"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, cast

from ..._exceptions import ConversionError, ConversionTimeoutError

if TYPE_CHECKING:
    from ..._client import Indox


class Conversions:
    """
    Access font conversion status and downloads.

    Usage:
        client.fonts.conversions.get(conversion_id)
        client.fonts.conversions.wait(conversion_id)
        client.fonts.conversions.download(conversion_id, output_path)
    """

    def __init__(self, client: "Indox") -> None:
        self._client = client

    def get(self, conversion_id: str) -> dict[str, Any]:
        """
        Get conversion status and metadata.

        Args:
            conversion_id: The conversion UUID.

        Returns:
            Dict with status, success flag, download_url, etc.

        Example:
            >>> status = client.fonts.conversions.get("abc-123")
            >>> print(status["status"])  # "completed", "pending", "failed"
        """
        if not conversion_id:
            raise ValueError("conversion_id is required")
        return cast(dict[str, Any], self._client._http.get(f"/docs/api/v1/fonts/conversion/{conversion_id}/"))

    def wait(
        self,
        conversion_id: str,
        *,
        timeout: float = 60.0,
        poll_interval: float = 0.5,
    ) -> dict[str, Any]:
        """
        Wait for conversion to complete.

        Args:
            conversion_id: The conversion UUID.
            timeout: Max seconds to wait (default: 60).
            poll_interval: Seconds between status checks (default: 0.5).

        Returns:
            Final conversion status dict.

        Raises:
            ConversionError: If conversion fails.
            ConversionTimeoutError: If timeout exceeded.

        Example:
            >>> result = client.fonts.conversions.wait("abc-123", timeout=30)
            >>> print(result["download_url"])
        """
        if not conversion_id:
            raise ValueError("conversion_id is required")

        start = time.time()
        while True:
            status = self.get(conversion_id)

            if status.get("status") == "completed":
                return status

            if status.get("status") == "failed":
                raise ConversionError(
                    status.get("error", "Conversion failed"),
                    conversion_id=conversion_id,
                )

            elapsed = time.time() - start
            if elapsed > timeout:
                raise ConversionTimeoutError(
                    f"Conversion {conversion_id} timed out after {timeout}s"
                )

            time.sleep(poll_interval)

    def download(
        self,
        conversion_id: str,
        output_path: str | Path,
        *,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Download converted font file.

        Args:
            conversion_id: The conversion UUID.
            output_path: Local path to save the file.
            filename: Optional filename for URL (defaults to "file").

        Returns:
            Path to downloaded file.

        Example:
            >>> path = client.fonts.conversions.download("abc-123", "./output/myfont.woff2")
        """
        if not conversion_id:
            raise ValueError("conversion_id is required")

        fname = filename or "file"
        response = self._client._http.get(
            f"/docs/api/v1/fonts/{conversion_id}/download/{fname}",
            stream=True,
        )

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)

        return target
