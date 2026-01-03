"""IO-enabled agent that exposes workflow IO tools to language models."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

from planar.ai.agent import Agent
from planar.io import IO

IO_AGENT_TOOL_PROMPT = """You can interact with the human operator via dedicated IO tools:
- use `display_markdown(message)` to show formatted content in the UI.
- use `request_text_input(label, help_text=None, placeholder=None)` to ask the operator for text.
- use `request_confirmation(short_title, prompt, confirm_label="Confirm", cancel_label="Cancel")` when you need a yes/no answer.
Prefer showing context with markdown and ask concise, clear questions when requesting input."""


async def display_markdown(message: str) -> str:
    """Render markdown for the human operator."""
    await IO.display.markdown(message)
    return "Displayed markdown to the operator."


async def request_text_input(
    label: str,
    help_text: Optional[str] = None,
    placeholder: Optional[str] = None,
) -> str:
    """Prompt the operator for textual input."""
    return await IO.input.text(
        label,
        help_text=help_text,
        placeholder=placeholder,
    )


async def request_confirmation(
    short_title: str,
    prompt: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
) -> bool:
    """Ask the operator to confirm or decline an action."""
    return await IO.input.boolean(
        short_title,
        help_text=f"{prompt}. Confirm with '{confirm_label}' or cancel with '{cancel_label}'.",
        default=False,
    )


_DEFAULT_IO_TOOLS: tuple[Callable[..., Any], ...] = (
    display_markdown,
    request_text_input,
    request_confirmation,
)


TInput = TypeVar("TInput", bound=Any)
TOutput = TypeVar("TOutput", bound=Any)
TDeps = TypeVar("TDeps", bound=Any)


@dataclass
class IOAgent(Agent[TInput, TOutput, TDeps]):
    """Agent variant that comes pre-wired with IO display/input tools."""

    def __post_init__(self) -> None:
        super().__post_init__()
        existing = {tool.__name__ for tool in self.tools}
        for tool in _DEFAULT_IO_TOOLS:
            if tool.__name__ not in existing:
                self.tools.append(tool)
        if IO_AGENT_TOOL_PROMPT not in self.system_prompt:
            if self.system_prompt:
                self.system_prompt = f"{IO_AGENT_TOOL_PROMPT}\n\n{self.system_prompt}"
            else:
                self.system_prompt = IO_AGENT_TOOL_PROMPT
