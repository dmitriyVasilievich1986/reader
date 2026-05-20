"""Base command interface for implementing the Command pattern."""

__all__ = ("BaseCommand",)

from abc import ABC, abstractmethod
from typing import Any


class BaseCommand[ResultType: Any](ABC):
    """Abstract async command with initialize, validate, and execute hooks.

    Subclasses implement the three-step lifecycle: optional setup via
    ``initialize``, precondition checks in ``validate``, then ``execute`` for
    the main work. Call ``validate`` before ``execute`` once prerequisites
    are ready.
    """

    @abstractmethod
    async def initialize(self, **_: Any) -> None:
        """Initialize the command with the given arguments.

        Args:
            **_: Additional keyword arguments for the command.

        """
        pass

    @abstractmethod
    async def execute(self) -> ResultType:
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
