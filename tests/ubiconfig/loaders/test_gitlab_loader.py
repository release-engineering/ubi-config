import os

import pytest
import yaml
from mock import patch, MagicMock, Mock

from ubiconfig._impl.loaders import GitlabLoader
from ubiconfig.exceptions import ConfigNotFound

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')


@pytest.fixture
def ubi7_config_file():
    with open(os.path.join(TEST_DATA_DIR, 'configs/ubi7/rhel-7-for-power-le.yaml')) as f:
        yield f


def mock_json(value, headers=None):
    out = MagicMock()
    out.json.return_value = value
    if headers:
        out.headers = headers
    return out


def test_bad_yaml():
    with patch('requests.Session') as mock_session_class:
        session = mock_session_class.return_value
        session.get.side_effect = [
            # branches
            mock_json([{'name': 'master',
                        'commit': {'id': '2189cbc2e447f796fe354f8d784d76b0a2620248'}}]),

            # files and headers
            mock_json([{'name': 'badfile.yaml', 'path': 'badfile.yaml'}],
                      {'Content-Length': '629', 'X-Total-Pages': '2', 'X-Per-Page': '20'}),

            mock_json([{'name': 'badfile1.yaml', 'path': 'badfile1.yaml'}],
                      {'Content-Length': '629', 'X-Total-Pages': '2', 'X-Per-Page': '20'}),

            # content (not valid yaml!)
            Mock(content='[oops not yaml'),
        ]
        loader = GitlabLoader('https://some-repo.example.com/foo/bar')

        # It should propagate the YAML load exception
        with pytest.raises(yaml.YAMLError):
            loader.load('badfile.yaml')


@pytest.mark.parametrize('cs_label', [
    'ubi-7-for-power-le-rpms', 'ubi-7-for-power-le-source-rpms', 'ubi-7-for-power-le-debug-rpms'
])
def test_load_from_cs(cs_label, ubi7_config_file):
    with patch('requests.Session') as mock_session_class:
        session = mock_session_class.return_value
        session.get.side_effect = [
            # branches
            mock_json([{'name': 'master',
                        'commit': {'id': '2189cbc2e447f796fe354f8d784d76b0a2620248'}}]),

            # files and headers
            mock_json([{'name': 'ubi-7-for-power-le.yaml', 'path': 'ubi-7-for-power-le.yaml'}],
                      {'Content-Length': '629', 'X-Total-Pages': '2', 'X-Per-Page': '20'}),

            mock_json([{'name': 'ubi-8-for-power-le.yaml', 'path': 'ubi-8-for-power-le.yaml'}],
                      {'Content-Length': '629', 'X-Total-Pages': '2', 'X-Per-Page': '20'}),

            # content
            Mock(content=ubi7_config_file),
        ]
        loader = GitlabLoader('https://some-repo.example.com/foo/bar')
        config = loader.load_from_cs_label(cs_label)

    # check that load_from_cs_label stripped 'rpm' suffix
    assert str(config) == 'ubi-7-for-power-le.yaml'


def test_load_from_cs_with_bad_label():
    with patch('requests.Session') as mock_session_class:
        session = mock_session_class.return_value
        session.get.side_effect = [
            # branches
            mock_json([{'name': 'master',
                        'commit': {'id': '2189cbc2e447f796fe354f8d784d76b0a2620248'}}]),

            # files and headers
            mock_json([{'name': 'ubi-7-for-power-le.yaml', 'path': 'ubi-7-for-power-le.yaml'}],
                      {'Content-Length': '629', 'X-Total-Pages': '2', 'X-Per-Page': '20'}),

            mock_json([{'name': 'ubi-8-for-power-le.yaml', 'path': 'ubi-8-for-power-le.yaml'}],
                      {'Content-Length': '629', 'X-Total-Pages': '2', 'X-Per-Page': '20'}),

            # content
            Mock(content=ubi7_config_file),
        ]
        loader = GitlabLoader('https://some-repo.example.com/foo/bar')

        with pytest.raises(ConfigNotFound) as e:
            loader.load_from_cs_label('non-existent-rpms')

        assert "No config found for label: non-existent-rpms" in str(e.value)
