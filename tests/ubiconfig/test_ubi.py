import os

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import pytest
from mock import patch
import yaml
from jsonschema.exceptions import ValidationError

from ubiconfig import ubi, UbiConfig


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
ubi.DEFAULT_UBI_REPO = "https://contentdelivery.com/ubi/data"


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        # currently it's not demanded.
        return None


@pytest.fixture
def ubi7_1_config_file1():
    with open(os.path.join(TEST_DATA_DIR, "configs/ubi7.1/rhel-atomic-host.yaml")) as f:
        yield f


@pytest.fixture
def ubi7_1_config_file2():
    with open(os.path.join(TEST_DATA_DIR, "configs/ubi7.1/rhel-7-server.yaml")) as f:
        yield f


@pytest.fixture
def ubi7_config_file():
    with open(os.path.join(TEST_DATA_DIR, "configs/ubi7/rhel-7-server.yaml")) as f:
        yield f


@pytest.fixture
def ubi8_config_file():
    with open(
        os.path.join(TEST_DATA_DIR, "configs/ubi8/rhel-8-for-power-le.yaml")
    ) as f:
        yield f


@pytest.fixture
def invalid_config_file():
    with open(os.path.join(TEST_DATA_DIR, "bad_configs/ubi7/invalid_config.yaml")) as f:
        yield f


@pytest.fixture
def syntax_error_file():
    with open(os.path.join(TEST_DATA_DIR, "bad_configs/ubi7/syntax_error.yaml")) as f:
        yield f


@pytest.fixture
def branches():
    return {
        "ubi7.1": "2189cbc2e447f796fe354f8d784d76b0a2620248",
        "ubi7": "c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f",
        "ubi8": "26d24af7859df3c4d361bd33cd57984d03abe206",
    }


@pytest.fixture
def files_branch_map():
    return OrderedDict(
        [
            (
                "rhel-atomic-host.yaml",
                [("ubi7.1", "2189cbc2e447f796fe354f8d784d76b0a2620248")],
            ),
            (
                "rhel-8-for-power-le.yaml",
                [("ubi8", "26d24af7859df3c4d361bd33cd57984d03abe206")],
            ),
            (
                "rhel-7-server.yaml",
                [
                    ("ubi7.1", "2189cbc2e447f796fe354f8d784d76b0a2620248"),
                    ("ubi7", "c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f"),
                ],
            ),
        ]
    )


@pytest.fixture
def files_branch_map_with_error_config_file(files_branch_map):
    result_map = {
        "invaild_config.yaml": [("ubi7", "c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f")],
        "syntax_error.yaml": [("ubi7.1", "2189cbc2e447f796fe354f8d784d76b0a2620248")],
    }
    result_map.update(files_branch_map)
    return result_map


