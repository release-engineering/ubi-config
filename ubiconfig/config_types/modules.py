"""This module abstract the 'modules' content type"""


class Module(object):
    """Define a single module"""
    def __init__(self, name, stream, profiles=None):
        self.name = name
        self.stream = str(stream)
        self.profiles = profiles

    def __repr__(self):
        return '<Module: %s>' % self.name


class Modules(object):
    """group of modules"""

    def __init__(self, include):
        """
        Args:
            include(list): a list of Module instances
        """
        self.whitelist = include

    def __getitem__(self, index):
        return self.whitelist[index]

    @classmethod
    def load_from_dict(cls, data):
        """create instances of moudles from a dictionary"""
        include = []

        for item in data.get('include', []):
            module = Module(**item)
            include.append(module)

        return cls(include)
