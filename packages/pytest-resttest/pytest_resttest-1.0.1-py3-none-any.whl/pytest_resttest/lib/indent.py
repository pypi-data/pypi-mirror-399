from typing import overload


@overload
def indent(text: str, prefix: str = "    ") -> str: ...


@overload
def indent(text: list[str], prefix: str = "    ") -> list[str]: ...


def indent(text: str | list[str], prefix: str = "    ") -> str | list[str]:
    """
    Indent each line of the given text with the specified prefix.

    Args:
        text (str): The text to indent.
        prefix (str): The string to use for indentation.

    Returns:
        str: The indented text.
    """
    if isinstance(text, list):
        return [indent(line, prefix) for line in text]

    return "\n".join(prefix + line for line in text.splitlines())
