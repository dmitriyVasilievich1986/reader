"""Base command interface for implementing the Command pattern."""

__all__ = ("BaseCommand",)

from abc import ABC, abstractmethod
from typing import Any


class BaseCommand(ABC):
    """Abstract base class for command pattern implementation.

    This class defines the interface for all command objects in the application.
    Commands encapsulate business logic operations that can be validated before
    execution, providing a consistent way to handle operations with pre-conditions.

    All concrete command classes must implement both the validate and execute methods.
    The typical usage pattern is:
    1. Validate the command's preconditions
    2. Execute the command's business logic

    Example:
        >>> class CreateUserCommand(BaseCommand):
        ...     def __init__(self, username: str, email: str):
        ...         self.username = username
        ...         self.email = email
        ...
        ...     def validate(self) -> None:
        ...         if not self.email or '@' not in self.email:
        ...             raise ValueError("Invalid email")
        ...
        ...     def execute(self) -> None:
        ...         # Create user logic here
        ...         pass

    """

    @abstractmethod
    async def initialize(self, **_: Any) -> None:
        """Initialize the command with the given arguments.

        Args:
            **_: Additional keyword arguments for the command.

        """
        pass

    @abstractmethod
    async def execute(self) -> None:
        """Execute the command's business logic.

        This method contains the main operation that the command performs.
        It should only be called after validate() has been called and passed
        successfully.

        Raises:
            Implementation-specific exceptions based on the command's logic

        """
        pass

    @abstractmethod
    async def validate(self) -> None:
        """Validate the command's preconditions before execution.

        This method checks that all required data is present and valid before
        the command is executed. It should raise appropriate exceptions if
        validation fails.

        Raises:
            ValueError: If any validation constraint is not met
            Implementation-specific exceptions based on validation logic

        """
        pass
