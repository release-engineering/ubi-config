class Loader(object):
    """Load UBI configuration.

    Don't construct instances of this class directly;
    use the :func:`~ubiconfig.get_loader` function.
    """

    # This is a base class only. See implementations alongside this one
    # under the loaders module.

    def load(self, file_name, version=None):
        """
        Load a single configuration file and return a :class:`UbiConfig` object.

        The given file_name should be a relative path to a YAML file
        in the loader's config source (e.g. relative path to file within a
        git repo or local directory).

        version is an option argument to specify the version of config file to load,
        if it's None, then use default, e.g. ubi7, ubi8
        """
        raise NotImplementedError()

    def load_all(self):
        """Get the list of config files from repo and call load on every file.
        Return a list of :class:`UbiConfig` objects.
        """
        raise NotImplementedError()
