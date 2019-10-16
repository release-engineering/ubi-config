from .gitlab import GitlabLoader as _GitlabLoader
from .local import LocalLoader as _LocalLoader

__all__ = ["_GitlabLoader", "_LocalLoader"]
