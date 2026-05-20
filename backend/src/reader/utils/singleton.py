"""Thread-safe singleton metaclass for one-instance-per-class semantics."""

__all__ = ("Singleton",)

from threading import Lock
from typing import Any, ClassVar


class Singleton[InstanceType: Any](type):
    """Metaclass that ensures at most one instance exists per concrete class.

    The first call to a class constructor creates and caches the instance;
    subsequent calls return the same object. Access is synchronized with a
    lock so instance creation is safe across threads.
    """

    _instances: ClassVar[dict[type, InstanceType]] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> InstanceType:
        """Return the singleton instance for ``cls``, creating it if needed.

        Args:
            *args (Any): Positional arguments forwarded to the class
                constructor on first instantiation.
            **kwargs (Any): Keyword arguments forwarded to the class
                constructor on first instantiation.

        Returns:
            InstanceType: The cached singleton instance for ``cls``.

        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
