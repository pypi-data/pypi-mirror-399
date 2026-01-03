from .compendium import Compendium
from _typeshed import Incomplete
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

__all__ = ['SkillConfig', 'SkillGenerationError', 'SkillMetadata', 'SkillProgress', 'render_skill_folder']

class SkillGenerationError(RuntimeError): ...

@dataclass(frozen=True)
class SkillProgress:
    phase: str
    status: str
    message: str
    metadata: dict[str, Any] | None = ...

@dataclass
class SkillConfig:
    skill_namer_model: str = field(default_factory=Incomplete)
    skill_writer_model: str = field(default_factory=Incomplete)
    reasoning_effort: str = ...
    max_retries: int = ...
    progress_callback: Callable[[SkillProgress], None] | None = ...

@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str

def render_skill_folder(compendium: Compendium, base_path: Path, client: Any, config: SkillConfig | None = None) -> Path: ...
