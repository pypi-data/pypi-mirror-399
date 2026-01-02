"""
AOP Core Module

Provides decorators, registry, execution context, and injector functionality.
"""

from tspkg_base.aop.decorators import aop_entry, rewrite
from tspkg_base.aop.registry import REWRITE_REGISTRY
from tspkg_base.aop.context import ExecutionContext

__all__ = [
    "aop_entry",
    "rewrite",
    "REWRITE_REGISTRY",
    "ExecutionContext",
]

