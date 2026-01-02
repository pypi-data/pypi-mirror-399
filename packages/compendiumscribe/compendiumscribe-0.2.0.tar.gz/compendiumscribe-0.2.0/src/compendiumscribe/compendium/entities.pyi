import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

__all__ = ['Citation', 'Insight', 'Section']

@dataclass
class Citation:
    identifier: str
    title: str
    url: str
    publisher: str | None = ...
    published_at: str | None = ...
    summary: str | None = ...
    def to_xml(self) -> ET.Element: ...

@dataclass
class Insight:
    title: str
    evidence: str
    implications: str | None = ...
    citation_refs: list[str] = field(default_factory=list)
    def to_xml(self) -> ET.Element: ...

@dataclass
class Section:
    identifier: str
    title: str
    summary: str
    key_terms: list[str] = field(default_factory=list)
    guiding_questions: list[str] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    def to_xml(self) -> ET.Element: ...
