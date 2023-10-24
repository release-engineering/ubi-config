import logging
import re
import yaml
import os
import requests

from jsonschema.exceptions import ValidationError
from urllib3 import Retry
from requests.adapters import HTTPAdapter

from ubiconfig.utils.api.gitlab import RepoApi
from ubiconfig.utils.config_validation import validate_config
from ubiconfig.config_types import UbiConfig

from .base import Loader

LOG = logging.getLogger("ubiconfig")

BRANCH_RE = re.compile(r"^(?P<prefix>[\w-]{1,25})(?P<default_version>[\d]{1,2})")

GITLAB_RETRIES = int(os.getenv("UBICONFIG_GITLAB_RETRIES", "5"))
GITLAB_BACKOFF = float(os.getenv("UBICONFIG_GITLAB_BACKOFF", "0.5"))


class GitlabLoader(Loader):
    """Load configuration from a remote repo on gitlab."""

    def __init__(self, url):
        """
        :param url: gitlab repo url in form of `https://<host>/<repo>`
        """
        self._url = url
        self._session = None
        self._repo_api = RepoApi(self._url.rstrip("/"))
        self._branches = self._get_branches()
        self._files_branch_map = self._pre_load()

    @property
    def session(self):
        if not self._session:
            retries = Retry(
                total=GITLAB_RETRIES,
                status_forcelist=[429, 500, 502, 503, 504],
                backoff_factor=GITLAB_BACKOFF,
            )
            session = requests.Session()
            session.mount("https://", HTTPAdapter(max_retries=retries))
            session.mount("http://", HTTPAdapter(max_retries=retries))
            self._session = session

        return self._session

    def do_request(self, **kwargs):
        try:
            response = self.session.request(**kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            LOG.exception(
                "Error ocurred during request to GitLab, check exception details."
            )
            raise

        return response

    def try_json(self, response):
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            LOG.exception("Cannot convert response to JSON.")
            raise

    def load(self, file_name, version=None):
        """Load file from remote repository.
        :param file_name: filename that is on remote repository in any branch
        :param version: name of remote branch
        """
        if version is None:
            raise ValueError(
                "Provide valid name of remote branch, provided %s" % version
            )

        if file_name not in self._files_branch_map:
            raise ValueError(
                "Couldn't find file %s from remote repo %s" % (file_name, self._url)
            )

        match = re.match(BRANCH_RE, version)
        if not match:
            raise ValueError("Invalid version (branch name) %s" % version)

        prefix = match.group("prefix")
        default_version = match.group("default_version")

        default_branch = f"{prefix}{default_version}"

        sha1 = None
        loaded_version = None

        for branch_name in (version, default_branch):
            sha1 = self._branches.get(branch_name)
            if sha1:
                loaded_version = branch_name.lstrip(prefix)
                break

        if sha1 is None:
            raise ValueError(
                "Couldn't find version %s and default branch %s from %s for %s"
                % (version, default_branch, self._url, file_name)
            )

        LOG.info("Loading config file %s from branch %s", file_name, version)
        config_file_url = self._repo_api.get_file_content_api(file_name, sha1)
        response = self.do_request(method="GET", url=config_file_url)

        config_dict = yaml.load(response.content, Loader=yaml.BaseLoader)
        # validate input data
        validate_config(config_dict)

        return UbiConfig.load_from_dict(config_dict, file_name, loaded_version)

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
        """Iterate all branches to get a mapping of {file_path: (branch, sha1)...}"""
        files_branch_map = {}

        LOG.debug("Loading config files from all branches")

        for branch, sha1 in self._branches.items():
            page = 1
            while True:
                file_list_api = self._repo_api.get_file_list_api(branch=sha1, page=page)
                response = self.do_request(method="GET", url=file_list_api)
                data = self.try_json(response)
                file_list = [
                    f["path"] for f in data if f["name"].endswith((".yaml", ".yml"))
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
        response = self.do_request(method="GET", url=branches_list_api)
        data = self.try_json(response)

        if not data:
            raise RuntimeError("Please check %s is in right format" % self._url)
        for b in data:
            branch_sha1[b["name"]] = b["commit"]["id"]

        return branch_sha1
