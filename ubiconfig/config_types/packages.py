"""This module abstract the 'packages' content type"""


class Package(object):
    def __init__(self, package, arches):
        self.package = package
        if '.' in package:
            name, arch = package.rsplit('.', 1)
            if arch in arches or arch == '*':
                self.name, self.arch = name, arch
        if not hasattr(self, 'name'):
            self.name = package
            self.arch = None

    def __repr__(self):
        return "<Package: %s>" % self.package


class IncludePackage(Package):

    def __init__(self, package, arches):
        super(IncludePackage, self).__init__(package, arches)
        if '*' in self.name:
            raise ValueError("<name>*.<arch> is not supported in whitelist")


class ExcludePackage(Package):
    pass


class Packages(object):

    def __init__(self, include, exclude, arches):
        self.whitelist, self.blacklist = [], []
        for package in include:
            self.whitelist.append(IncludePackage(package, arches))
        for package in exclude:
            self.blacklist.append(ExcludePackage(package, arches))
