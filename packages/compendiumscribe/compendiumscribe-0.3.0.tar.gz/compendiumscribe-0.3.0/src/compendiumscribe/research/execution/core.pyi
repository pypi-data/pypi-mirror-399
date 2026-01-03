from ..cancellation import CancellationContext
from ..config import ResearchConfig
from typing import Any

__all__ = ['execute_deep_research']

def execute_deep_research(client: Any, prompt: Any, config: ResearchConfig, cancel_ctx: CancellationContext | None = None): ...
