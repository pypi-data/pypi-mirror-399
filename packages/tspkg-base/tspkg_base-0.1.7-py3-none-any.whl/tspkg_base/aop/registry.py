"""
Global Registry

Used to store and manage registration information of rewrite methods.
"""

from typing import Dict, Callable, Optional, List

# Global rewrite registry
# key: str, value: Callable
REWRITE_REGISTRY: Dict[str, Callable] = {}


def register_rewrite(key: str, func: Callable) -> None:
    """
    Register a rewrite method

    Args:
        key: Unique identifier of the rewrite, e.g., "order.create"
        func: Rewrite function that receives ExecutionContext as parameter

    Raises:
        ValueError: If key already exists with a different function
    """
    if key in REWRITE_REGISTRY:
        existing = REWRITE_REGISTRY[key]
        if existing is not func:
            raise ValueError(f"Rewrite key '{key}' already registered with a different function")
    REWRITE_REGISTRY[key] = func


def get_rewrite(key: str) -> Optional[Callable]:
    """
    Get registered rewrite method by key

    Args:
        key: Unique identifier of the rewrite

    Returns:
        Registered rewrite function, or None if not found
    """
    return REWRITE_REGISTRY.get(key)


def unregister_rewrite(key: str) -> bool:
    """
    Unregister a rewrite method

    Args:
        key: Unique identifier of the rewrite

    Returns:
        True if successfully unregistered, False if key doesn't exist
    """
    if key in REWRITE_REGISTRY:
        del REWRITE_REGISTRY[key]
        return True
    return False


def clear_registry() -> None:
    """
    Clear all registered rewrite methods

    Mainly used for testing scenarios
    """
    REWRITE_REGISTRY.clear()


def has_rewrite(key: str) -> bool:
    """
    Check if the specified key is registered

    Args:
        key: Unique identifier of the rewrite

    Returns:
        True if registered, False otherwise
    """
    return key in REWRITE_REGISTRY


def get_all_keys() -> List[str]:
    """
    Get list of all registered keys

    Returns:
        List of all registered keys
    """
    return list(REWRITE_REGISTRY.keys())


def get_registry_size() -> int:
    """
    Get the number of registered items in the registry

    Returns:
        Number of registered items
    """
    return len(REWRITE_REGISTRY)

