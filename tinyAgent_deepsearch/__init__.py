# tinyAgent_deepsearch - A Python library for deep research

"""
tinyAgent_deepsearch

This library provides tools for performing deep research using AI agents.
"""

__version__ = "0.1.0"

from .core import deep_research
from .exceptions import MissingAPIKeyError

__all__ = [
    "deep_research",
    "MissingAPIKeyError",
]