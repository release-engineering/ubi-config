from pytest import raises

from ubiconfig import Loader


def test_no_load():
    """load must be implemented in subclass"""
    with raises(NotImplementedError):
        Loader().load("something.yaml")


def test_no_load_all():
    """load_all must be implemented in subclass"""
    with raises(NotImplementedError):
        Loader().load_all()
