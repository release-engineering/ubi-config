import os
import json

from jsonschema import validate

DEFAULT_SCHEMA = os.path.join(os.path.dirname(__file__), "config_schema.json")
""" Default yaml schema used for validation of UbiConfig configuration files """


def validate_config(data, schema=None):
    """Validate the data according to the schema
    If no schema is provided, :data:`DEFAULT_SCHEMA` is used"""
    if schema is None:
        with open(DEFAULT_SCHEMA) as f:
            schema = json.load(f)
    validate(data, schema)