@pytest.fixture
def response():
    def make_response(content):
        return FakeResponse(content)

    return make_response


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_all_from_default_repo(
    mocked_get_branches,
    mocked_pre_load,
    mocked_session,
    branches,
    files_branch_map,
    ubi7_1_config_file1,
    ubi7_1_config_file2,
    ubi7_config_file,
    ubi8_config_file,
    response,
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.request.side_effect = [
        response(ubi7_1_config_file1),
        response(ubi8_config_file),
        response(ubi7_1_config_file2),
        response(ubi7_config_file),
    ]
    loader = ubi.get_loader()
    configs = loader.load_all()
    configs = sorted(configs, key=repr)
    assert len(configs) == 4
    assert isinstance(configs[0], UbiConfig)
    assert str(configs[1]) == "rhel-7-server.yaml"
    assert configs[1].version == "7"


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_all_with_error_config(
    mocked_get_branches,
    mocked_pre_load,
    mocked_session,
    branches,
    ubi7_1_config_file1,
    ubi7_1_config_file2,
    ubi7_config_file,
    ubi8_config_file,
    invalid_config_file,
    syntax_error_file,
    response,
    files_branch_map_with_error_config_file,
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map_with_error_config_file
    mocked_session.return_value.request.side_effect = [
        response(ubi7_1_config_file1),
        response(ubi8_config_file),
        response(ubi7_1_config_file2),
        response(ubi7_config_file),
        response(invalid_config_file),
        response(syntax_error_file),
    ]

    loader = ubi.get_loader()
    configs = loader.load_all()
    assert mocked_session.return_value.request.call_count == 6
    assert len(configs) == 4


@pytest.mark.parametrize(
    "path, expected_version, filename",
    [
        ("configs/ubi7.1", "7.1", "rhel-atomic-host.yaml"),
        ("configs/test-prefix12.13", "12.13", "test-config.yaml"),
    ],
)
def test_load_from_local(path, expected_version, filename):
    path = os.path.join(TEST_DATA_DIR, path)
    loader = ubi.get_loader(path)
    # loads relative to given path
    config = loader.load(filename)
    assert isinstance(config, UbiConfig)
    assert config.version == expected_version


def test_load_from_local_decimal_integrity():
    loader = ubi.get_loader(TEST_DATA_DIR)
    config = loader.load("configs/ubi7.1/rhel-atomic-host.yaml")
    assert config.modules.whitelist[2].stream == "1.10"


def test_load_from_nonyaml(tmpdir):
    somefile = tmpdir.mkdir("ubi7").join("some-file.txt")
    somefile.write("[oops, this is not valid yaml")

    loader = ubi.get_loader(str(tmpdir))

    with pytest.raises(yaml.YAMLError):
        loader.load("ubi7/some-file.txt")


def test_load_local_failed_validation():
    loader = ubi.get_loader(TEST_DATA_DIR)

    with pytest.raises(ValidationError):
        loader.load("bad_configs/ubi7/invalid_config.yaml")


def test_load_all_from_local():
    repo = os.path.join(TEST_DATA_DIR, "configs/ubi7.1")
    loader = ubi.get_loader(repo)
    configs = loader.load_all()
    assert len(configs) == 2
    assert configs[0].version == "7.1"
    assert isinstance(configs[0], UbiConfig)


def test_load_from_directory_not_named_after_ubi():
    with patch("os.path.isdir"):
        loader = ubi.get_loader("./ubi7.1a")
        with pytest.raises(ValueError):
            config = loader.load("file")


def test_load_all_from_local_with_error_configs():
    loader = ubi.get_loader(TEST_DATA_DIR)
    configs = loader.load_all()

    assert len(configs) == 5


def test_load_all_from_local_recursive():
    repo = os.path.join(TEST_DATA_DIR, "configs")
    loader = ubi.get_loader(repo)
    configs = loader.load_all()
    assert len(configs) == 5
    assert isinstance(configs[0], UbiConfig)
    for conf in configs:
        # version should be populated
        assert hasattr(conf, "version")
        if conf.file_name == "rhel-8-for-power-le.yaml":
            # it's under ubi8 directory, version should be 8
            assert conf.version == "8"


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_file_non_exists_from_remote(
    mocked_get_branches, mocked_pre_load, mocked_session, branches, files_branch_map
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map

    with pytest.raises(ValueError):
        ubi.get_loader().load("non-exists.yaml", "ubi7")


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_file_without_providing_version(
    mocked_get_branches,
    mocked_pre_load,
    mocked_session,
    branches,
    files_branch_map,
    ubi7_config_file,
    response,
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.request.side_effect = [response(ubi7_config_file)]

    with pytest.raises(ValueError):
        ubi.get_loader().load("rhel-7-server.yaml")


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_invalid_branch_name(
    mocked_get_branches, mocked_pre_load, mocked_session, branches, files_branch_map
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map

    with pytest.raises(ValueError):
        ubi.get_loader().load("rhel-7-server.yaml", "invalid_branch")


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_file_with_wanted_version(
    mocked_get_branches,
    mocked_pre_load,
    mocked_session,
    branches,
    files_branch_map,
    ubi7_config_file,
    ubi8_config_file,
    response,
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.request.side_effect = [
        response(ubi7_config_file),
        response(ubi8_config_file),
    ]

    loader = ubi.get_loader()
    config = loader.load("rhel-7-server.yaml", "ubi7.1")
    assert config.version == "7.1"

    config = loader.load("rhel-8-for-power-le.yaml", "ubi8")
    assert config.version == "8"


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_file_with_non_exists_version(
    mocked_get_branches,
    mocked_pre_load,
    mocked_session,
    branches,
    files_branch_map,
    ubi8_config_file,
    response,
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.request.side_effect = [response(ubi8_config_file)]

    loader = ubi.get_loader()
    config = loader.load("rhel-8-for-power-le.yaml", "ubi8.20")

    assert config.version == "8"


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._pre_load")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_load_file_failed_fallback_to_default(
    mocked_get_branches,
    mocked_pre_load,
    mocked_session,
    branches,
    files_branch_map,
    ubi8_config_file,
    response,
):
    mocked_get_branches.return_value = branches
    mocked_pre_load.return_value = files_branch_map
    mocked_session.return_value.request.side_effect = [response(ubi8_config_file)]

    with pytest.raises(ValueError):
        loader = ubi.get_loader()
        config = loader.load("rhel-8-for-power-le.yaml", "ubi9.9")


def test_get_loader_notexist(tmpdir):
    with pytest.raises(ubi.LoaderError) as exc:
        ubi.get_loader(str(tmpdir.join("not-exist-dir")))

    assert "not an existing directory" in str(exc.value)


def test_default_or_local_repo_not_set():
    try:
        ubi.DEFAULT_UBI_REPO = ""

        expected_error = (
            "Please either set a source or define DEFAULT_UBI_REPO "
            "in your environment"
        )

        with pytest.raises(ubi.LoaderError) as exc:
            ubi.get_loader()

        assert str(exc.value) == expected_error

    finally:
        ubi.DEFAULT_UBI_REPO = "https://contentdelivery.com/ubi/data"


@patch("requests.Session")
def test_get_empty_branches(mocked_session):
    mocked_session.return_value.request.return_value.json.return_value = {}
    exception = RuntimeError(
        ("Please check https://contentdelivery.com/ubi/data " "is in right format")
    )
    try:
        ubi.get_loader()
        raise AssertionError("test should fail!")
    except RuntimeError as actual_exception:
        assert actual_exception.args == exception.args


@patch("requests.Session")
def test_get_branches(mocked_session, branches):
    remote_branches = [
        {"name": "ubi7", "commit": {"id": "c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f"}},
        {
            "name": "ubi7.1",
            "commit": {"id": "2189cbc2e447f796fe354f8d784d76b0a2620248"},
        },
        {"name": "ubi8", "commit": {"id": "26d24af7859df3c4d361bd33cd57984d03abe206"}},
    ]
    headers = {"Content-Length": "629", "X-Total-Pages": "1", "X-Per-Page": "20"}
    mocked_session.return_value.request.return_value.headers = headers
    mocked_session.return_value.request.return_value.json.return_value = remote_branches
    loader = ubi.get_loader()
    actual_branches_sha1 = loader._get_branches()
    assert actual_branches_sha1 == branches


@patch("requests.Session")
@patch("ubiconfig._impl.loaders._GitlabLoader._get_branches")
def test_pre_load(mocked_get_branches, mocked_session, files_branch_map):
    branch_sha1 = OrderedDict(
        [
            ("ubi7.1", "2189cbc2e447f796fe354f8d784d76b0a2620248"),
            ("ubi7", "c99cb8d7dae2e78e8cc7e720d3f950d1c5a0b51f"),
            ("ubi8", "26d24af7859df3c4d361bd33cd57984d03abe206"),
        ]
    )
    mocked_get_branches.return_value = branch_sha1
    headers = {"Content-Length": "629", "X-Total-Pages": "1", "X-Per-Page": "20"}
    mocked_session.return_value.request.return_value.headers = headers
    file_list = [
        [
            {"name": "rhel-7-server.yaml", "path": "rhel-7-server.yaml"},
            {"name": "rhel-atomic-host.yaml", "path": "rhel-atomic-host.yaml"},
            {"name": "README.md", "path": "README.md"},
        ],
        [{"name": "rhel-7-server.yaml", "path": "rhel-7-server.yaml"}],
        [{"name": "rhel-8-for-power-le.yaml", "path": "rhel-8-for-power-le.yaml"}],
    ]
    mocked_session.return_value.request.return_value.json.side_effect = file_list
    loader = ubi.get_loader()
    expected_map = files_branch_map
    actual_files_branch_map = loader._files_branch_map
    assert expected_map == actual_files_branch_map


def test_ubi_config(ubi7_1_config_file1):
    config_dict = yaml.safe_load(ubi7_1_config_file1)
    config = UbiConfig.load_from_dict(config_dict, "rhel-atomic-host.yaml", "7.1")
    assert config.modules[0].name == "nodejs"
    assert config.content_sets.rpm.input == "rhel-atomic-host-rpms"
    assert str(config.packages.blacklist[0]) == "<Package: kernel*>"
    assert config.version == "7.1"
    assert config.flags.base_pkgs_only.value is False
