import textwrap
from typing import Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel


class AsciiArtCombiner:
    """
    A utility for combining ASCII art with support for rich text formatting.

    This class provides methods to combine two ASCII art pieces side by side
    with customizable vertical alignment and spacing.
    """

    class Config(BaseModel):
        """Configuration options for combining ASCII art"""

        vertical_offset: int = Field(
            default=0, description="Line number where the right graphic starts relative to the left"
        )
        horizontal_spacing: int = Field(default=2, description="Number of spaces between the two graphics")

    @staticmethod
    def combine(left: str, right: str, config: Optional[Config] = None) -> str:
        """
        Combine two ASCII art pieces side by side.

        Args:
            left: The ASCII art to place on the left
            right: The ASCII art to place on the right
            config: Configuration options for the combination

        Returns:
            A string containing the combined ASCII art
        """
        if config is None:
            config = AsciiArtCombiner.Config()

        # Split both graphics into lines
        left_lines = left.strip("\n").split("\n")
        right_lines = right.strip("\n").split("\n")

        # Adjust for vertical offset
        offset = config.vertical_offset
        if offset < 0:
            # If offset is negative, pad the left graphic at the top
            left_lines = [""] * abs(offset) + left_lines
            offset = 0

        # Calculate dimensions
        max_height = max(len(left_lines), len(right_lines) + offset)
        left_width = max(len(line) for line in left_lines) if left_lines else 0
        spacing = " " * config.horizontal_spacing

        # Combine the lines
        combined_lines = []
        for i in range(max_height):
            # Get the left line, or empty string if beyond the graphic
            left_line = left_lines[i] if i < len(left_lines) else ""

            # Pad the left line to ensure proper alignment
            left_padded = left_line.ljust(left_width)

            # Get the right line, accounting for vertical offset
            right_idx = i - offset
            right_line = right_lines[right_idx] if 0 <= right_idx < len(right_lines) else ""

            # Combine the lines with spacing
            combined_lines.append(f"{left_padded}{spacing}{right_line}")

        return "\n".join(combined_lines)


console = Console()


def display_logo(version: str) -> None:
    """
    Display the ragbits logo with a rabbit face in ASCII art.
    """
    rabbit_face = textwrap.dedent(
        """
        [magenta bold]  __     __
        [magenta bold] /_/|   |\\_\\
        [magenta bold]  |U|___|U|
        [magenta bold]  |       |
        [magenta bold]  | ,   , |
        [magenta bold] (  = Y =  )
        [magenta bold]  |   `   |
        [magenta bold] /|       |\\
        [magenta bold] \\| |   | |/
        [magenta bold](_|_|___|_|_)
        [magenta bold]  '"'   '"'
        """
    )
    ragbits_title = textwrap.dedent(
        f"""
        [cyan bold]▗▄▄▖  ▗▄▖  ▗▄▄▖▗▄▄▖ ▗▄▄▄▖▗▄▄▄▖▗▄▄▖
        [cyan bold]▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌ ▐▌  █    █ ▐▌
        [cyan bold]▐▛▀▚▖▐▛▀▜▌▐▌▝▜▌▐▛▀▚▖  █    █  ▝▀▚▖
        [cyan bold]▐▌ ▐▌▐▌ ▐▌▝▚▄▞▘▐▙▄▞▘▗▄█▄▖  █ ▗▄▄▞▘

        [cyan bold]Current version: [magenta bold]{version}[/magenta bold]
        [cyan bold]Docs: [magenta bold underline]https://ragbits.deepsense.ai[/magenta bold underline]
        """
    )
    combined = AsciiArtCombiner.combine(
        left=rabbit_face,
        right=ragbits_title,
        config=AsciiArtCombiner.Config(vertical_offset=2),
    )
    logo_panel = Panel.fit(
        combined,
        border_style="cyan",
        padding=(0, 1),
    )
    console.print(logo_panel)
