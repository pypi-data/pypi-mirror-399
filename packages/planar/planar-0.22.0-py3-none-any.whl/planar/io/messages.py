"""Message helpers for Planar IO display APIs."""

from pydantic import BaseModel

from planar.workflows.contrib import message

from ._base import logger


class IOMessage(BaseModel):
    planar_type: str


class MarkdownMessage(IOMessage):
    """Structured payload for IO markdown display."""

    planar_type: str = "io.display.markdown"
    markdown: str


class IODisplay:
    async def markdown(self, markdown_text: str) -> None:
        await message(MarkdownMessage(markdown=markdown_text))
        logger.debug("io markdown message emitted")


__all__ = ["IOMessage", "MarkdownMessage", "IODisplay"]
