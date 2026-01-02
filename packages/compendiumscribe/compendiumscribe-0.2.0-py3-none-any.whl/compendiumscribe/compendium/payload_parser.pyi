from .compendium import Compendium
from datetime import datetime
from typing import Any

__all__ = ['build_from_payload']

def build_from_payload(cls, topic: str, payload: dict[str, Any], generated_at: datetime | None = None) -> Compendium: ...
