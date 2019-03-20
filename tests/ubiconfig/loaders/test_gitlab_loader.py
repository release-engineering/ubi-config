from mock import patch, MagicMock, Mock
import pytest
import yaml

from ubiconfig._impl.loaders import GitlabLoader


def mock_json(value):
    out = MagicMock()
    out.json.return_value = value
    return out


def test_bad_yaml():
    with patch('requests.Session') as mock_session_class:
        session = mock_session_class.return_value
        session.get.side_effect = [
            # branches
            mock_json([{'name': 'master'}]),

            # files
            mock_json([{'name': 'badfile.yaml', 'path': 'badfile.yaml'}]),

            # content (not valid yaml!)
            Mock(content='[oops not yaml'),
        ]

        loader = GitlabLoader('https://some-repo.example.com/foo/bar', per_page=30)

        # It should propagate the YAML load exception
        with pytest.raises(yaml.YAMLError):
            loader.load('badfile.yaml')
