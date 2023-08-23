import os

import yaml
import pytest

from jsonschema.exceptions import ValidationError
from ubiconfig.utils import config_validation

TEST_DATA = os.path.join(
    os.path.dirname(__file__), "../../data/configs/ubi7.1/rhel-atomic-host.yaml"
)


@pytest.fixture
def ubi7_1_config():
    with open(TEST_DATA) as f:
        config = yaml.safe_load(f)
    return config


def test_validate_data_pass(ubi7_1_config):
    assert config_validation.validate_config(ubi7_1_config) is None


def test_validate_data_pass_without_module(ubi7_1_config):
    ubi7_1_config.pop("modules")
    assert config_validation.validate_config(ubi7_1_config) is None


def test_validate_failed_missing_content_sets(ubi7_1_config):
    ubi7_1_config.pop("content_sets")
    with pytest.raises(ValidationError):
        config_validation.validate_config(ubi7_1_config)


def test_validate_failed_extra_keyword(ubi7_1_config):
    ubi7_1_config.update({"extra": "something should not exist"})
    with pytest.raises(ValidationError):
        config_validation.validate_config(ubi7_1_config)


def test_validate_failed_missing_package_include(ubi7_1_config):
    ubi7_1_config["packages"].pop("include")
    with pytest.raises(ValidationError):
        config_validation.validate_config(ubi7_1_config)


def test_validate_failed_wrong_data_type(ubi7_1_config):
    ubi7_1_config["packages"]["include"] = "A string"
    with pytest.raises(ValidationError):
        config_validation.validate_config(ubi7_1_config)


def test_validate_failed_wrong_data_type_flags(ubi7_1_config):
    ubi7_1_config["flags"]["base_pkgs_only"] = 120
    with pytest.raises(ValidationError):
        config_validation.validate_config(ubi7_1_config)


def test_validate_failed_unsupported_flag(ubi7_1_config):
    ubi7_1_config["flags"] = {"unsupported-flag": True}
    with pytest.raises(ValidationError):
        config_validation.validate_config(ubi7_1_config)
