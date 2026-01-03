import xml.etree.ElementTree as ET
from .entities import Citation, Section
from _typeshed import Incomplete
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

__all__ = ['Compendium']

@dataclass
class Compendium:
    XML_CDATA_TAGS = ...
    topic: str
    overview: str
    methodology: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=Incomplete)
    def to_xml(self) -> ET.Element: ...
    def to_xml_string(self) -> str: ...
    def to_markdown(self) -> str: ...
    def to_html_site(self) -> dict[str, str]: ...
    def to_pdf_bytes(self) -> bytes: ...
    @classmethod
    def from_payload(cls, topic: str, payload: dict[str, Any], generated_at: datetime | None = None) -> Compendium: ...
    @classmethod
    def from_xml_file(cls, path: str) -> Compendium: ...
    @classmethod
    def from_xml_string(cls, content: str) -> Compendium: ...
