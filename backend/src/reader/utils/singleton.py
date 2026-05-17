"""Singleton metaclass for thread-safe singleton pattern implementation."""

__all__ = ("Singleton",)

from asyncio import Lock
from typing import ClassVar


class Singleton(type):
    """Thread-safe singleton metaclass.

    This metaclass ensures that only one instance of a class is created,
    regardless of how many times the class is instantiated. The implementation
    is thread-safe using a Lock to prevent race conditions in multi-threaded
    environments.

    Usage:
        class MyClass(metaclass=Singleton):
            pass

        instance1 = MyClass()
        instance2 = MyClass()
        # instance1 is instance2 == True
    """

    _instances: ClassVar[dict] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Create or return the singleton instance of the class.

        On first call, creates a new instance and stores it. Subsequent calls
        return the same stored instance. This method is thread-safe and will
        ensure only one instance is created even in concurrent environments.

        Args:
            *args: Positional arguments passed to the class constructor.
            **kwargs: Keyword arguments passed to the class constructor.

        Returns:
            The singleton instance of the class.

        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
