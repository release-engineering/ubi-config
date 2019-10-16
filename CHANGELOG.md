# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
