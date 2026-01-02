"""
Python Secondary Development Platform Base

Provides AOP, Hook, and Rewrite capabilities, allowing external business packages
to dynamically take over, rewrite, or enhance the execution logic of original methods
without modifying the original project code.
"""

__version__ = "0.1.7"

from tspkg_base.aop.decorators import aop_entry, rewrite
from tspkg_base.aop.registry import REWRITE_REGISTRY

__all__ = [
    "aop_entry",
    "rewrite",
    "REWRITE_REGISTRY",
]

