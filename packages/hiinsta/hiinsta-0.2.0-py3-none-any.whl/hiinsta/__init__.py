"""
hiinsta - A Python package for hiinsta functionality.
"""

__version__ = "0.2.0"
__author__ = "Tomas Santana"
__email__ = "tomas@cervant.chat"

from .InstagramMessenger import InstagramMessenger
from .types import Update

__all__ = ["InstagramMessenger", "Update"]

__all__ = ["InstagramMessenger"]
