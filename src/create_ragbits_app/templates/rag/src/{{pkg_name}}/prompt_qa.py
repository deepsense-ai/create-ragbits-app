from pydantic import BaseModel
from ragbits.core.prompt import Prompt


class QAPromptInput(BaseModel):
    """Input for question answering prompt."""

    question: str
    contexts: list[str]


class QAPrompt(Prompt[QAPromptInput, str]):
    """Prompt for question answering."""

    system_prompt = """
    Your task is to answer user questions based on context.
    If the question is not related to the context, say that the question is not related.

    <context>
    {% for context in contexts %}
    {{context}}
    {% endfor %}
    </context>
    """

    user_prompt = "{{ question }}"
