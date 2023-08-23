class Flag:
    def __init__(self, name, value):
        self.name = name
        self.value = _str_to_bool(value)


class Flags(object):
    """group of modules"""

    def __init__(self, flags):
        """
        Args:
            include(list): a list of :class:`Flag` instances
        """
        self._flags = flags

    def __getattr__(self, name):
        # allow getting flags as object attrs
        for item in self._flags:
            if item.name == name:
                return item

    def as_dict(self):
        return {item.name: item.value for item in self._flags}

    @classmethod
    def load_from_dict(cls, data):
        """Create instances of :class:`Flags` from a dictionary

        Args:
            data(dict): dictionary with data of following format

        .. code-block:: json

            {
                "flag_1": "value",
                "flag_2": "value"
            }
        """
        return cls([Flag(name, value) for name, value in data.items()])


def _str_to_bool(value):
    out = value

    if isinstance(value, str):
        if value.lower() in ("true", "yes"):
            out = True
        elif value.lower() in ("false", "no"):
            out = False

    return out
