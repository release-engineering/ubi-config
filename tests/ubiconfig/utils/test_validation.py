import os

import yaml
import pytest

from jsonschema.exceptions import ValidationError
from ubiconfig.utils import config_validation

TEST_DATA = os.path.join(os.path.dirname(__file__),
                         '../../data/configs/dnf7/rhel-atomic-host.yaml')


@pytest.fixture
def dnf7_config():
    with open(TEST_DATA) as f:
        config = yaml.safe_load(f)
    return config


def test_validate_data_pass(dnf7_config):
    assert config_validation.validate_config(dnf7_config) is None


def test_validate_data_pass_without_module(dnf7_config):
    dnf7_config.pop('modules')
    assert config_validation.validate_config(dnf7_config) is None


def test_validate_failed_missing_content_sets(dnf7_config):
    dnf7_config.pop('content_sets')
    with pytest.raises(ValidationError):
        config_validation.validate_config(dnf7_config)


def test_validate_failed_extra_keyword(dnf7_config):
    dnf7_config.update({'extra': 'something should not exist'})
    with pytest.raises(ValidationError):
        config_validation.validate_config(dnf7_config)


def test_validate_failed_missing_package_include(dnf7_config):
    dnf7_config['packages'].pop('include')
    with pytest.raises(ValidationError):
        config_validation.validate_config(dnf7_config)


def test_validate_failed_wrong_data_type(dnf7_config):
    dnf7_config['packages']['include'] = 'A string'
    with pytest.raises(ValidationError):
        config_validation.validate_config(dnf7_config)
