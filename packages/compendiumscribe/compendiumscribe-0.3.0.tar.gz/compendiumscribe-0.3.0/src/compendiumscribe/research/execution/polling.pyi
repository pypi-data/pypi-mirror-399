from ..cancellation import CancellationContext
from ..config import ResearchConfig
from typing import Any

__all__ = ['await_completion']

def await_completion(client: Any, response: Any, config: ResearchConfig, cancel_ctx: CancellationContext | None = None): ...
