"""
Base classes for template configuration.
"""
from typing import List, Dict, Union, Optional, Literal, Any


class Question:
    """Base class for template questions"""
    def __init__(
        self,
        name: str,
        message: str,
        default: Optional[Any] = None
    ):
        self.name = name
        self.message = message
        self.default = default
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "default": self.default,
            "type": self.question_type
        }
        
    def prompt(self) -> Any:
        """Base method to prompt for and return an answer"""
        raise NotImplementedError("Subclasses must implement prompt()")
        
class TextQuestion(Question):
    """Text input question"""
    question_type: str = "text"
    
    def prompt(self) -> str:
        from inquirer.shortcuts import text
        return text(self.message, default=self.default)
        
class ListQuestion(Question):
    """List selection question"""
    question_type: str = "list"
    
    def __init__(
        self,
        name: str,
        message: str,
        choices: List[str],
        default: Optional[str] = None
    ):
        super().__init__(name, message, default)
        self.choices = choices
        
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["choices"] = self.choices
        return result
        
    def prompt(self) -> str:
        from inquirer.shortcuts import list_input
        return list_input(self.message, choices=self.choices, default=self.default)
        
class ConfirmQuestion(Question):
    """Yes/No confirmation question"""
    question_type: str = "confirm"
    
    def prompt(self) -> bool:
        from inquirer.shortcuts import confirm
        return confirm(self.message, default=self.default)


class TemplateConfig:
    """Base class for template configuration"""
    name: str = "Base Template"
    description: str = "Base template description"
    
    questions: List[Question] = []
    
    @property
    def questions_dict(self) -> List[Dict[str, Any]]:
        """Get questions as a list of dictionaries"""
        return [q.to_dict() for q in self.questions]
    
    def build_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
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