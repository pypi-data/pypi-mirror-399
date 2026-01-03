"""
thinkpdf - The Ultimate PDF to Markdown Converter

Combines the best of pdfmd and Marker with exclusive features:
- Modern GUI with CustomTkinter
- CLI tool for automation
- MCP Server for IDE integration
- Intelligent caching
- Optional LLM validation
"""

__version__ = "1.0.0"
__author__ = "thinkpdf Team"

from .core.extractor import PDFExtractor
from .core.converter import PDFConverter

__all__ = [
    "PDFExtractor",
    "PDFConverter",
    "__version__",
]
