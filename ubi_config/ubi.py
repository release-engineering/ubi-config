import os
import logging

import yaml
import requests

from .config_types import content_sets, packages, modules
from .utils.config_validation import validate_config
from .utils.api.gitlab import RepoApi


DEFAULT_UBI_REPO = os.getenv("DEFAULT_UBI_REPO", "")

logging.basicConfig()
LOG = logging.getLogger('ubi_config')


def get_loader(local=False, local_repo=None):
    """Get a Loader instance which is used to load configurations.

    The default config file source is as DEFAULT_UBI_REPO/configfile.yaml,
    when use_local is not set, it will check if the DEFAULT_UBI_REPO is set
    or not, then creates a requests session and pass it to Loader.

    Or if use_local is set, then user can pass the local_repo address to
    Loader or send full path to loader.load(), for example:

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
    ##TODO: possible ssl verification options
    """
    if not local:
        if not DEFAULT_UBI_REPO:
            msg = 'Please either set use_local or define DEFAULT_UBI_URL in your environment'
            raise ValueError(msg)
        session = requests.Session()
        repo_apis = RepoApi(DEFAULT_UBI_REPO.rstrip('/'))
        session.get(repo_apis.api_url)
        return Loader(session=session, repo_api=repo_apis)
    else:
        return Loader(local=True, local_repo=local_repo)


class UbiConfig(object):
    """wrap all UBI related configurations"""
    def __init__(self, cs, pkgs, mds, file_name):
        self.content_sets = cs
        self.packages = pkgs
        self.modules = mds
        self.file_name = file_name

    def __repr__(self):
        return self.file_name


class Loader(object):
    """ load configuration from default repo or from local file."""
    def __init__(self, session=None, repo_api=None, local=False, local_repo=None):
        self.session = session
        self.repo_api = repo_api
        self.local = local
        self.local_repo = local_repo
        if not self.local:
            self.files_branch_map = self._pre_load()

    def load(self, file_name):
        """
        Load a single configuration file and return a UbiConfig Object

        Use cases:
          Remote:
            1. repo url is the root url, such as host/project/:
              a. called by load_all() the branch will be read from the
                self.files_branch_map
              b. called directly by user, the branch will be read from
                 self.files_branch_map

          Local:
            1. called directly by user without self.local_repo specified:
              user needs to pass the full path
            2. called by load_all():
              a. without defining the self.local_repo, error will be raised
              b. or load all config files from a local_repo
              ##TODO: make it git aware
        """
        if not self.local:
            # find the right branch from the mapping
            branch = self.files_branch_map[file_name]
            config_file_url = self.repo_api.get_file_content_api(file_name, branch)
            LOG.info("Loading configuration file from remote: %s", file_name)
            response = self.session.get(config_file_url)
            response.raise_for_status()
            try:
                config_dict = yaml.safe_load(response.content)
            except yaml.YAMLError:
                LOG.error('There is syntax error in your config file %s, please fix', file_name)
                raise
        else:
            if self.local_repo:
                file_path = os.path.join(self.local_repo, file_name)
            else:
                file_path = file_name
            LOG.info("Loading configuration file locally: %s", file_path)
            with open(file_path, 'r') as f:
                config_dict = yaml.safe_load(f)

        # validate input data
        validate_config(config_dict)
        m_data = modules.Modules.load_from_dict(config_dict.get('modules', {}))
        pkgs = config_dict.get('packages', {})
        pkgs_data = packages.Packages(pkgs.get('include', []),
                                      pkgs.get('exclude', []),
                                      config_dict.get('arches', []))
        cs_map = content_sets.ContentSetsMapping.load_from_dict(config_dict['content_sets'])
        # use the simplified file name
        file_name = file_name.split('/')[-1]

        return UbiConfig(cs_map, pkgs_data, m_data, file_name)

    def load_all(self, recursive=False):
        """get the list of config files from repo and call load on every file.
        Return a list of UbiConfig objects.

        If recursive is set, it will walk through the submodules, no matter local
        or remote
        """
        ubi_configs = []
        # if not load from local repo, then self.files_branch_map should be loaded
        if not self.local:
            for file in self.files_branch_map:
                LOG.debug("Now loading %s from branch %s", file, self.files_branch_map[file])
                ubi_configs.append(self.load(file))
        else:
            file_list = self._get_local_file_list(recursive)
            for file in file_list:
                LOG.debug("Now loading %s", file)
                ubi_configs.append(self.load(file))

        return ubi_configs

    def _get_local_file_list(self, recursive=False):
        """
        Get the config file list from local. If recusive is set, then it would walk
        through the sub-modules.
        """
        LOG.info('Getting the local config file list')
        if self.local_repo is None:
            raise RuntimeError('You need to set local repo to load all files')
        file_list = []
        if recursive:
            for root, _, files in os.walk(self.local_repo):
                files = [os.path.join(root, f) for f in files if f.endswith(('.yaml', '.yml'))]
                file_list.extend(files)
        else:
            file_list = [file for file in os.listdir(self.local_repo)
                         if file.endswith(('yaml', '.yml'))]

        return file_list

    def _pre_load(self, recursive=False):
        """iterate all branches to get a mapping of {file_path: branch,...}
        """
        files_branch_map = {}
        branches = self._get_branches()
        LOG.info("Loading config files from all branches: %s", branches)
        for branch in branches:
            file_list_api = self.repo_api.get_file_list_api(branch=branch,
                                                            recursive=recursive)
            json_response = self.session.get(file_list_api).json()
            file_list = [file['path'] for file in json_response
                         if file['name'].endswith(('.yaml', '.yml'))]
            for file in file_list:
                files_branch_map[file] = branch
        return files_branch_map

    def _get_branches(self):
        """Get all the branches of a given repo"""
        LOG.info("Getting branches of the repo")
        branches_list_api = self.repo_api.get_branch_list_api()
        json_response = self.session.get(branches_list_api).json()
        if not json_response:
            raise RuntimeError('Please check your DEFAULT_UBI_REPO is in right format')
        branches = [b['name'] for b in json_response]
        return branches
