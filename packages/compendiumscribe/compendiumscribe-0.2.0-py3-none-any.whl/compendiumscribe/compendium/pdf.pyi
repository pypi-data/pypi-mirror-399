from .compendium import Compendium
from fpdf import FPDF

__all__ = ['render_pdf']

class CompendiumPDF(FPDF):
    def header(self) -> None: ...
    def footer(self) -> None: ...

def render_pdf(compendium: Compendium) -> bytes: ...
