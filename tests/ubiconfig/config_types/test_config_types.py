from ubiconfig.config_types import packages, modules, content_sets


def test_package_with_arch():
    arches = ["i686", "ppc64le"]
    pkg_info = "glibc.i686"
    pkg = packages.Package(pkg_info, arches)
    assert pkg.name == "glibc"
    assert pkg.arch == "i686"


def test_pack_with_dot():
    """This test shows if the package name includes '.', but it's not arch,
    Then the package.arch should be None
    """
    arches = ["i686", "ppc64le"]
    pkg_info = "python2.7"
    pkg = packages.Package(pkg_info, arches)
    assert pkg.name == "python2.7"
    assert pkg.arch is None
    assert repr(pkg) == "<Package: python2.7>"


def test_white_list_package():
    """If it's a whilelist package, then the format <name>*.<arch> is not allowed"""
    pkg_info = "kernel*"
    arches = ["i686", "ppc64le"]
    expected_error = ValueError("<name>*.<arch> is not supported in whitelist")
    try:
        packages.IncludePackage(pkg_info, arches)
        raise AssertionError("It was expected to fail!")
    except ValueError as real_error:
        assert type(real_error) == type(expected_error)
        assert real_error.args == expected_error.args


def test_packages():
    include = ["python2.7", "yum.*"]
    exclude = ["linux-firmware", "kernel*"]
    arches = ["i686", "ppc64le"]
    pkgs = packages.Packages(include, exclude, arches)

    assert pkgs.whitelist[0].name == "python2.7"
    assert pkgs.blacklist[0].name == "linux-firmware"
    assert len(pkgs.whitelist) == 2
    assert len(pkgs.blacklist) == 2


def test_modules():
    data = {
        "include": [
            {"name": "nodejs", "stream": 8, "profiles": ["interpreter"]},
            {"name": "nodejs", "stream": 10},
        ]
    }
    md = modules.Modules.load_from_dict(data)
    assert len(md.whitelist) == 2
    assert md[0].name == "nodejs"
    assert md[0].stream == "8"
    assert md[0].profiles == ["interpreter"]
    assert md[1].stream == "10"
    assert repr(md[1]) == "<Module: nodejs>"


def test_content_sets():
    data = {
        "rpm": {
            "input": "rhel-7-for-power-le-rpms",
            "output": "ubi-7-for-power-le-rpms",
        },
        "srpm": {
            "input": "rhel-7-for-power-le-source-rpms",
            "output": "ubi-7-for-power-le-source-rpms",
        },
        "debuginfo": {
            "input": "rhel-7-for-power-le-debug-rpms",
            "output": "ubi-7-for-power-le-debug-rpms",
        },
    }

    css = content_sets.ContentSetsMapping.load_from_dict(data)

    assert css.rpm.input == "rhel-7-for-power-le-rpms"
    assert css.rpm.output == "ubi-7-for-power-le-rpms"
    assert css.srpm.input == "rhel-7-for-power-le-source-rpms"
    assert css.srpm.output == "ubi-7-for-power-le-source-rpms"
    assert css.debuginfo.input == "rhel-7-for-power-le-debug-rpms"
    assert css.debuginfo.output == "ubi-7-for-power-le-debug-rpms"

    expected_exported_dict = {
        "rpm": ("rhel-7-for-power-le-rpms", "ubi-7-for-power-le-rpms"),
        "srpm": ("rhel-7-for-power-le-source-rpms", "ubi-7-for-power-le-source-rpms"),
        "debuginfo": (
            "rhel-7-for-power-le-debug-rpms",
            "ubi-7-for-power-le-debug-rpms",
        ),
    }
    assert expected_exported_dict == css.export_dict()
