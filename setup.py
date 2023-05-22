from setuptools import setup, find_packages


def get_description():
    return "A Python Library for accessing Universal Base Image configuration"


def get_long_description():
    with open("README.md") as f:
        text = f.read()

    # Long description is everything after README's initial heading
    idx = text.find("\n\n")
    return text[idx:]


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name="ubi-config",
    version="2.2.0",
    author="",
    author_email="",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"ubiconfig": ["utils/config_schema.json"]},
    url="https://github.com/release-engineering/ubi-config",
    license="GNU General Public License",
    description=get_description(),
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires=get_requirements(),
    python_requires='>=3.6',
    project_urls={"Documentation": "https://release-engineering.github.io/ubi-config/"},
)
