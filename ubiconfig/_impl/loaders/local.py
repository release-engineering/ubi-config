import logging
import os

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
        self._current_version = os.path.basename(self._path.rstrip("/"))
        # set the current version to the last part of path, e.g. /configs/ubi7,
        # the current version is ubi7

    def load(self, file_name):
        """Load a config file from local.

        Args:
            file_name (str): file name of the config file.
        """
        if not self._isroot:
            file_path = os.path.join(self._path, file_name)
        else:
            file_path = file_name

        LOG.info("Loading configuration file locally: %s", file_path)

        with open(file_path, "r") as f:
            config_dict = yaml.load(f, Loader=yaml.BaseLoader)
        # validate input data
        validate_config(config_dict)

        return UbiConfig.load_from_dict(
            config_dict, file_name, self._current_version[3:]
        )

    def load_all(self):
        """Load all config file from a local directory and all its subdirectories"""

        ubi_configs = []
        self._isroot = True

        ver_files_map = self._get_local_files_mapping()
        current_version = self._current_version

        for version, files in ver_files_map.items():
            self._current_version = version
            for f in files:
                LOG.debug("Now loading %s", f)
                try:
                    ubi_configs.append(self.load(f))
                except yaml.YAMLError:
                    LOG.error(
                        "%s FAILED loading because of Syntax error, Skip for now", f
                    )
                    continue
                except ValidationError as e:
                    LOG.error("%s FAILED schema validation:\n%s\nSkip for now", f, e)
                    continue

        self._isroot = False
        self._current_version = current_version
        # restore _isroot and _current_version so the loader can be used again.

        return ubi_configs

    def _get_local_files_mapping(self):
        """Get the config file list from local."""
        LOG.info("Getting the local config file list")
        ver_files_map = {}
        for root, _, files in os.walk(self._path):
            conf_files = [
                os.path.join(root, f) for f in files if f.endswith((".yaml", ".yml"))
            ]
            if conf_files:
                # if there's yaml files, then it must under some version directory
                version = os.path.basename(root)
                ver_files_map[version] = conf_files
                # the result map is as {'version': ['file1', 'file2', ..]}

        return ver_files_map
