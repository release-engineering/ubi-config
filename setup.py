from setuptools import find_packages, setup


def get_long_description():
    with open("README.md") as f:
        return f.read()


def get_requirements():
    with open("requirements.in") as f:
        return f.read().splitlines()


setup(
    name="ubi-config",
    version="3.2.2",
    description="A Python Library for accessing Universal Base Image configuration",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="https://github.com/release-engineering/ubi-config",
    license="GPL-3.0-or-later",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "ubiconfig": ["utils/config_schema.json"],
    },
    python_requires=">=3.6",
    install_requires=get_requirements(),
)
