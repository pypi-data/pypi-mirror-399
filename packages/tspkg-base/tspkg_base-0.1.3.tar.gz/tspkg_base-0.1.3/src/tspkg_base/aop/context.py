"""
Execution Context Module

Provides the ExecutionContext class for encapsulating the execution environment of original methods.
"""

from typing import Any, Tuple, Dict, Callable, Optional
import inspect


class ExecutionContext:
    """
    Execution Context

    Encapsulates the original method's function, parameters, and execution control,
    provided for rewrite methods to use.
    """

    def __init__(
        self,
        func: Callable,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any]
    ):
        """
        Initialize execution context

        Args:
            func: Original method function
            args: Positional arguments
            kwargs: Keyword arguments
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result: Optional[Any] = None
        self.skip_original: bool = False
        self._original_called: bool = False
        self._exception: Optional[Exception] = None  # Store exceptions during execution

    def call_original(self) -> Any:
        """
        Call the original method

        Returns:
            Return value of the original method

        Raises:
            RuntimeError: If the original method has already been called (prevents duplicate calls)
        """
        if self._original_called:
            raise RuntimeError("Original function has already been called")
        
        self._original_called = True
        
        # Check if the function is async
        if inspect.iscoroutinefunction(self.func):
            # For async functions, return the coroutine
            # The caller should await it
            coro = self.func(*self.args, **self.kwargs)
            return coro
        else:
            # For sync functions, call directly
            self.result = self.func(*self.args, **self.kwargs)
            return self.result
    
    async def call_original_async(self) -> Any:
        """
        Call the original method (async version)
        
        This method should be used when you know the original function is async.

        Returns:
            Return value of the original method

        Raises:
            RuntimeError: If the original method has already been called (prevents duplicate calls)
        """
        if self._original_called:
            raise RuntimeError("Original function has already been called")
        
        self._original_called = True
        
        # Check if the function is async
        if inspect.iscoroutinefunction(self.func):
            # For async functions, await the result
            self.result = await self.func(*self.args, **self.kwargs)
            return self.result
        else:
            # For sync functions, call directly
            self.result = self.func(*self.args, **self.kwargs)
            return self.result

    def is_original_called(self) -> bool:
        """
        Check if the original method has been called

        Returns:
            True if the original method has been called, False otherwise
        """
        return self._original_called

    def get_args(self) -> Tuple[Any, ...]:
        """
        Get positional arguments

        Returns:
            Tuple of positional arguments
        """
        return self.args

    def get_kwargs(self) -> Dict[str, Any]:
        """
        Get keyword arguments

        Returns:
            Dictionary of keyword arguments
        """
        return self.kwargs

    def get_exception(self) -> Optional[Exception]:
        """
        Get exception caught during execution

        Returns:
            Exception object, or None if no exception
        """
        return self._exception

    def set_exception(self, exception: Exception) -> None:
        """
        Set exception

        Args:
            exception: Exception object
        """
        self._exception = exception

    def has_exception(self) -> bool:
        """
        Check if there is an exception

        Returns:
            True if there is an exception, False otherwise
        """
        return self._exception is not None

