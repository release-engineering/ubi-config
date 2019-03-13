ubi-config
==========

A tool for loading UBI configurations

.. toctree::
   :maxdepth: 2
   :caption: Contents:

- `Source <https://github.com/release-engineering/ubi-config>`_
- `Documentation <https://release-engineering.github.io/ubi-config/>`_
- `PyPI <https://pypi.org/project/ubi-config>`_

Quick Start
-----------

Install the ubi-config from PyPI:

::

    pip install ubi-config


If you want to load UBI configuration from default repo, set the default url
in your environment:

::

    export DEFAULT_UBI_REPO='https://some/url/'

In your python code, simply call the function ``get_loader`` without passing any
argument and call ``load`` on the returned object with the configuration file name
No matter which branch is the config file in, it will load it for you.

.. code-block:: python

    from ubiconfig import get_loader

    default_loader = get_loader()
    config = default_loader.load("ubi7_config_file")

    # the return config is an UbiConfig instance, wraps all types of UBI configurations
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

2. Load configuration files from a local repo by setting ``local`` to ``True``

.. code-block:: python

    from ubiconfig import get_loader

    local_loader = get_loader(local=True)
    config = local_loader.load("full/path/to/local_ubi7_config")

3. If there's a local repo inlcudes several configuration files, you can also set the repo
path by passing ``local_repo`` to ``get_loader``

.. code-block:: python

    from ubiconfig import get_loader

    local_loader = get_loader(use=True, local_repo='repo/path')
    config = local_loader.load('local_ubi7_config')
    # or load all config files
    configs = local_loader.load_all()
    # if there's sub directories include configuration files,
    # user can set ``recursive`` to True to load all of them
    configs = local_loader.load_all(recursive=True)

You can always reuse the loader

API Reference
-------------
.. currentmodule:: ubiconfig
.. function:: get_loader

    Get a Loader instance which is used to load configurations.

    The default config file source is as ``DEFAULT_UBI_URL/configfile.yaml``,
    when ``local`` is not set, it will check if the ``DEFAULT_UBI_URL`` is set
    or not, then creates a requests session and pass it to ``Loader``.

    Or if ``local`` is set, then user can pass the local_repo address to
    Loader or send full path to ``loader.load()``, for example:

    .. code-block:: python

      # use default config source
      >>> loader = get_loader()
      >>> config_ubi7 = loader.load('ubi7')
      >>> config)ubi7.content_sets.rpm.input
      # loader can be used repeatedly
      >>> config_ubi8 = loader.load('ubi8')

      # now use local file
      >>> loader = get_loader(use_local=True)
      >>> config = loader.load('full/path/to/configfile')

      # can pass local repo address as well
      >>> loader = get_loader(use_local=True, local_repo='some/repo/path')
      >>> config = loader.load('ubi7')
      # can be reused
      >>> config_ubi8 = loader.load('ubi8')

    If the default ubi url is not defined and use_local not set, error will
    be raised.

.. autoclass:: UbiConfig

.. autoclass:: Loader
    :members: load, load_all