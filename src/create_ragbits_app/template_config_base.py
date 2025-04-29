"""
Base classes for template configuration.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar

T = TypeVar("T", str, bool)


class Question(ABC):
    """Base class for template questions"""

    @property
    @abstractmethod
    def question_type(self) -> str:
        """Type of the question"""
        pass

    def __init__(self, name: str, message: str, default: Optional[str | bool] = None):
        self.name = name
        self.message = message
        self.default = default

    def to_dict(self) -> dict[str, Any]:
        """Convert question properties to a dictionary representation."""
        return {"name": self.name, "message": self.message, "default": self.default, "type": self.question_type}

    def prompt(self) -> str | bool:
        """Base method to prompt for and return an answer"""
        raise NotImplementedError("Subclasses must implement prompt()")


class TextQuestion(Question):
    """Text input question"""

    question_type: str = "text"

    def prompt(self) -> str:
        """Display a text input prompt and return the user's text response."""
        from inquirer.shortcuts import text

        return text(self.message, default=self.default)


class ListQuestion(Question):
    """List selection question"""

    question_type: str = "list"

    def __init__(self, name: str, message: str, choices: list[str], default: Optional[str] = None):
        super().__init__(name, message, default)
        self.choices = choices

    def to_dict(self) -> dict[str, Any]:
        """Convert question properties to a dictionary including choices."""
        result = super().to_dict()
        result["choices"] = self.choices
        return result

    def prompt(self) -> str:
        """Display a list selection prompt and return the user's selection."""
        from inquirer.shortcuts import list_input

        return list_input(self.message, choices=self.choices, default=self.default)


class ConfirmQuestion(Question):
    """Yes/No confirmation question"""

    question_type: str = "confirm"

    def prompt(self) -> bool:
        """Confirm question prompt"""
        from inquirer.shortcuts import confirm

        return confirm(self.message, default=self.default)


class TemplateConfig:
    """Base class for template configuration"""

    name: str = "Base Template"
    description: str = "Base template description"

    questions: list[Question] = []

    @property
    def questions_dict(self) -> list[dict[str, Any]]:
        """Get questions as a list of dictionaries"""
        return [q.to_dict() for q in self.questions]

    def build_context(self, context: dict[str, Any]) -> dict[str, Any]:  # noqa: PLR6301
        """
        Build additional context based on the answers.
        Override this method in template configs to add custom context.

        Args:
            context: Dictionary containing the current context including answers
                    from questions

        Returns:
            Dictionary containing additional context variables
        """
        return {}
