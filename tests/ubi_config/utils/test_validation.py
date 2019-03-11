import os
import pytest

import yaml

from ubi_config.utils import config_validation

TEST_DATA = os.path.join(os.path.dirname(__file__),
						 '../../data/configs/dnf7/rhel-atomic-host.yaml')

def test_validate_data():
	with open(TEST_DATA) as f:
		config = yaml.safe_load(f)
	assert config_validation.validate_config(config) == None
