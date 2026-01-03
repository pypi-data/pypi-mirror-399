from typing import Any

from ruamel import yaml as ruamel

from pytest_resttest.compare.partial import PartialList, Unsorted


class CustomRepresenter(ruamel.RoundTripRepresenter):
    """
    Custom YAML representer that handles undefined types by converting them to strings.
    """

    def represent_undefined(self, data: Any) -> Any:
        """Represent undefined types by converting them to strings."""

        if isinstance(data, int):
            return self.represent_int(str(data))

        if isinstance(data, float):
            return self.represent_float(str(data))

        return self.represent_str(str(data))

    def __init__(
        self,
        default_style: Any = None,
        default_flow_style: Any = None,
        dumper: Any = None,
    ) -> None:
        super().__init__(
            default_style=default_style,
            default_flow_style=default_flow_style,
            dumper=dumper,
        )
        self.add_representer(None, self.__class__.represent_undefined)


class YAML(ruamel.YAML):
    """
    Custom YAML loader and dumper that supports additional types.
    """

    def __init__(self) -> None:
        super().__init__()
        self.Representer = CustomRepresenter
        self.register_class(Unsorted)
        self.register_class(PartialList)
