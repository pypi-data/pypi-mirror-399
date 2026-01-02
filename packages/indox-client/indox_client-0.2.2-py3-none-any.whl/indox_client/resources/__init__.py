from typing import Any
from .fonts.fonts import Fonts

__all__ = ["Fonts", "Images", "Videos"]


class Images:
    """Image conversion API (coming soon)."""

    def __init__(self, client: Any) -> None:
        raise NotImplementedError("Images API coming soon")


class Videos:
    """Video conversion API (coming soon)."""

    def __init__(self, client: Any) -> None:
        raise NotImplementedError("Videos API coming soon")
