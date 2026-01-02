from .compendium import Compendium

__all__ = ['render_html_site']

def render_html_site(compendium: Compendium) -> dict[str, str]: ...
