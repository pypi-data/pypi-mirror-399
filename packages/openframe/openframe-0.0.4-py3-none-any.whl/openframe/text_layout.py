from typing import List
from PIL import ImageFont

from openframe.util import WrapMode


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    mode: WrapMode = WrapMode.AUTO,
) -> str:
    """Wrap text into multiple lines based on a max width.

    Args:
        text: Source text that may contain line breaks.
        font: Loaded font used for measuring rendered width.
        max_width: Maximum width allowed per line.
        mode: Wrapping behavior selector.

    Returns:
        str: Wrapped text with line breaks inserted.
    """

    paragraphs = text.splitlines()
    lines: List[str] = []

    for paragraph in paragraphs:
        if paragraph == "":
            lines.append("")
            continue

        active_mode = mode
        if mode == WrapMode.AUTO:
            active_mode = WrapMode.WORD if " " in paragraph else WrapMode.CHAR

        if active_mode == WrapMode.CHAR:
            current = ""
            for ch in paragraph:
                candidate = f"{current}{ch}"
                if font.getlength(candidate) <= max_width or current == "":
                    current = candidate
                else:
                    lines.append(current)
                    current = ch

            if current != "":
                lines.append(current)
            continue

        words = paragraph.split(" ")
        current = ""
        for word in words:
            candidate = word if current == "" else f"{current} {word}"
            if font.getlength(candidate) <= max_width or current == "":
                current = candidate
            else:
                lines.append(current)
                current = word

        if current != "":
            lines.append(current)

    return "\n".join(lines)
