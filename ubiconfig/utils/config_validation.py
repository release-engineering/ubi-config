import os
import json

from jsonschema import validate

DEFAULT_SCHEMA = os.path.join(os.path.dirname(__file__), "config_schema.json")


def validate_config(data, schema=None):
    """validate the data according to the schema"""
    if schema is None:
        with open(DEFAULT_SCHEMA) as f:
            schema = json.load(f)
    validate(data, schema)
