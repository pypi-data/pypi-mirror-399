"""
Decorator Module

Provides aop_entry and rewrite decorators.
"""

from functools import wraps
from typing import Callable, Optional, Any
import inspect

from tspkg_base.aop.registry import register_rewrite, get_rewrite
from tspkg_base.aop.context import ExecutionContext
from tspkg_base.aop.injector import Injector


def rewrite(target: str, mode: str = "around"):
    """
    Rewrite Decorator

    Used to mark a function as a rewrite implementation of an original method.

    Args:
        target: Identifier of the target original method, e.g., "order.create"
        mode: Enhancement mode, options: before, after, around (default)

    Returns:
        Decorator function

    Raises:
        ValueError: If target is empty or mode is invalid

    Example:
        @rewrite(target="order.create", mode="around")
        def my_create_order(ctx):
            # ctx is an ExecutionContext instance
            return ctx.call_original()
    """
    # Parameter validation
    if not target or not isinstance(target, str) or not target.strip():
        raise ValueError("target must be a non-empty string")

    if mode not in ("before", "after", "around"):
        raise ValueError(f"Invalid mode: {mode}. Must be one of: before, after, around")

    def decorator(func: Callable) -> Callable:
        # Validate that func is callable
        if not callable(func):
            raise TypeError("rewrite decorator can only be applied to callable objects")

        # Store mode information in function attributes for later use
        func.__rewrite_mode__ = mode
        func.__rewrite_target__ = target

        # Register to global registry
        register_rewrite(target, func)

        return func

    return decorator


def aop_entry(key: str):
    """
    AOP Entry Decorator

    Used to mark an original method, making it an AOP entry point.
    When the decorated method is called, it will automatically find and execute
    the corresponding rewrite method.

    Args:
        key: Unique identifier of the method, corresponding to the target parameter
             in the rewrite decorator

    Returns:
        Decorator function

    Example:
        @aop_entry(key="order.create")
        def create_order(user_id: int, product_id: int):
            # Original method logic
            return {"order_id": 123}
    """
    # Parameter validation
    if not key or not isinstance(key, str) or not key.strip():
        raise ValueError("key must be a non-empty string")

    def decorator(func: Callable) -> Callable:
        # Check if the function is async
        is_async = inspect.iscoroutinefunction(func)
        
        if is_async:
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                # Construct execution context
                ctx = ExecutionContext(func, args, kwargs)

                # Use Injector to execute rewrite (async version)
                return await Injector.execute_rewrite_async(key, ctx)
            
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Construct execution context
                ctx = ExecutionContext(func, args, kwargs)

                # Use Injector to execute rewrite
                return Injector.execute_rewrite(key, ctx)

            return wrapper

    return decorator

