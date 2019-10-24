import logging
import os
import re

import yaml
from jsonschema.exceptions import ValidationError

from ubiconfig.utils.config_validation import validate_config
from ubiconfig.config_types import UbiConfig


LOG = logging.getLogger("ubiconfig")


class LocalLoader(object):
    """Load configuration from a local directory tree."""

    def __init__(self, path):
        """
        Args:
            path (str): a local path to config files
        """

        self._path = path
        self._isroot = False
        # when load_all is called, the path returned includes self._path, no
        # need to join again.
        self._ver_files_map = self._get_local_files_map()
        # a {version: [file]} map

    def load(self, file_name, version=None):
        """Load a config file from local.

        Args:
            file_name (str): path to the config file.

            version(str):
                The version usage here is a little different from the remote loader,
                it's only used to denote the version of config file, but in remote
                loader, it's also used to find the right config.

                If version is None, we should get it from its path.
        """
        if not self._isroot:
            file_path = os.path.join(self._path, file_name)
        else:
            file_path = file_name

        if version is None:
            # get version from path, such as configs/ubi7.1/config.yaml, get
            # ubi7.1.
            version = os.path.basename(os.path.dirname(os.path.abspath(file_path)))

        if not re.search(r"ubi[0-9]\.[0-9]{1,2}$|ubi[0-9]$", version):
            raise ValueError(
                "Expect directories named in format ubi[0-9].([0-9]{1,2})$' or ubi[0-9]$, but got %s"
                % version
            )

        LOG.info("Loading configuration file locally: %s", file_path)

        with open(file_path, "r") as f:
            config_dict = yaml.load(f, Loader=yaml.BaseLoader)
        # validate input data
        validate_config(config_dict)

        return UbiConfig.load_from_dict(config_dict, file_name, version[3:])

    def load_all(self):
        """Load all config file from a local directory and all its subdirectories"""

        ubi_configs = []
        self._isroot = True

        for version, files in self._ver_files_map.items():
            for f in files:
                LOG.debug("Now loading %s", f)
                try:
                    ubi_configs.append(self.load(f, version))
                except yaml.YAMLError:
                    LOG.error(
                        "%s FAILED loading because of Syntax error, Skip for now", f
                    )
                    continue
                except ValidationError as e:
                    LOG.error("%s FAILED schema validation:\n%s\nSkip for now", f, e)
                    continue

        self._isroot = False
        # restore _isroot so the loader can be used again.

        return ubi_configs

    def _get_local_files_map(self):
        """Get the config file list from local."""
        LOG.info("Getting the local config file list")
        ver_files_map = {}
        for root, _, files in os.walk(self._path):
            conf_files = [
                os.path.join(root, f) for f in files if f.endswith((".yaml", ".yml"))
            ]
            if conf_files:
                # if there's yaml files, then it must under some version directory
                version = os.path.basename(os.path.abspath(root))
                ver_files_map.setdefault(version, []).extend(conf_files)
                # the result map is as {'version': ['file1', 'file2', ..]}

        return ver_files_map
