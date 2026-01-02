"""Base HTTP client with shared logic."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Mapping, Optional

import requests

from ._exceptions import APIConnectionError, raise_for_status
from ._version import __version__

if TYPE_CHECKING:
    from ._client import Indox

DEFAULT_TIMEOUT = (5.0, 60.0)  # (connect, read)


class BaseClient:
    """Low-level HTTP client used by all resources."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: Optional[tuple[float, float]] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._session = session or requests.Session()
        self._user_agent = f"indox-client/{__version__}"

    @property
    def base_url(self) -> str:
        return self._base_url

    def _build_headers(self, extra: Optional[Mapping[str, str]] = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": self._user_agent,
        }
        if extra:
            headers.update({k: v for k, v in extra.items() if v is not None})
        return headers

    def _build_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        path = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[tuple[float, float]] = None,
        stream: bool = False,
    ) -> Any:
        """Execute HTTP request and handle response."""
        url = self._build_url(path)
        final_headers = self._build_headers(headers)

        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_body,
                data=data,
                files=files,
                headers=final_headers,
                timeout=timeout or self._timeout,
                stream=stream,
            )
        except requests.RequestException as exc:
            raise APIConnectionError(f"Connection error: {exc}") from exc

        return self._handle_response(response, stream=stream)

    def _handle_response(self, response: requests.Response, stream: bool = False) -> Any:
        """Process response and raise appropriate errors."""
        if response.status_code >= 400:
            payload = self._safe_json(response)
            message = payload.get("detail") if isinstance(payload, dict) else response.text
            raise_for_status(
                response.status_code,
                message or f"HTTP {response.status_code}",
                response=payload if isinstance(payload, dict) else None,
                request_id=response.headers.get("X-Request-ID"),
            )

        if stream:
            return response

        if not response.content:
            return {}

        return self._safe_json(response)

    def _safe_json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw": response.text}

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(
        self,
        path: str,
        *,
        json_body: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        return self.request("POST", path, json_body=json_body, data=data, files=files, **kwargs)

    def close(self) -> None:
        self._session.close()


class SyncAPIResource:
    """Base class for API resources."""

    _client: "Indox"

    def __init__(self, client: "Indox") -> None:
        self._client = client

    @property
    def _http(self) -> BaseClient:
        return self._client._http
