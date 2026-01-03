"""
godaddycheck - Simple GoDaddy domain availability checker.
"""

from .client import GoDaddyClient, check, suggest, tlds

__version__ = "0.1.1"
__all__ = ["GoDaddyClient", "check", "suggest", "tlds"]
