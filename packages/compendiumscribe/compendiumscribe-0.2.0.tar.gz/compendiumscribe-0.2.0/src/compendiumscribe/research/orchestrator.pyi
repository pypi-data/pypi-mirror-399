from ..compendium import Compendium
from .cancellation import CancellationContext
from .config import ResearchConfig
from openai import OpenAI

__all__ = ['build_compendium', 'recover_compendium']

def build_compendium(topic: str, *, client: OpenAI | None = None, config: ResearchConfig | None = None, cancel_ctx: CancellationContext | None = None) -> Compendium: ...
def recover_compendium(research_id: str, topic: str, *, client: OpenAI | None = None, config: ResearchConfig | None = None) -> Compendium: ...
