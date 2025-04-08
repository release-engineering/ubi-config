import pytest
import requests
import requests_mock
import yaml
from mock import MagicMock, Mock, patch

from ubiconfig._impl.loaders import _GitlabLoader


def mock_json(value, headers=None):
    out = MagicMock()
    out.json.return_value = value
    if headers:
        out.headers = headers
    return out


def test_bad_yaml():
    with patch("requests.Session") as mock_session_class:
        session = mock_session_class.return_value
        session.request.side_effect = [
            # branches
            mock_json(
                [
                    {
                        "name": "ubi7",
                        "commit": {"id": "2189cbc2e447f796fe354f8d784d76b0a2620248"},
                    }
                ]
            ),
            # files and headers
            mock_json(
                [{"name": "badfile.yaml", "path": "badfile.yaml"}],
                {"Content-Length": "629", "X-Total-Pages": "2", "X-Per-Page": "20"},
            ),
            mock_json(
                [{"name": "badfile1.yaml", "path": "badfile1.yaml"}],
                {"Content-Length": "629", "X-Total-Pages": "2", "X-Per-Page": "20"},
            ),
            # content (not valid yaml!)
            Mock(content="[oops not yaml"),
        ]
        loader = _GitlabLoader("https://some-repo.example.com/foo/bar")

        # It should propagate the YAML load exception
        with pytest.raises(yaml.YAMLError):
            loader.load("badfile.yaml", "ubi7")


def test_bad_json():
    with requests_mock.Mocker() as m:
        m.get(
            "https://some-repo.example.com/api/v4/projects/foo%2Fbar/repository/branches"
        )

        with pytest.raises(requests.exceptions.JSONDecodeError):
            _GitlabLoader("https://some-repo.example.com/foo/bar")


def test_request_error():
    with requests_mock.Mocker() as m:
        m.get(
            "https://some-repo.example.com/api/v4/projects/foo%2Fbar/repository/branches",
            status_code=500,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            _GitlabLoader("https://some-repo.example.com/foo/bar")
