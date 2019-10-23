import logging
import yaml
import requests

from jsonschema.exceptions import ValidationError

from ubiconfig.utils.api.gitlab import RepoApi
from ubiconfig.utils.config_validation import validate_config
from ubiconfig.config_types import UbiConfig

from .base import Loader

LOG = logging.getLogger("ubiconfig")


class GitlabLoader(Loader):
    """Load configuration from a remote repo on gitlab."""

    def __init__(self, url):
        """
        :param url: gitlab repo url in form of `https://<host>/<repo>`
        """
        self._url = url
        self._session = requests.Session()
        self._repo_api = RepoApi(self._url.rstrip("/"))
        self._branches = self._get_branches()
        self._files_branch_map = self._pre_load()

    def load(self, file_name, version=None):
        """ Load file from remote repository.
        :param file_name: filename that is on remote repository in any branch
        """
        if file_name not in self._files_branch_map:
            raise ValueError(
                "Couldn't find file %s from remote repo %s" % (file_name, self._url)
            )

        sha1 = self._branches.get(version)
        if version and not sha1:
            LOG.warning(
                "Couldn't find version %s from %s, will try to find %s in default",
                version,
                self._url,
                file_name,
            )

        if not version or not sha1:
            # branch is not available from the wanted version or not specified,
            # use the default version.
            for branch_sha1 in self._files_branch_map[file_name]:
                if branch_sha1[0] == "ubi7":
                    version = "ubi7"
                    break
            else:
                version = "ubi8"
            sha1 = self._branches[version]

        LOG.info("Loading config file %s from branch %s", file_name, version)
        config_file_url = self._repo_api.get_file_content_api(file_name, sha1)
        response = self._session.get(config_file_url)
        response.raise_for_status()

        config_dict = yaml.load(response.content, Loader=yaml.BaseLoader)
        # validate input data
        validate_config(config_dict)

        return UbiConfig.load_from_dict(config_dict, file_name, version[3:])

    def load_all(self):
        ubi_configs = []
        for f in self._files_branch_map:
            for branch_sha1 in self._files_branch_map[f]:
                LOG.debug("Now loading %s from branch %s", f, branch_sha1[0])
                try:
                    ubi_configs.append(self.load(f, branch_sha1[0]))
                except yaml.YAMLError:
                    LOG.error(
                        "%s FAILED loading because of Syntax error, skipping for now", f
                    )
                    continue
                except ValidationError as e:
                    LOG.error("%s FAILED schema validation:\n%s\nSkip for now", f, e)
                    continue

        return ubi_configs

    def _pre_load(self):
        """Iterate all branches to get a mapping of {file_path: (branch, sha1)...}
        """
        files_branch_map = {}

        LOG.debug("Loading config files from all branches")

        for branch, sha1 in self._branches.items():
            page = 1
            while True:
                file_list_api = self._repo_api.get_file_list_api(branch=sha1, page=page)
                response = self._session.get(file_list_api)
                response.raise_for_status()
                file_list = [
                    f["path"]
                    for f in response.json()
                    if f["name"].endswith((".yaml", ".yml"))
                ]
                for f in file_list:
                    files_branch_map.setdefault(f, []).append((branch, sha1))
                    # now the map is {filename: [(branch1, sha1), (branch2, sha1),...]}
                    # same file name could map to multiple config files.
                if page >= int(response.headers.get("X-Total-Pages", 1)):
                    break
                page += 1

        return files_branch_map

    def _get_branches(self):
        """Get a {branch: sha1} mapping for all branches of a given repo"""
        branch_sha1 = {}

        LOG.info("Getting branches of the repo")
        branches_list_api = self._repo_api.get_branch_list_api()
        json_response = self._session.get(branches_list_api).json()
        if not json_response:
            raise RuntimeError("Please check %s is in right format" % self._url)
        for b in json_response:
            branch_sha1[b["name"]] = b["commit"]["id"]

        return branch_sha1
