# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- n/a

## [v3.1.0] - 2023-11-10

### Added

- `GitlabLoader` now retries failed requests to GitLab

## [v3.0.0] - 2023-08-29

### Added

- Support for flags in config file

## [v2.3.0] - 2023-08-04

### Added
- `GitlabLoader` is now more generic and supports custom branch names

## [v2.2.0] - 2019-10-24

### Added
- Make ubiconfig.utils.config_validation.validate_config publicly available via
  ubiconfig.validate_config

### Fixed
- Fix LocalLoader couldn't get right version if the argument version of load() is None.

## [v2.1.0] - 2019-10-23

### Fixed
- Fix LocalLoader couldn't populate version field, now it populates the version field
  based on directory name.
- Fix remote loader couldn't load all config files with same name from different branches.
- Make version an option argument to Loader.load(), so it could load right version of
  config file.

## [v2.0.0] - 2019-10-16

### Added
- A new field `version` in UbiConfig class.
- GitlabLoader now populates the `UbiConfig.version` field while loading config.

### Fixed
- LocalLoader couldn't load all config files correctly.

### Changed
- **API break**: `recursive` option is now removed from all loaders. While using
  LocalLoader to load all config files from a directly, it now load all config files
  from its subdirectories automatically.

## [v1.0.2] - 2019-08-07

### Changed
- Fix implicit conversion of data from YAML files
- Limit dependency PyYAML version only when python_version < 2.7
- Fix syntax error in CODEOWNERS file and change code owners
