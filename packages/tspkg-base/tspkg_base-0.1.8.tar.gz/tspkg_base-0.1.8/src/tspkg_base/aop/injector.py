"""
Injector Module

Responsible for finding rewrite methods and executing injection logic.
"""

from typing import Optional, Callable, Any
import logging
import inspect

from tspkg_base.aop.context import ExecutionContext
from tspkg_base.aop.registry import get_rewrite
from tspkg_base.runtime.exception_handler import ExceptionHandler

logger = logging.getLogger(__name__)


class Injector:
    """
    Injector

    Responsible for finding and executing corresponding rewrite methods when
    methods marked with aop_entry are executed.
    """

    # Default exception handling strategy: fallback_to_original (fallback to original method)
    # Options: raise (raise exception), fallback_to_original (execute original method), ignore (ignore exception)
    DEFAULT_EXCEPTION_STRATEGY = "fallback_to_original"
    
    # Default timeout (seconds), 0 means no timeout
    DEFAULT_TIMEOUT = 0

    @staticmethod
    def execute_rewrite(
        key: str,
        ctx: ExecutionContext,
        rewrite_func: Optional[Callable] = None,
        exception_strategy: str = DEFAULT_EXCEPTION_STRATEGY,
        timeout: float = DEFAULT_TIMEOUT
    ) -> Any:
        """
        Execute rewrite method

        Args:
            key: Identifier of the rewrite
            ctx: Execution context
            rewrite_func: Rewrite function (optional, if not provided, will be looked up from registry)
            exception_strategy: Exception handling strategy
                - "raise": Raise exception (default behavior, suitable for development)
                - "fallback_to_original": Fallback to execute original method (suitable for production)
                - "ignore": Ignore exception and continue (not recommended)
            timeout: Timeout in seconds, 0 means no timeout

        Returns:
            Execution result

        Raises:
            Exception: If rewrite method raises exception and exception_strategy is "raise"
            TimeoutError: If execution times out
        """
        # If rewrite_func is not provided, look it up from registry
        if rewrite_func is None:
            rewrite_func = get_rewrite(key)

        # If no rewrite is found, directly execute original method
        if not rewrite_func:
            result = ctx.call_original()
            # If the original function is async, we need to handle it
            if inspect.iscoroutine(result):
                raise RuntimeError(
                    "Original function is async but execute_rewrite is sync. "
                    "Use execute_rewrite_async instead."
                )
            return result

        # Get mode from rewrite function attributes (if exists)
        mode = getattr(rewrite_func, "__rewrite_mode__", "around")

        # Define execution function
        def execute_rewrite_mode():
            if mode == "before":
                return Injector._execute_before_mode(rewrite_func, ctx)
            elif mode == "after":
                return Injector._execute_after_mode(rewrite_func, ctx)
            else:  # mode == "around"
                return Injector._execute_around_mode(rewrite_func, ctx)

        try:
            # Use timeout control if timeout is enabled
            if timeout > 0:
                return ExceptionHandler.execute_with_timeout(
                    execute_rewrite_mode,
                    timeout,
                    rewrite_key=key
                )
            else:
                return execute_rewrite_mode()
        except Exception as e:
            # Record exception
            ctx.set_exception(e)
            
            # Distinguish timeout exceptions from other exceptions
            if isinstance(e, TimeoutError):
                logger.error(
                    f"Rewrite '{key}' (mode={mode}) execution timeout: {e}",
                    exc_info=False  # Timeout doesn't need full traceback
                )
            else:
                logger.error(
                    f"Error executing rewrite '{key}' (mode={mode}): {e}",
                    exc_info=True
                )

            # Handle according to exception strategy
            if exception_strategy == "raise":
                raise
            elif exception_strategy == "fallback_to_original":
                logger.warning(f"Falling back to original function for '{key}' due to rewrite error")
                # If original method has been called (e.g., in after mode), return result directly
                if ctx.is_original_called():
                    return ctx.result
                # Otherwise call original method
                return ctx.call_original()
            elif exception_strategy == "ignore":
                logger.warning(f"Ignoring exception in rewrite '{key}', returning None")
                # If original method has been called, return original method result instead of None
                if ctx.is_original_called():
                    return ctx.result
                return None
            else:
                logger.warning(f"Unknown exception_strategy '{exception_strategy}', falling back to original")
                if ctx.is_original_called():
                    return ctx.result
                return ctx.call_original()

    @staticmethod
    def _execute_before_mode(rewrite_func: Callable, ctx: ExecutionContext) -> Any:
        """
        Execute rewrite in before mode

        Args:
            rewrite_func: Rewrite function
            ctx: Execution context

        Returns:
            Execution result
        """
        # Pre-enhancement: execute rewrite first, then original method
        rewrite_result = rewrite_func(ctx)
        if inspect.iscoroutine(rewrite_result):
            raise RuntimeError(
                "Rewrite function is async but execute_rewrite is sync. "
                "Use execute_rewrite_async instead."
            )
        
        if not ctx.skip_original:
            result = ctx.call_original()
            if inspect.iscoroutine(result):
                raise RuntimeError(
                    "Original function is async but execute_rewrite is sync. "
                    "Use execute_rewrite_async instead."
                )
            return result
        # If skip_original is True, return result set by rewrite
        return ctx.result if ctx.result is not None else None

    @staticmethod
    def _execute_after_mode(rewrite_func: Callable, ctx: ExecutionContext) -> Any:
        """
        Execute rewrite in after mode

        Args:
            rewrite_func: Rewrite function
            ctx: Execution context

        Returns:
            Execution result
        """
        # Post-enhancement: execute original method first, then rewrite
        original_result = ctx.call_original()
        if inspect.iscoroutine(original_result):
            raise RuntimeError(
                "Original function is async but execute_rewrite is sync. "
                "Use execute_rewrite_async instead."
            )
        ctx.result = original_result
        # If rewrite raises exception, original method result is already saved in ctx.result
        rewrite_result = rewrite_func(ctx)
        if inspect.iscoroutine(rewrite_result):
            raise RuntimeError(
                "Rewrite function is async but execute_rewrite is sync. "
                "Use execute_rewrite_async instead."
            )
        return ctx.result

    @staticmethod
    def _execute_around_mode(rewrite_func: Callable, ctx: ExecutionContext) -> Any:
        """
        Execute rewrite in around mode

        Args:
            rewrite_func: Rewrite function
            ctx: Execution context

        Returns:
            Execution result
        """
        # Around enhancement: completely controlled by rewrite
        result = rewrite_func(ctx)
        # Check if rewrite function is async
        if inspect.iscoroutine(result):
            raise RuntimeError(
                "Rewrite function is async but execute_rewrite is sync. "
                "Use execute_rewrite_async instead."
            )
        return result
    
    @staticmethod
    async def execute_rewrite_async(
        key: str,
        ctx: ExecutionContext,
        rewrite_func: Optional[Callable] = None,
        exception_strategy: str = DEFAULT_EXCEPTION_STRATEGY,
        timeout: float = DEFAULT_TIMEOUT
    ) -> Any:
        """
        Execute rewrite method (async version)

        Args:
            key: Identifier of the rewrite
            ctx: Execution context
            rewrite_func: Rewrite function (optional, if not provided, will be looked up from registry)
            exception_strategy: Exception handling strategy
                - "raise": Raise exception (default behavior, suitable for development)
                - "fallback_to_original": Fallback to execute original method (suitable for production)
                - "ignore": Ignore exception and continue (not recommended)
            timeout: Timeout in seconds, 0 means no timeout

        Returns:
            Execution result

        Raises:
            Exception: If rewrite method raises exception and exception_strategy is "raise"
            TimeoutError: If execution times out
        """
        # If rewrite_func is not provided, look it up from registry
        if rewrite_func is None:
            rewrite_func = get_rewrite(key)

        # If no rewrite is found, directly execute original method
        if not rewrite_func:
            return await ctx.call_original_async()

        # Get mode from rewrite function attributes (if exists)
        mode = getattr(rewrite_func, "__rewrite_mode__", "around")

        # Define execution function
        async def execute_rewrite_mode():
            if mode == "before":
                return await Injector._execute_before_mode_async(rewrite_func, ctx)
            elif mode == "after":
                return await Injector._execute_after_mode_async(rewrite_func, ctx)
            else:  # mode == "around"
                return await Injector._execute_around_mode_async(rewrite_func, ctx)

        try:
            # Use timeout control if timeout is enabled
            if timeout > 0:
                return await ExceptionHandler.execute_with_timeout_async(
                    execute_rewrite_mode,
                    timeout,
                    rewrite_key=key
                )
            else:
                return await execute_rewrite_mode()
        except Exception as e:
            # Record exception
            ctx.set_exception(e)
            
            # Distinguish timeout exceptions from other exceptions
            if isinstance(e, TimeoutError):
                logger.error(
                    f"Rewrite '{key}' (mode={mode}) execution timeout: {e}",
                    exc_info=False  # Timeout doesn't need full traceback
                )
            else:
                logger.error(
                    f"Error executing rewrite '{key}' (mode={mode}): {e}",
                    exc_info=True
                )

            # Handle according to exception strategy
            if exception_strategy == "raise":
                raise
            elif exception_strategy == "fallback_to_original":
                logger.warning(f"Falling back to original function for '{key}' due to rewrite error")
                # If original method has been called (e.g., in after mode), return result directly
                if ctx.is_original_called():
                    return ctx.result
                # Otherwise call original method
                return await ctx.call_original_async()
            elif exception_strategy == "ignore":
                logger.warning(f"Ignoring exception in rewrite '{key}', returning None")
                # If original method has been called, return original method result instead of None
                if ctx.is_original_called():
                    return ctx.result
                return None
            else:
                logger.warning(f"Unknown exception_strategy '{exception_strategy}', falling back to original")
                if ctx.is_original_called():
                    return ctx.result
                return await ctx.call_original_async()

    @staticmethod
    async def _execute_before_mode_async(rewrite_func: Callable, ctx: ExecutionContext) -> Any:
        """
        Execute rewrite in before mode (async version)

        Args:
            rewrite_func: Rewrite function
            ctx: Execution context

        Returns:
            Execution result
        """
        # Pre-enhancement: execute rewrite first, then original method
        rewrite_result = rewrite_func(ctx)
        if inspect.iscoroutine(rewrite_result):
            await rewrite_result
        
        if not ctx.skip_original:
            return await ctx.call_original_async()
        # If skip_original is True, return result set by rewrite
        return ctx.result if ctx.result is not None else None

    @staticmethod
    async def _execute_after_mode_async(rewrite_func: Callable, ctx: ExecutionContext) -> Any:
        """
        Execute rewrite in after mode (async version)

        Args:
            rewrite_func: Rewrite function
            ctx: Execution context

        Returns:
            Execution result
        """
        # Post-enhancement: execute original method first, then rewrite
        original_result = await ctx.call_original_async()
        ctx.result = original_result
        # If rewrite raises exception, original method result is already saved in ctx.result
        rewrite_result = rewrite_func(ctx)
        if inspect.iscoroutine(rewrite_result):
            await rewrite_result
        return ctx.result

    @staticmethod
    async def _execute_around_mode_async(rewrite_func: Callable, ctx: ExecutionContext) -> Any:
        """
        Execute rewrite in around mode (async version)

        Args:
            rewrite_func: Rewrite function
            ctx: Execution context

        Returns:
            Execution result
        """
        # Around enhancement: completely controlled by rewrite
        result = rewrite_func(ctx)
        if inspect.iscoroutine(result):
            return await result
        return result

