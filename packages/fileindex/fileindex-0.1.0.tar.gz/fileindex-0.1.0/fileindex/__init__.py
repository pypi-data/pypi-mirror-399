"""
fileindex - Fast local file indexing and searching tool
"""

__version__ = "0.1.0"
__author__ = "Dhritikrishna Tripathi"

from .core.scan import Scan
from .core.search import Search
from .core.cache import IndexCache

__all__ = ["Scan", "Search", "IndexCache"]
