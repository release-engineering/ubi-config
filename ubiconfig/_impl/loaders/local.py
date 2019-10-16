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

        return UbiConfig.load_from_dict(config_dict, file_name)

    def load_all(self):
        """Load all config file from a local directory and all its subdirectories"""

        ubi_configs = []
        self._isroot = True

        file_list = self._get_local_file_list()
        for file in file_list:
            LOG.debug("Now loading %s", file)
            try:
                ubi_configs.append(self.load(file))
            except yaml.YAMLError:
                LOG.error(
                    "%s FAILED loading because of Syntax error, Skip for now", file
                )
                continue
            except ValidationError as e:
                LOG.error("%s FAILED schema validation:\n%s\nSkip for now", file, e)
                continue
        self._isroot = False

        return ubi_configs

    def _get_local_file_list(self):
        """Get the config file list from local."""
        LOG.info("Getting the local config file list")
        file_list = []
        for root, _, files in os.walk(self._path):
            files = [
                os.path.join(root, f) for f in files if f.endswith((".yaml", ".yml"))
            ]
            file_list.extend(files)

        return file_list
