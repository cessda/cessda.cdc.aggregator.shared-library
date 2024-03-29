# Changelog

All notable changes to the CDC Aggregator Shared Library will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [0.6.0] - 2023-11-24

### Changed

- Alter RecordBase schema: add `_direct_base_url` attribute. (Implements
  [#39](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/39))
- Map source records direct base url to `study._direct_base_url`. (Implements
  [#39](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/39))


## [0.5.0] - 2022-11-18

### Changed

- Require Kuha Common >= 2.0.1 in setup.py.
- Update dependency Kuha Common to 2.0.1 in requirements.txt.
- Update dependency Tornado to 6.2.0 in requirements.txt.

### Added

- Support for Funding information. (Implements
  [#33](https://bitbucket.org/cessda/cessda.cdc.aggregator.shared-library/issues/33))
- Support for Related Publication identifiers. (Implements
  [#33](https://bitbucket.org/cessda/cessda.cdc.aggregator.shared-library/issues/33))


## [0.4.0] - 2022-06-29

### Changed

- Update dependency Kuha Common to 1.1.0 in requirements.txt.
- Require Kuha Common >= 1.1.0 in setup.py.

### Added

- Mapping study-level metadata from DDI 3.3 format to internal data
  model.


## [0.3.0] - 2022-05-18
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6577777.svg)](https://doi.org/10.5281/zenodo.6577777)

**Contains backwards incompatible changes.**

### Changed

- The studies generator in `mappings.DynamicAggregatorBase` now assings
  the `study._aggregator_identifier`. The identifier is generated by
  first joining the source OAI-PMH Base URL and OAI Identifier by a
  separator '-', and then generating a sha256 hexadecimal notation of
  the result. (Implements [#27](https://bitbucket.org/cessda/cessda.cdc.aggregator.shared-library/issues/27))
- `Study._aggregator_identifier` can now be set using
  `records.Study.set_aggregator_identifier()`.
- `Study._aggregator_identifier` is no longer generated when creating a new
  Study-object.
- Update dependency of Kuha Common in requirements.txt. Use released
  version 1.0.0.


## [0.2.0] - 2021-12-17
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5779958.svg)](https://doi.org/10.5281/zenodo.5779958)

### Changed

- Update dependencies in requirements.txt.
  - ConfigArgParse 1.5.3
  - Kuha Common commit 8e7de1f16530decc356fee660255b60fcacaea23


## [0.1.0] - 2021-09-21

### Added

Initial codebase.
