"""provide gitlab api used to read repositories"""
import os
import re

from six.moves.urllib.parse import urljoin


DEFAULT_GIT_LAB_URL_FMT = re.compile(r"(?P<host>.+com|org|net)/(?P<project>.+)")

API_FORMAT = "%s/api/v%s/projects/%s/"  # hostname/api/:apiversion/projects/:id/

GIT_LAB_URL_FMT = re.compile(os.getenv("GIT_LAB_URL_FMT", DEFAULT_GIT_LAB_URL_FMT))


class RepoApi(object):
    """Used to generate the gitlab api used to access the config files.config
    It will parse the repo url to get according api with right host, id and
    branch.
    Users can also set their own regular expression format if the host doesn't end
    with .com/org/net
    The default api version is 4
    """
    def __init__(self, repo_url, v_3=False):
        m = GIT_LAB_URL_FMT.match(repo_url)
        if not m:
            raise ValueError("The hostname must end with '.com|org|net' \
or set GIT_LAB_URL_FMT by yourself")
        self.host = m.group('host')
        self.repo_id = m.group('project').replace('/', '%2F')
        self.v_3 = v_3

    @property
    def api_url(self):
        if self.v_3:
            return API_FORMAT % (self.host, '3', self.repo_id)
        return API_FORMAT % (self.host, '4', self.repo_id)

    def get_branch_list_api(self):
        return urljoin(self.api_url, 'repository/branches')

    def get_file_list_api(self, page, branch=None):
        """Return the api used to get the list of files in the repo or files
        in the sub-module.
        """
        branch = branch.replace('/', '%2F') if branch else 'master'
        return urljoin(self.api_url, 'repository/tree?ref=%s&page=%s' % (branch, page))

    def get_file_content_api(self, file_path, branch=None):
        """Get the api used to retrieve the raw content.
        The input file_path should be from get_files_list_api or the full path to the file,
        for example:
            The url is 'https://some-host.com/ubi-config-data/tree/master/data/ubi7/config.yaml'
            Then the file path should data/ubi7/config.yaml
        """
        branch = branch.replace('/', '%2F') if branch else 'master'
        encoded_file_path = file_path.replace('/', '%2F')
        return urljoin(self.api_url, 'repository/files/%s/raw?ref=%s' % (encoded_file_path, branch))
