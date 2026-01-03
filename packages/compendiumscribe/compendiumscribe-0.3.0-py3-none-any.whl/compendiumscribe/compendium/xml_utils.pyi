import xml.etree.ElementTree as ET

__all__ = ['etree_to_string']

def etree_to_string(elem: ET.Element, cdata_tags: set[str] | None = None) -> str: ...
