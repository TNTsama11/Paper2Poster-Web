"""
Paper2Poster-Web (P2P-Web)
将学术论文 PDF 自动转换为学术海报
"""
__version__ = "1.0.0"

from .harvester import PDFHarvester
from .editor import LLMEditor
from .renderer import PosterRenderer
from .models import PosterContent, Section

__all__ = [
    'PDFHarvester',
    'LLMEditor',
    'PosterRenderer',
    'PosterContent',
    'Section',
]

