from urllib.parse import urljoin

import pytest

from ubiconfig.utils.api import gitlab


@pytest.fixture
def v4_repo_api():
    return gitlab.RepoApi("https://test-host.com/ubi/data")


@pytest.fixture
def v4_api_prefix(v4_repo_api):
    return v4_repo_api.api_url


def test_v4_api_prefix(v4_api_prefix):
    assert v4_api_prefix == "https://test-host.com/api/v4/projects/ubi%2Fdata/"


def test_get_branch_list_api(v4_repo_api, v4_api_prefix):
    expected_branch_api = urljoin(v4_api_prefix, "repository/branches")
    assert v4_repo_api.get_branch_list_api() == expected_branch_api


def test_get_file_list_api(v4_repo_api, v4_api_prefix):
    expected_file_list_api = urljoin(v4_api_prefix, "repository/tree?ref=master&page=1")
    v4_repo_api.get_file_list_api(page=1) == expected_file_list_api


def test_file_content_api(v4_repo_api, v4_api_prefix):
    file_path = "some/path"
    expected_file_content_api = urljoin(
        v4_api_prefix, "repository/files/some%2Fpath/raw?ref=master"
    )
    assert v4_repo_api.get_file_content_api(file_path) == expected_file_content_api


def test_gitlab_api_v3():
    repo_api = gitlab.RepoApi("https://test-host.com/ubi/data", v_3=True)
    assert repo_api.api_url == "https://test-host.com/api/v3/projects/ubi%2Fdata/"


def test_host_name_invalid():
    expect_msg = (
        "The hostname must end with '.com|org|net' or set GIT_LAB_URL_FMT by yourself"
    )
    try:
        gitlab.RepoApi("https://test-host.cc/ubi/data")
        raise AssertionError("should fail!")
    except ValueError as e:
        assert e.args == (expect_msg,)
