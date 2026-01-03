"""Dependency injection system for Crimsy."""

from collections.abc import AsyncIterator, Awaitable
from typing import Any, Callable, TypeVar, overload

T = TypeVar("T")


class _DependsClass:
    """Internal class for dependency injection marker."""

    dependency: Callable[..., Any]
    use_cache: bool

    def __init__(self, dependency: Callable[..., Any], use_cache: bool = True) -> None:
        """Initialize dependency marker.

        Args:
            dependency: Callable that provides the dependency
            use_cache: Whether to cache the dependency result (default: True)
        """
        self.dependency = dependency
        self.use_cache = use_cache

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Depends({self.dependency.__name__})"


# Overloads for async iterators (unwrap AsyncIterator[T] to T)
@overload
def Depends(
    dependency: Callable[..., AsyncIterator[T]], use_cache: bool = True
) -> T: ...


# Overloads for async functions returning T (unwrap Awaitable[T] to T)
@overload
def Depends(dependency: Callable[..., Awaitable[T]], use_cache: bool = True) -> T: ...


# Overloads for sync functions returning T
@overload
def Depends(dependency: Callable[..., T], use_cache: bool = True) -> T: ...


def Depends(dependency: Callable[..., Any], use_cache: bool = True) -> Any:
    """Marker for dependency injection.

    Similar to FastAPI's Depends, this function marks a parameter as a dependency
    that should be resolved and injected by the framework.

    The function signature is designed so that type checkers understand that
    Depends(func) returns the same type as func's return type (unwrapping
    Awaitable and AsyncIterator for async functions).

    Example:
        async def get_db() -> Database:
            return Database()

        @router.get("/")
        async def handler(db: Database = Depends(get_db)) -> dict:
            return {"status": "ok"}
    """
    return _DependsClass(dependency, use_cache)
