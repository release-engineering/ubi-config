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
    config = default_loader.load("ubi7_config_file.yaml")

    # the returned config is an UbiConfig instance, wraps all types of UBI configuration
    modules = config.modules
    module_name = modules[0].name
    print(module_name)

    # the returned Load object can be reused to load other configuration file in the
    # same repo
    config = default_loader.load("ubi8_config_file.yaml")
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


2. Load configuration files from a directory by passing a local path:

.. code-block:: python

    from ubiconfig import get_loader

    local_loader = get_loader("/my/config/dir")
    config = local_loader.load("path/to/local_ubi7_config.yaml")

    # or try load_all with recursive to load all available config files
    configs = local_loader.load_all(recursive=True)


API Reference
-------------
:mod:`ubiconfig`
================
.. currentmodule:: ubiconfig

.. autofunction:: get_loader

.. autoclass:: UbiConfig
    :members: load_from_dict

.. autoclass:: Loader
    :members: load, load_all

:mod:`ubiconfig.config_types.packages`
======================================

.. currentmodule:: ubiconfig.config_types.packages
.. autoclass:: Packages
  :members:

:mod:`ubiconfig.config_types.modules`
=====================================

.. currentmodule:: ubiconfig.config_types.modules
.. autoclass:: Modules
    :members: load_from_dict

.. autoclass:: Module
    :members:


:mod:`ubiconfig.config_types.content_sets`
==========================================

.. currentmodule:: ubiconfig.config_types.content_sets
.. autoclass:: ContentSetsMapping
    :members: load_from_dict

.. autoclass:: Rpm
.. autoclass:: Srpm
.. autoclass:: Debuginfo


.. _yaml_format:

Configuration files format
==========================

Loaded configuration files has to be presented in following format

.. code-block:: yaml

  content_sets:
    rpm:
      output: <output-content-set>
      input: <input-content-set>
    srpm:
      output: <output-content-set>
      input: <input-content-set>
    debuginfo:
      output: <output-content-set>
      input: <input-content-set>
  arches:
   - <arch-for-all-content-sets>
   - <arch-for-all-content-sets>
  packages:
    include:
    - <whitelisted-package-full-name>
    - <whitelisted-package-name-regular-expresion-.*>

    # Blacklist of packages to exclude
    exclude:
    - <whitelisted-package-full-name>
    - <whitelisted-package-name-regular-expresion-.*>
  modules:
    include:
    - name: <module-name>
      stream: <module-stream>

See also :py:meth:`~ubiconfig.Loader.load_all`, :py:meth:`~ubiconfig.Loader.load`, :py:meth:`~ubiconfig.get_loader`

.. _git_repo_format:

Configuration git repository structure
======================================

When git repository as passed as source for config data to :py:meth:`~ubiconfig.Loader.load` or :py:meth:`~ubiconfig.Loader.load_all`
it has to be have following structure:

<branch-x-root-dir>:
 - <configuration-file-1>.yaml
 - <configuration-file-1>.yaml
 - <configuration-file-1>.yaml
 - <configuration-file-1>.yaml

See also: :ref:`yaml_format`

