from collections.abc import Sequence
from typing import Any


def format_struct(data: Any, indent: int = 0) -> list[str]:
    """
    Formats data structure for serialization to string. This is used to create human-readable representation of the data.
    :param data: Data to be formatted
    :param indent: Indent for individual rows of the output. You probably don't need to specify this, it's used for recursive
      serialization.
    :return: List of lines containing formatted data.
    """
    lines = []

    if not isinstance(data, (dict, Sequence)) or isinstance(data, (str, bytes)):
        lines.append(f"{' ' * indent}{data!r}")
    elif isinstance(data, dict):
        lines.extend(
            [
                v
                for key, value in data.items()
                for v in (
                    [f"{' ' * indent}{key}: {format_struct(value, 0)[0]}"]
                    if not isinstance(value, (dict, Sequence)) or isinstance(value, (str, bytes))
                    else [f"{' ' * indent}{key}:", *format_struct(value, indent + 2)]
                )
            ]
        )
    else:
        if len(data) == 0:
            lines.append(f"{' ' * indent}[]")

        else:
            lines.extend(
                [
                    v
                    for item in data
                    for v in (
                        [f"{' ' * indent}- {format_struct(item, 0)[0]}"]
                        if not isinstance(item, (dict, Sequence)) or isinstance(item, (str, bytes))
                        else [
                            f"{' ' * indent}- {line.strip()}" if idx == 0 else line
                            for idx, line in enumerate(format_struct(item, indent + 2))
                        ]
                    )
                ]
            )

    return lines
