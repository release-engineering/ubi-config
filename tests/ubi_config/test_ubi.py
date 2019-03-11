import os

from collections import OrderedDict
import pytest
from mock import patch, MagicMock
import yaml

from ubi_config import ubi
from ubi_config.utils.api.gitlab import RepoApi


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
ubi.DEFAULT_UBI_REPO = 'https://contentdelivery.com/ubi/data'


class FakeResponse():
    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        # currently it's not demanded.
        return None


@pytest.fixture
def dnf7_config_file():
    dnf7 = open(os.path.join(TEST_DATA_DIR, 'configs/dnf7/rhel-atomic-host.yaml'))
    return dnf7


@pytest.fixture
def ubi7_config_file():
    ubi7 = open(os.path.join(TEST_DATA_DIR, 'configs/ubi7/rhel-7-for-power-le.yaml'))
    return ubi7


@pytest.fixture
def files_branch_map():
    return OrderedDict({'rhel-atomic-host.yaml': 'dnf7',
                        'rhel-7-for-power-le.yaml': 'ubi7'})


@pytest.fixture
def response():
    def make_response(content):
        return FakeResponse(content)
    return make_response


@patch('requests.Session')
@patch('ubi_config.ubi.Loader._pre_load')
def test_load_all_from_default_repo(mocked_pre_load, mocked_session, files_branch_map,
                                    dnf7_config_file, ubi7_config_file, response):
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.get.side_effect = ['200 OK',
                                                   response(dnf7_config_file),
                                                   response(ubi7_config_file)
                                                ]
    loader = ubi.get_loader()
    # import pdb; pdb.set_trace()
    configs = loader.load_all()
    assert len(configs) == 2
    assert isinstance(configs[0], ubi.UbiConfig)
    assert configs[0].modules.whitelist[0].name == 'nodejs'


def test_load_from_local():
    loader = ubi.get_loader(local=True)
    # pass the complete path to load
    config = loader.load(os.path.join(TEST_DATA_DIR, 'configs/dnf7/rhel-atomic-host.yaml'))
    assert isinstance(config, ubi.UbiConfig)


def test_load_all_from_local():
    repo = os.path.join(TEST_DATA_DIR, 'configs/dnf7')
    loader = ubi.get_loader(local=True, local_repo=repo)
    configs = loader.load_all()
    assert len(configs) == 1
    assert isinstance(configs[0], ubi.UbiConfig)


def test_load_all_from_local_recursive():
    repo = os.path.join(TEST_DATA_DIR, 'configs')
    loader = ubi.get_loader(local=True, local_repo=repo)
    configs = loader.load_all(recursive=True)
    assert len(configs) == 2
    assert isinstance(configs[0], ubi.UbiConfig)


def test_syntax_from_config_file():
    loader = ubi.get_loader(local=True, local_repo=TEST_DATA_DIR)
    try:
        configs = loader.load('bad_configs/syntax_error.yaml')
        raise AssertionError('load should fail!')
    except yaml.YAMLError as e:
        assert e.problem == "expected <block end>, but found '?'"


def test_default_or_local_repo_not_set():
    ubi.DEFAULT_UBI_REPO = ''
    expected_error = ValueError('Please either set use_local or define \
DEFAULT_UBI_URL in your environment')
    try:
        loader = ubi.get_loader()
        raise AssertionError('should not get a loader!')
    except ValueError as e:
        assert isinstance(e, type(expected_error))
        assert e.args == expected_error.args
    ubi.DEFAULT_UBI_REPO = 'https://contentdelivery.com/ubi/data'


def test_load_all_from_local_without_repo_set():
    loader = ubi.get_loader(local=True)
    try:
        loader.load_all()
        raise AssertionError('should fail!')
    except RuntimeError as e:
        assert e.args == ('You need to set local repo to load all files',)


@patch('requests.Session')
def test_get_empty_branches(mocked_session):
    mocked_session.get.return_value.json.return_value = {}
    repo_apis = RepoApi(ubi.DEFAULT_UBI_REPO)
    exception = RuntimeError('Please check your DEFAULT_UBI_REPO is in right format')
    try:
        loader = ubi.Loader(session=mocked_session, repo_api=repo_apis)
        raise AssertionError('test should fail!')
    except RuntimeError as actual_exception:
        assert actual_exception.args == exception.args


@patch('requests.Session')
def test_get_branches(mocked_session):
    branches = [{'name': 'dnf7', 'default': True, 'can_push': True},
                {'name': 'ubi7', 'default': False, 'can_push': True}]
    mocked_session.get.return_value.json.return_value = branches
    repo_apis = RepoApi(ubi.DEFAULT_UBI_REPO)
    with patch('ubi_config.ubi.Loader._pre_load'):
        loader = ubi.Loader(session=mocked_session, repo_api=repo_apis)
        actual_branches = loader._get_branches()
    assert actual_branches == ['dnf7', 'ubi7']


@patch('requests.Session')
@patch('ubi_config.ubi.Loader._get_branches')
def test_pre_load(mocked_get_branches, mocked_session, files_branch_map):
    branches = ['dnf7', 'ubi7']
    mocked_get_branches.return_value = branches
    file_list = [[{'name': 'rhel-atomic-host.yaml', 'path': 'rhel-atomic-host.yaml'},
                  {'name': 'README.md', 'path': 'README.md'}],
                 [{'name': 'rhel-7-for-power-le.yaml', 'path': 'rhel-7-for-power-le.yaml'}]]
    mocked_session.get.return_value.json.side_effect = file_list
    repo_apis = RepoApi(ubi.DEFAULT_UBI_REPO)
    loader = ubi.Loader(session=mocked_session, repo_api=repo_apis)
    expected_map = files_branch_map
    actual_files_branch_map = loader.files_branch_map
    assert expected_map == actual_files_branch_map
