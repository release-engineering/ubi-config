import os

import pytest
from mock import patch
import yaml
from jsonschema.exceptions import ValidationError

from ubiconfig import ubi, UbiConfig


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
    with open(os.path.join(TEST_DATA_DIR, 'configs/dnf7/rhel-atomic-host.yaml')) as f:
        yield f


@pytest.fixture
def ubi7_config_file():
    with open(os.path.join(TEST_DATA_DIR, 'configs/ubi7/rhel-7-for-power-le.yaml')) as f:
        yield f


@pytest.fixture
def invalid_config_file():
    with open(os.path.join(TEST_DATA_DIR, 'bad_configs/invalid_config.yaml')) as f:
        yield f


@pytest.fixture
def syntax_error_file():
    with open(os.path.join(TEST_DATA_DIR, 'bad_configs/syntax_error.yaml')) as f:
        yield f


@pytest.fixture
def files_branch_map():
    return {'rhel-atomic-host.yaml': 'c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f',
            'rhel-7-for-power-le.yaml': '2189cbc2e447f796fe354f8d784d76b0a2620248'}


@pytest.fixture
def files_branch_map_with_error_config_file(files_branch_map):
    result_map = {'invaild_config.yaml': 'c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f',
                  'syntax_error.yaml': 'c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f'}
    result_map.update(files_branch_map)
    return result_map


@pytest.fixture
def response():
    def make_response(content):
        return FakeResponse(content)
    return make_response


@patch('requests.Session')
@patch('ubiconfig._impl.loaders._GitlabLoader._pre_load')
def test_load_all_from_default_repo(mocked_pre_load, mocked_session, files_branch_map,
                                    dnf7_config_file, ubi7_config_file, response):
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.get.side_effect = [response(dnf7_config_file),
                                                   response(ubi7_config_file)]
    loader = ubi.get_loader()
    configs = loader.load_all()
    configs = sorted(configs, key=repr)
    assert len(configs) == 2
    assert isinstance(configs[0], UbiConfig)
    assert str(configs[1]) == 'rhel-atomic-host.yaml'


@patch('requests.Session')
@patch('ubiconfig._impl.loaders._GitlabLoader._pre_load')
def test_load_all_with_error_config(mocked_pre_load, mocked_session, dnf7_config_file,
                                    ubi7_config_file, invalid_config_file, syntax_error_file,
                                    response, files_branch_map_with_error_config_file):
    mocked_pre_load.return_value = files_branch_map_with_error_config_file
    mocked_session.return_value.get.side_effect = [response(dnf7_config_file),
                                                   response(ubi7_config_file),
                                                   response(invalid_config_file),
                                                   response(syntax_error_file)]

    loader = ubi.get_loader()
    configs = loader.load_all()
    assert mocked_session.return_value.get.call_count == 4
    assert len(configs) == 2


def test_load_from_local():
    loader = ubi.get_loader(TEST_DATA_DIR)
    # loads relative to given path
    config = loader.load('configs/dnf7/rhel-atomic-host.yaml')
    assert isinstance(config, UbiConfig)


def test_load_from_local_decimal_integrity():
    loader = ubi.get_loader(TEST_DATA_DIR)
    config = loader.load('configs/dnf7/rhel-atomic-host.yaml')
    assert config.modules.whitelist[2].stream == '1.10'


def test_load_from_nonyaml(tmpdir):
    somefile = tmpdir.join('some-file.txt')
    somefile.write('[oops, this is not valid yaml')

    loader = ubi.get_loader(str(tmpdir))

    with pytest.raises(yaml.YAMLError):
        loader.load('some-file.txt')


def test_load_local_failed_validation():
    loader = ubi.get_loader(TEST_DATA_DIR)

    with pytest.raises(ValidationError):
        loader.load('bad_configs/invalid_config.yaml')


