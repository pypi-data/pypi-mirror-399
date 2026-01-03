from _typeshed import Incomplete

__all__ = ['DeepResearchError', 'MissingConfigurationError', 'ResearchCancelledError', 'ResearchTimeoutError']

class DeepResearchError(RuntimeError): ...
class MissingConfigurationError(RuntimeError): ...

class ResearchTimeoutError(DeepResearchError):
    research_id: Incomplete
    def __init__(self, message: str, research_id: str) -> None: ...

class ResearchCancelledError(DeepResearchError):
    research_id: Incomplete
    def __init__(self, message: str, research_id: str) -> None: ...
