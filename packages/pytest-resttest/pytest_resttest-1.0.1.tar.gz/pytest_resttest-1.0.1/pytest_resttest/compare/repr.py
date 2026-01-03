from __future__ import annotations

import os
import re
from collections.abc import Iterable
from io import StringIO
from typing import Any, Literal

from termcolor import RESET
from termcolor import colored as termcolor_colored

from pytest_resttest.lib.yaml import YAML

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

type Colors = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "light_grey",
    "dark_grey",
    "light_red",
    "light_green",
    "light_yellow",
    "light_blue",
    "light_magenta",
    "light_cyan",
]

type Highlights = Literal[
    "on_black",
    "on_red",
    "on_green",
    "on_yellow",
    "on_blue",
    "on_magenta",
    "on_cyan",
    "on_white",
    "on_light_grey",
    "on_dark_grey",
    "on_light_red",
    "on_light_green",
    "on_light_yellow",
    "on_light_blue",
    "on_light_magenta",
    "on_light_cyan",
]

type Attributes = Literal["bold", "dark", "underline", "blink", "reverse", "concealed"]


def colored(
    text: str,
    color: Colors | tuple[int, int, int] | None = None,
    on_color: Highlights | tuple[int, int, int] | None = None,
    attrs: Iterable[Attributes] | None = None,
    *,
    no_color: bool | None = None,
    force_color: bool | None = None,
) -> str:
    """
    Wraps text in color.
    :param text: Text to wrap
    :param color: Color to use
    :param on_color: Highlight color
    :param attrs: Text attributes
    :param no_color: When True, disables color output.
    :param force_color: Forces color output even in non-TTY terminals.
    """

    texts = text.split(RESET)
    out: list[str] = []

    for part in texts:
        out.append(
            termcolor_colored(
                part,
                color,
                on_color,
                attrs,
                no_color=no_color,
                force_color=force_color,
            )
        )

    return "".join(out)


def format_msg(item: str, reason: str, color: Colors | None = None, indent: int = 0) -> str:
    """
    Format item with description.
    """

    reason_fmt = colored(f"[{reason}]", color, attrs=["bold"], force_color=True) if reason else ""
    head, *tail = item.splitlines()

    indent = max(0, indent - len(head)) + 4

    formatted = [
        f"{colored(head, color, force_color=True)} {colored('\u2508' * (indent - 2), 'dark_grey', force_color=True)} {reason_fmt}"
        if reason_fmt
        else colored(head, color, force_color=True),
        *[f"{colored(line, color, force_color=True)}" for line in tail],
    ]

    return "\n".join(formatted)


def expected_error(item: str, reason: str = "", indent: int = 0) -> str:
    """Generate an error message for expected errors."""
    return format_msg(item, reason, "red", indent=indent)


def actual_error(item: str, reason: str = "", indent: int = 0) -> str:
    """Generate an error message for actual errors."""
    return format_msg(item, reason, "green", indent=indent)


def actual_excessive(item: str, reason: str = "", indent: int = 0) -> str:
    """Generate an error message for excessive items (items not present in test) when partial matching is enabled."""
    return format_msg(item, reason, "light_grey", indent=indent)


def stringify_value(value: Any) -> str:
    """Convert a value to a string suitable for comparison output."""

    io = StringIO()
    YAML().dump(value, io)
    out = io.getvalue()
    if out.endswith("\n...\n"):
        out = out[: -len("\n...\n")]

    return out


def unescape(text: str) -> str:
    """Remove all ANSI escape sequences from text."""

    return ansi_escape.sub("", text)


def get_escapes(text: str) -> str:
    """Get all ANSI escape sequences until the last reset."""
    escapes: list[str] = []
    for match in ansi_escape.finditer(text):
        escapes.append(match.group(0))
        if match.group(0) == RESET:
            escapes.clear()

    return "".join(escapes)


def _format_line_with_padding(line: str, width: int) -> str:
    """Add padding to a line of text for boxed output."""

    line_length = len(unescape(line))
    line_padding = max(width - line_length - 4, 0)
    return f"\u2502  {line}{RESET}{' ' * line_padding}\u2502"


def boxed(
    text: str,
    header: str | None = None,
    color: Colors | None = None,
    attrs: Iterable[Attributes] | None = None,
    width: int | None = None,
) -> str:
    """Draws a box around content with an optional header."""

    # pylint: disable=too-many-locals

    out: list[str] = []
    lines = text.splitlines()

    if not width:
        try:
            term_width, _ = os.get_terminal_size()
        except OSError:
            term_width = 120

        width = (max(0, len(unescape(header)), *[len(unescape(line)) for line in lines])) + 5

        if term_width:
            width = min(width, term_width - 1)

    header_padding = max(width - len(unescape(header)) - 5, 0)

    out.append(f"\u250c\u2500 {colored(header, color, attrs=attrs, force_color=True)} {'\u2500' * header_padding}\u2510")

    for line in lines:
        line_length = len(unescape(line))
        max_line_width = width - 5

        if line_length > max_line_width:
            # Need to split line into multiple...
            words = line.split(" ")
            current_line = ""
            is_first_line = True

            while words:
                if (
                    len(unescape(current_line)) + len(unescape(words[0])) + 3 <= max_line_width
                    or len(unescape(current_line).strip().lstrip("\u2026")) == 0
                ):
                    current_line += words.pop(0) + " "
                else:
                    current_color = get_escapes(current_line)
                    current_line = current_line.rstrip()  # Remove trailing space

                    # There are still words left to be printed, append line feed.
                    if words:
                        current_line_length = len(unescape(current_line))
                        outdent = f"{' ' * (max_line_width - current_line_length - 1)}\u21a9"
                        current_line += f"{RESET}{colored(outdent, 'light_grey', force_color=True)} "

                    out.append(_format_line_with_padding(current_line, width))

                    if is_first_line:
                        is_first_line = False
                        max_line_width -= 2

                    current_line = f"{colored('\u2026 ', 'light_grey', force_color=True)}{current_color}"

            # Write remaining line
            if current_line:
                out.append(_format_line_with_padding(current_line, width))
        else:
            out.append(_format_line_with_padding(line, width))

    out.append(f"\u2514{'\u2500' * (width - 2)}\u2518")

    return "\n".join(out)
