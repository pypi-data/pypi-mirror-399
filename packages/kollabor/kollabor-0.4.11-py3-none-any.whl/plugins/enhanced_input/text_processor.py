"""Text processing utilities for enhanced input plugin."""

import re
from typing import List


class TextProcessor:
    """Handles text wrapping, truncation, and visual length calculations."""

    def __init__(self, config):
        """Initialize text processor.

        Args:
            config: InputConfig object with plugin configuration.
        """
        self.config = config

    def wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to fit within the specified width.

        Args:
            text: Text to wrap.
            width: Maximum width for each line.

        Returns:
            List of wrapped text lines.
        """
        wrap_text = self.config.wrap_text

        if not wrap_text or not text:
            return [text] if text else [""]

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # Check if adding this word would exceed the width
            test_line = f"{current_line} {word}".strip()
            if len(test_line) <= width:
                current_line = test_line
            else:
                # Start a new line
                if current_line:
                    lines.append(current_line)
                current_line = word

        # Add the last line
        if current_line:
            lines.append(current_line)

        return lines if lines else [""]

    def get_visual_length(self, text: str) -> int:
        """Get the visual length of text, excluding ANSI escape codes.

        Args:
            text: Text that may contain ANSI codes.

        Returns:
            Visual length of the text.
        """
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        clean_text = ansi_escape.sub('', text)
        return len(clean_text)

    def truncate_with_ellipsis(self, text: str, max_width: int) -> str:
        """Truncate text with ellipsis if it exceeds max width.

        Args:
            text: Text to potentially truncate.
            max_width: Maximum allowed width.

        Returns:
            Truncated text with ellipsis if needed.
        """
        visual_length = self.get_visual_length(text)
        if visual_length > max_width:
            # Truncate content but be careful with ANSI codes
            return text[:max_width-3] + "..."
        return text

    def pad_to_width(self, text: str, target_width: int) -> str:
        """Pad text to target width with spaces.

        Args:
            text: Text to pad.
            target_width: Target width.

        Returns:
            Padded text.
        """
        visual_length = self.get_visual_length(text)
        if visual_length < target_width:
            padding_needed = target_width - visual_length
            return text + " " * padding_needed
        return text

    def fit_text_to_width(self, text: str, target_width: int) -> str:
        """Fit text to target width by truncating or padding as needed.

        Args:
            text: Text to fit.
            target_width: Target width.

        Returns:
            Text fitted to target width.
        """
        visual_length = self.get_visual_length(text)

        if visual_length > target_width:
            return self.truncate_with_ellipsis(text, target_width)
        else:
            return self.pad_to_width(text, target_width)