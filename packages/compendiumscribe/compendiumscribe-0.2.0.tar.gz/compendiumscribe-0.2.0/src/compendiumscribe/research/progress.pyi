from .config import ResearchConfig
from _typeshed import Incomplete
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

__all__ = ['ProgressPhase', 'ProgressStatus', 'ResearchProgress', 'emit_progress']

ProgressPhase: Incomplete
ProgressStatus: Incomplete

@dataclass(slots=True)
class ResearchProgress:
    phase: ProgressPhase
    status: ProgressStatus
    message: str
    metadata: dict[str, Any] | None = ...
    timestamp: datetime = field(default_factory=Incomplete)

def emit_progress(config: ResearchConfig, *, phase: ProgressPhase, status: ProgressStatus, message: str, metadata: dict[str, Any] | None = None) -> None: ...