def test_load_all_from_local():
    repo = os.path.join(TEST_DATA_DIR, 'configs/dnf7')
    loader = ubi.get_loader(repo)
    configs = loader.load_all()
    assert len(configs) == 1
    assert isinstance(configs[0], UbiConfig)


def test_load_all_from_local_with_error_configs():
    loader = ubi.get_loader(TEST_DATA_DIR)
    configs = loader.load_all()

    assert len(configs) == 2


def test_load_all_from_local_recursive():
    repo = os.path.join(TEST_DATA_DIR, "configs")
    loader = ubi.get_loader(repo)
    configs = loader.load_all()
    assert len(configs) == 2
    assert isinstance(configs[0], UbiConfig)


def test_get_loader_notexist(tmpdir):
    with pytest.raises(ubi.LoaderError) as exc:
        ubi.get_loader(str(tmpdir.join("not-exist-dir")))

    assert 'not an existing directory' in str(exc.value)


def test_default_or_local_repo_not_set():
    try:
        ubi.DEFAULT_UBI_REPO = ''

        expected_error = ('Please either set a source or define DEFAULT_UBI_REPO '
                          'in your environment')

        with pytest.raises(ubi.LoaderError) as exc:
            ubi.get_loader()

        assert str(exc.value) == expected_error

    finally:
        ubi.DEFAULT_UBI_REPO = 'https://contentdelivery.com/ubi/data'


@patch('requests.Session')
def test_get_empty_branches(mocked_session):
    mocked_session.return_value.get.return_value.json.return_value = {}
    exception = RuntimeError(('Please check https://contentdelivery.com/ubi/data '
                              'is in right format'))
    try:
        ubi.get_loader()
        raise AssertionError('test should fail!')
    except RuntimeError as actual_exception:
        assert actual_exception.args == exception.args


@patch('requests.Session')
def test_get_branches(mocked_session):
    branches = [{'name': 'dnf7',
                 'commit': {'id': 'c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f'}},
                {'name': 'ubi7',
                 'commit': {'id': '2189cbc2e447f796fe354f8d784d76b0a2620248'}}]
    headers = {'Content-Length': '629', 'X-Total-Pages': '1', 'X-Per-Page': '20'}
    mocked_session.return_value.get.return_value.headers = headers
    mocked_session.return_value.get.return_value.json.return_value = branches
    loader = ubi.get_loader()
    actual_branches = loader._get_branches()
    assert actual_branches == ['c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f',
                               '2189cbc2e447f796fe354f8d784d76b0a2620248']


@patch('requests.Session')
@patch('ubiconfig._impl.loaders._GitlabLoader._get_branches')
def test_pre_load(mocked_get_branches, mocked_session, files_branch_map):
    branches = ['c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f',
                '2189cbc2e447f796fe354f8d784d76b0a2620248']
    mocked_get_branches.return_value = branches
    headers = {'Content-Length': '629', 'X-Total-Pages': '1', 'X-Per-Page': '20'}
    mocked_session.return_value.get.return_value.headers = headers
    file_list = [[{'name': 'rhel-atomic-host.yaml', 'path': 'rhel-atomic-host.yaml'},
                  {'name': 'README.md', 'path': 'README.md'}],
                 [{'name': 'rhel-7-for-power-le.yaml', 'path': 'rhel-7-for-power-le.yaml'}]]
    mocked_session.return_value.get.return_value.json.side_effect = file_list
    loader = ubi.get_loader()
    expected_map = files_branch_map
    actual_files_branch_map = loader._files_branch_map
    assert expected_map == actual_files_branch_map


def test_ubi_config(dnf7_config_file):
    config_dict = yaml.safe_load(dnf7_config_file)
    config = UbiConfig.load_from_dict(config_dict, 'rhel-atomic-host.yaml')
    assert config.modules[0].name == 'nodejs'
    assert config.content_sets.rpm.input == 'rhel-atomic-host-rpms'
    assert str(config.packages.blacklist[0]) == '<Package: kernel*>'
