import logging
import yaml
import requests

from jsonschema.exceptions import ValidationError

from ubiconfig.utils.api.gitlab import RepoApi
from ubiconfig.utils.config_validation import validate_config
from ubiconfig.config_types import UbiConfig

from .base import Loader

LOG = logging.getLogger('ubiconfig')


class GitlabLoader(Loader):
    """Load configuration from a remote repo on gitlab."""
    def __init__(self, url):
        self._url = url
        self._session = requests.Session()
        self._repo_api = RepoApi(self._url.rstrip('/'))
        self._files_branch_map = self._pre_load()

    def load(self, file_name):
        # find the right branch from the mapping
        branch = self._files_branch_map[file_name]

        config_file_url = self._repo_api.get_file_content_api(file_name, branch)
        LOG.info("Loading configuration file from remote: %s", file_name)
        response = self._session.get(config_file_url)
        response.raise_for_status()

        config_dict = yaml.safe_load(response.content)
        # validate input data
        validate_config(config_dict)

        return UbiConfig.load_from_dict(config_dict, file_name)

    def load_all(self, recursive=False):
        ubi_configs = []
        for file in self._files_branch_map:
            LOG.debug("Now loading %s from branch %s", file, self._files_branch_map[file])
            try:
                ubi_configs.append(self.load(file))
            except yaml.YAMLError:
                LOG.error("%s FAILED loading because of Syntax error, Skip for now", file)
                continue
            except ValidationError as e:
                LOG.error("%s FAILED schema validation:\n%s\nSkip for now", file, e)
                continue

        return ubi_configs

    def _pre_load(self):
        """Iterate all branches to get a mapping of {file_path: branch,...}
        """
        files_branch_map = {}
        branches = self._get_branches()
        LOG.info("Loading config files from all branches: %s", branches)
        for branch in branches:
            page = 1
            while True:
                file_list_api = self._repo_api.get_file_list_api(branch=branch,
                                                                 page=page)
                response = self._session.get(file_list_api)
                file_list = [file['path'] for file in response.json()
                             if file['name'].endswith(('.yaml', '.yml'))]
                for file in file_list:
                    files_branch_map[file] = branch
                if page >= int(response.headers.get('X-Total-Pages', 1)):
                    break
                page += 1
        return files_branch_map

    def _get_branches(self):
        """Get all the branches of a given repo"""
        LOG.info("Getting branches of the repo")
        branches_list_api = self._repo_api.get_branch_list_api()
        json_response = self._session.get(branches_list_api).json()
        if not json_response:
            raise RuntimeError('Please check %s is in right format' % self._url)
        branches = [b['commit']['id'] for b in json_response]
        return branches
