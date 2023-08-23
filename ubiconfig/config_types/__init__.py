from .modules import Modules
from .packages import Packages
from .content_sets import ContentSetsMapping
from .flags import Flags


class UbiConfig(object):
    """Wrap all UBI related configurations
    Examples to access different configurations:

    Modules:
      config.modules[0].whitelist[0].name
    Packages:
      config.packages.whitelist[0].name
      config.packages.blacklist[0].name
    ContentSets:
      config.content_sets.rpm.input
      config.content_sets.debuginfo.output"""

    def __init__(self, cs, pkgs, mds, file_name, version, flags):
        """
        :param cs: :class:`~ubiconfig.config_types.content_sets.ContentSetsMapping`
        :param pkgs: :class:`~ubiconfig.config_types.packages.Packages`
        :param mds: :class:`~ubiconfig.config_types.modules.Modules`
        :param filename: filename used as identifier
        :param flags: :class:`~ubiconfig.config_types.flags.Flags`
        """
        self.content_sets = cs
        self.packages = pkgs
        self.modules = mds
        self.file_name = file_name
        self.version = version
        self.flags = flags

    def __repr__(self):
        return self.file_name

    @classmethod
    def load_from_dict(cls, data, file_name, version=None):
        """Create new instance of UbiConfig and load it from provided dictonary with
        following format:

        .. code-block:: json

            {
                "modules":  {},
                "packages": {
                    "include": ["package-name-.*"],
                    "exclude": ["package-name-.*"],
                    "arches": ["arch"]
                },
                "content_sets": {},
            }

        See also :meth:`ubiconfig.config_types.content_sets.ContentSetsMapping.load_from_dict`
        :meth:`ubiconfig.config_types.modules.Modules.load_from_dict`
        """
        m_data = Modules.load_from_dict(data.get("modules", {}))
        pkgs = data.get("packages", {})
        pkgs_data = Packages(
            pkgs.get("include", []), pkgs.get("exclude", []), data.get("arches", [])
        )
        cs_map = ContentSetsMapping.load_from_dict(data["content_sets"])

        flags = Flags.load_from_dict(data.get("flags", {}))
        # use the simplified file name
        file_name = file_name.split("/")[-1]

        return cls(
            cs=cs_map,
            pkgs=pkgs_data,
            mds=m_data,
            file_name=file_name,
            version=version,
            flags=flags,
        )
