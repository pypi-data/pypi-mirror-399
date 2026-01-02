"""
Exception Handler Module

Provides exception isolation and handling mechanisms for secondary development code.
"""

import logging
import traceback
import threading
import asyncio
from typing import Any, Callable, Optional, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class RewriteException(Exception):
    """
    Rewrite Execution Exception

    Used to encapsulate exceptions generated during rewrite execution,
    containing additional context information.
    """

    def __init__(self, message: str, original_exception: Exception, rewrite_key: str = None):
        """
        Initialize exception

        Args:
            message: Exception message
            original_exception: Original exception
            rewrite_key: Identifier of the rewrite
        """
        super().__init__(message)
        self.original_exception = original_exception
        self.rewrite_key = rewrite_key
        self.timestamp = datetime.now()

    def __str__(self):
        return f"{super().__str__()} (rewrite_key={self.rewrite_key}, original={type(self.original_exception).__name__})"


class ExceptionHandler:
    """
    Exception Handler

    Used to isolate exceptions from secondary development code,
    preventing them from affecting the original project's operation.
    """

    @staticmethod
    def safe_execute(
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        rewrite_key: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Safely execute function, catching all exceptions

        Args:
            func: Function to execute
            *args: Positional arguments
            fallback: Fallback function when exception occurs (optional)
            rewrite_key: Identifier of the rewrite (for logging)
            **kwargs: Keyword arguments

        Returns:
            Function execution result, if exception occurs and fallback is provided,
            returns fallback result

        Raises:
            RewriteException: If exception occurs and no fallback is provided
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Record detailed exception information
            exception_info = ExceptionHandler._format_exception_info(e, rewrite_key)
            logger.error(exception_info["message"], exc_info=True)

            if fallback:
                try:
                    return fallback(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback function also failed for rewrite '{rewrite_key}': {fallback_error}",
                        exc_info=True
                    )
                    raise RewriteException(
                        f"Both rewrite and fallback failed",
                        fallback_error,
                        rewrite_key
                    )

            # Wrap exception, providing more context information
            raise RewriteException(
                f"Error executing rewrite '{rewrite_key or func.__name__}'",
                e,
                rewrite_key
            )

    @staticmethod
    def _format_exception_info(exception: Exception, rewrite_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Format exception information

        Args:
            exception: Exception object
            rewrite_key: Identifier of the rewrite

        Returns:
            Dictionary containing exception information
        """
        return {
            "message": f"Error executing rewrite '{rewrite_key or 'unknown'}': {exception}",
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            "rewrite_key": rewrite_key,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def isolate_rewrite_execution(
        func: Callable,
        *args,
        rewrite_key: Optional[str] = None,
        **kwargs
    ) -> Tuple[Any, Optional[Exception]]:
        """
        Isolate execution of rewrite function, return result and exception (if any)

        This method ensures exceptions don't propagate, but are returned as return values.

        Args:
            func: Function to execute
            *args: Positional arguments
            rewrite_key: Identifier of the rewrite
            **kwargs: Keyword arguments

        Returns:
            (result, exception) tuple
            - result: Execution result, None if exception occurred
            - exception: Exception object, None if no exception
        """
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            exception_info = ExceptionHandler._format_exception_info(e, rewrite_key)
            logger.error(exception_info["message"], exc_info=True)
            return None, e

    @staticmethod
    def execute_with_timeout(
        func: Callable,
        timeout: float,
        *args,
        rewrite_key: Optional[str] = None,
        default_result: Any = None,
        **kwargs
    ) -> Any:
        """
        Execute function with timeout

        Args:
            func: Function to execute
            timeout: Timeout in seconds
            *args: Positional arguments
            rewrite_key: Identifier of the rewrite (for logging)
            default_result: Default return value on timeout
            **kwargs: Keyword arguments

        Returns:
            Function execution result, returns default_result if timeout

        Raises:
            TimeoutError: If execution times out (Python built-in exception)
        """
        if timeout <= 0:
            # No timeout, execute directly
            return func(*args, **kwargs)

        result_container: Dict[str, Any] = {"result": None, "exception": None, "done": False}

        def target():
            """Execute function in separate thread"""
            try:
                result_container["result"] = func(*args, **kwargs)
            except Exception as e:
                result_container["exception"] = e
            finally:
                result_container["done"] = True

        # Create and start thread
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

        # Wait for thread to complete or timeout
        thread.join(timeout=timeout)

        if not result_container["done"]:
            # Timeout
            timeout_msg = f"Rewrite '{rewrite_key or func.__name__}' execution timeout after {timeout}s"
            logger.warning(timeout_msg)
            raise TimeoutError(timeout_msg)

        # Check if there's an exception
        if result_container["exception"]:
            exception = result_container["exception"]
            exception_info = ExceptionHandler._format_exception_info(exception, rewrite_key)
            logger.error(exception_info["message"], exc_info=True)
            raise exception

        return result_container["result"]
    
    @staticmethod
    async def execute_with_timeout_async(
        coro: Callable,
        timeout: float,
        *args,
        rewrite_key: Optional[str] = None,
        default_result: Any = None,
        **kwargs
    ) -> Any:
        """
        Execute async function/coroutine with timeout

        Args:
            coro: Coroutine or async function to execute
            timeout: Timeout in seconds
            *args: Positional arguments (if coro is a function)
            rewrite_key: Identifier of the rewrite (for logging)
            default_result: Default return value on timeout
            **kwargs: Keyword arguments (if coro is a function)

        Returns:
            Coroutine execution result, returns default_result if timeout

        Raises:
            TimeoutError: If execution times out (Python built-in exception)
        """
        if timeout <= 0:
            # No timeout, execute directly
            if callable(coro):
                return await coro(*args, **kwargs)
            else:
                return await coro
        
        try:
            if callable(coro):
                return await asyncio.wait_for(coro(*args, **kwargs), timeout=timeout)
            else:
                return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            timeout_msg = f"Rewrite '{rewrite_key or 'unknown'}' execution timeout after {timeout}s"
            logger.warning(timeout_msg)
            raise TimeoutError(timeout_msg)

