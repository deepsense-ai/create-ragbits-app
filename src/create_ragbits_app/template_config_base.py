"""
Base classes for template configuration.
"""

import pathlib
from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T", str, bool)


class Question(ABC):
    """Base class for template questions"""

    @property
    @abstractmethod
    def question_type(self) -> str:
        """Type of the question"""
        pass

    def __init__(self, name: str, message: str, default: str | bool | list[str] | None = None):
        self.name = name
        self.message = message
        self.default = default

    def to_dict(self) -> dict[str, Any]:
        """Convert question properties to a dictionary representation."""
        return {"name": self.name, "message": self.message, "default": self.default, "type": self.question_type}

    def prompt(self) -> str | bool | list[str]:
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

    def __init__(self, name: str, message: str, choices: list[str], default: str | None = None):
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


class MultiSelectQuestion(Question):
    """Multi-select checkbox question"""

    question_type: str = "checkbox"

    def __init__(
        self,
        name: str,
        message: str,
        choices: list[str | dict[str, str]],
        default: list[str] | None = None,
    ):
        super().__init__(name, message, default)
        self.choices = choices
        self._choice_map = self._build_choice_map()

    def _build_choice_map(self) -> dict[str, str]:
        """Build a mapping from display names to values."""
        choice_map = {}
        for choice in self.choices:
            if isinstance(choice, dict):
                display_name = choice["display_name"]
                value = choice["value"]
                choice_map[display_name] = value
            else:
                # If it's just a string, use it as both display name and value
                choice_map[choice] = choice
        return choice_map

    def _get_display_choices(self) -> list[str]:
        """Get the list of display names for the choices."""
        display_choices = []
        for choice in self.choices:
            if isinstance(choice, dict):
                display_choices.append(choice["display_name"])
            else:
                display_choices.append(choice)
        return display_choices

    def _get_default_display_names(self) -> list[str]:
        """Convert default values to display names."""
        if not self.default or not isinstance(self.default, list):
            return []

        # Reverse mapping: value -> display_name
        value_to_display = {v: k for k, v in self._choice_map.items()}
        return [value_to_display.get(value, value) for value in self.default]

    def to_dict(self) -> dict[str, Any]:
        """Convert question properties to a dictionary including choices."""
        result = super().to_dict()
        result["choices"] = self._get_display_choices()
        return result

    def prompt(self) -> list[str]:
        """Display a multi-select checkbox prompt and return the user's selections as values."""
        from inquirer.shortcuts import checkbox

        display_choices = self._get_display_choices()
        default_display_names = self._get_default_display_names()

        selected_display_names = checkbox(self.message, choices=display_choices, default=default_display_names)

        # Convert selected display names back to values
        return [self._choice_map[display_name] for display_name in selected_display_names]


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

    def should_include_file(self, file_path: pathlib.Path, context: dict[str, Any]) -> bool:  # noqa: PLR6301
        """
        Determine whether a file should be included in the generated project.
        Override this method in template configs to add custom file filtering logic.

        Args:
            file_path: Path object representing the file relative to the template root
            context: Dictionary containing the current context including answers
                    from questions and additional context

        Returns:
            Boolean indicating whether the file should be included
        """
        return True

    def get_conditional_directories(self) -> dict[str, str]:  # noqa: PLR6301
        """
        Define directories that should be conditionally included based on context variables.

        Returns:
            Dictionary mapping directory paths to context variable names that control inclusion.
            For example: {"observability": "observability"} means the observability/ directory
            will only be included if context["observability"] is truthy.
        """
        return {}
