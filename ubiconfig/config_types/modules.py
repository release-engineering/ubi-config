"""This module abstract the 'modules' content type"""


class Module(object):
    """Define a single module"""

    def __init__(self, name, stream, profiles=None):
        self.name = name
        self.stream = str(stream)
        self.profiles = profiles

    def __repr__(self):
        return "<Module: %s>" % self.name


class Modules(object):
    """group of modules"""

    def __init__(self, include):
        """
        Args:
            include(list): a list of :class:`Module` instances
        """
        self.whitelist = include

    def __getitem__(self, index):
        return self.whitelist[index]

    @classmethod
    def load_from_dict(cls, data):
        """Create instances of :class:`Modules` from a dictionary

        Args:
            data(dict): dictionary with data of following format

        .. code-block:: json

            {"include": [
                    {
                        "name": "<module_name>",
                        "stream": "<module_stream>",
                        "profiles": "<module_profiles>"
                    }
                ]
            }
        """
        include = []

        for item in data.get("include", []):
            module = Module(**item)
            include.append(module)

        return cls(include)
