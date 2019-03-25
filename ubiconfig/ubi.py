import os
import logging

from six.moves.urllib.parse import urlparse

from ._impl.loaders import LocalLoader, GitlabLoader


DEFAULT_UBI_REPO = os.getenv("DEFAULT_UBI_REPO", "")

LOG = logging.getLogger('ubiconfig')


class LoaderError(RuntimeError):
    pass


def get_loader(source=None):
    """Get a Loader instance which is used to load configurations.

    ``source`` should be provided as one of the following:

        URL
            A URL of a remote git repo containing UBI config files.
            Currently, only Gitlab is supported.

        local path
            A path to a local directory containing UBI config files.

        :any:`None`
            If none/omitted, the value of the ``DEFAULT_UBI_REPO``
            environment variable is used. If this is unset, an
            exception is raised.

    After the loader is constructed, it can be used to load config files
    when given relative paths to config files.

    .. code-block:: python

        # use default config source
        >>> loader = get_loader()
        >>> config_ubi7 = loader.load('ubi7.yaml')
        >>> config_ubi7.content_sets.rpm.input
        # loader can be used repeatedly
        >>> config_ubi8 = loader.load('ubi8.yaml')

        # or use a local directory
        >>> loader = get_loader('/my/config/dir)
        >>> config = loader.load('path/to/configfile.yaml')
    """
    if not source:
        source = DEFAULT_UBI_REPO

    if not source:
        msg = 'Please either set a source or define DEFAULT_UBI_REPO in your environment'
        raise LoaderError(msg)

    parsed = urlparse(source)
    if parsed.netloc:
        # It's a URL, use the gitlab loader
        return GitlabLoader(source)

    # It should be a local path
    if not os.path.isdir(source):
        raise LoaderError("'%s' is not an existing directory" % source)

    return LocalLoader(source)
