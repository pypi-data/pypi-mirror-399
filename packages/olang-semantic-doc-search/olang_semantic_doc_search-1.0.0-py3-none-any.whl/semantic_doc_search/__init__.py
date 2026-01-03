"""O-lang Semantic Document Search Resolver - Python implementation"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import SemanticDocSearch
from .server import create_app, main

__all__ = ["SemanticDocSearch", "create_app", "main"]