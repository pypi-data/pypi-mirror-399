from enum import Enum

from fastapi_helper.config import settings


class Roles(str, Enum):
    """
    Docstring для Roles

    Defines the available system roles for the AI assistant.
    The value used in the API schema (and Swagger UI) is the short identifier (e.g., 'default').
    The long description is stored in the 'description' attribute.
    """
    DEFAULT = "Default"
    CODER = "Coder"
    TEACHER = "Teacher"


class Models(str, Enum):
    """
Models enumeration.

This class is used to list the supported AI models.

It is utilized in the /v1/create/chat endpoint to ensure
type safety and ease of use. Instead of manual string entry,
this class provides a predefined selection for better validation
and development consistency.
"""

    MODEL_GPT_4 = settings.gpt_4


class AppColor(str, Enum):
    """
AppColor enumeration.

This class defines the color palette used for console logging and
terminal output formatting.
"""
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


ROLE_PROMPTS: dict[Roles, str] = {
    Roles.TEACHER: (
        "Your role: Teacher.\n\n"
        "You are an experienced teacher.\n"
        "Explain the material in a simple and understandable way.\n"
        "Provide examples and analogies from real life.\n"
        "Adjust the difficulty according to the student's level.\n"
        "If the student does not understand, explain in other words.\n"
        "Answer in the same language as the user query."
    ),

    Roles.CODER: (
        "Your role: Programmer.\n\n"
        "You are a professional programmer.\n"
        "Write clean, readable, and maintainable code.\n"
        "First think about logic and structure, then syntax.\n"
        "If there are multiple solutions, explain differences and consequences.\n"
        "Follow best practices and good coding style.\n"
        "If information is missing, mention assumptions.\n"
        "Answer in the same language as the user query."
    ),

    Roles.DEFAULT: (
        "You are a general assistant.\n"
        "Answer clearly, logically, and to the point.\n"
        "If the question is incomplete, indicate what data is missing.\n"
        "Do not overcomplicate your answers.\n"
        "Be polite and neutral.\n"
        "Answer in the same language as the user."
    )
}
