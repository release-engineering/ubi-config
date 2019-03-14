ubi-config
==========

A library for loading UBI configuration

.. contents::
  :local:

Quick Start
-----------

Install ubi-config from PyPI:

::

    pip install ubi-config


If you want to load UBI configuration from default repo, set the default url
in your environment:

::

    export DEFAULT_UBI_REPO='https://some/url/'

In your python code, simply call the function ``get_loader`` without passing
any argument and call ``load`` on the returned object with the configuration
file name. No matter which branch is the config file in, it will load it
for you.

.. code-block:: python

    from ubiconfig import get_loader

    default_loader = get_loader()
    config = default_loader.load("ubi7_config_file")

    # the returned config is an UbiConfig instance, wraps all types of UBI configuration
    modules = config.modules
    module_name = modules[0].name
    print(module_name)

    # the returned Load object can be reused to load other configuration file in the
    # same repo
    config = default_loader.load("ubi8_config_file")
    content_sets = config.content_sets

More Use Cases
--------------

Except the above usage, there are some other use cases:

1. Load all configuration files from a repo by ``load_all``:

.. code-block:: python

    from ubiconfig import get_loader
    loader = get_loader()
    configs = loader.load_all()
    # returns a list of UbiConfig objects

2. Load configuration files from a local repo by setting ``local`` to ``True``:

.. code-block:: python

    from ubiconfig import get_loader

    local_loader = get_loader(local=True)
    config = local_loader.load("full/path/to/local_ubi7_config")

3. If there's a local repo including several configuration files, you can also
set the repo path by passing ``local_repo`` to ``get_loader``:

.. code-block:: python

    from ubiconfig import get_loader

    local_loader = get_loader(local=True, local_repo='repo/path')
    config = local_loader.load('local_ubi7_config')
    # or load all config files
    configs = local_loader.load_all()
    # if there's sub directories include configuration files,
    # user can set ``recursive`` to True to load all of them
    configs = local_loader.load_all(recursive=True)

A single loader can be used to load any number of files.

API Reference
-------------

.. currentmodule:: ubiconfig
.. function:: get_loader

    Get a Loader instance which is used to load configuration.

    The default config file source is ``${DEFAULT_UBI_REPO}/configfile.yaml``;
    this requires the ``DEFAULT_UBI_REPO`` environment variable to be set.
    In this case, call ``get_loader`` with no additional arguments, as in
    example:

    .. code-block:: python

      # use default config source
      >>> loader = get_loader()
      >>> config_ubi7 = loader.load('ubi7')
      >>> config_ubi7.content_sets.rpm.input
      # loader can be used repeatedly
      >>> config_ubi8 = loader.load('ubi8')

    Or if ``local`` is set, then user can pass the local_repo address to
    Loader or send full path to ``loader.load()``, for example:

    .. code-block:: python

      # now use local file
      >>> loader = get_loader(local=True)
      >>> config = loader.load('full/path/to/configfile')

      # can pass local repo address as well
      >>> loader = get_loader(local=True, local_repo='some/repo/path')
      >>> config = loader.load('ubi7')
      # can be reused
      >>> config_ubi8 = loader.load('ubi8')

    If the default UBI url is not defined and local is not set, an error will
    be raised.

.. autoclass:: UbiConfig

.. autoclass:: Loader
    :members: load, load_all
