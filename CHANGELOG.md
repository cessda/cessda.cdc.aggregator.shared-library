# Changelog

All notable changes to the CDC Aggregator Shared Library will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [0.10.0] - 2025-05-09

### Added

- Support reading DDI 3.2 from OAI-PMH metadata. (Implements
  [#50](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/50))

### Changed

- Require Kuha Common 2.7.0 in requirements.txt and setup.py.
- DDI 3.3 mapping: add primary lookup XPATH
  `/ddi:DDIInstance/s:StudyUnit/r:UserID` for `Study.identifiers` when
  `@typeOfUserID` attribute is "StudyNumber". If this is found, all
  other lookup locations are skipped. If this is not found or
  `@typeOfUserID` is not "StudyNumber", then the old behaviour
  applies. (Implements
  [#52](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/52))
- DDI 3.3 mapping: add primary lookup XPATH
  `/ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/r:Description/r:Content`
  for `Study.data_access`. If this is found, all other lookup
  locations are skipped. If this is not found, then the old behaviour
  applies. (Implements
  [#53](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/53))
- DDI 3.3 mapping: add primary lookup XPATH
  `/ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/a:TypeOfAccess`
  for `Study.data_access_descriptions`, and use its
  `@controlledVocabularyName` attributes value for
  `Study.data_access_descriptions.attr_element_version`. If this is
  found, all other lookup locations are skipped. If this is not found,
  the old behaviour applies. (Implements
  [#54](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/54))


## [0.9.0] - 2024-12-19

### Added

- Support more DDI-C elements. (Implements
  [#48](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/48))
  - Add `Study.distribution_dates` with `description` attribute.
  - Add `Study.research_instruments` with `system_name`, `uri` and
    `description` attributes.
  - Add `element_version` attribute to `Study.data_access_descriptions`.
  - Add `description` attribute to `Study.collection_periods`.
  - Map DDI-C `/codeBook/stdyDscr/citation/distStmt/distDate` to
    `Study.distribution_dates`.
  - Map DDI-C `/codeBook/stdyDscr/method/dataColl/resInstru` to
    `Study.research_instruments`.
  - Map DDI-C
    `/codeBook/stdyDscr/dataAccs/useStmt/conditions/@elementVersion`
    to `Study.data_access_descriptions.attr_element_version`.
  - Map DDI-C `/codeBook/stdyDscr/stdyInfo/sumDscr/collDate` CDATA to
    `Study.collection_periods.attr_description`.

### Changed

- Require Kuha Common 2.6.0 in requirements.txt.
- Require Tornado 6.4.2 in requirements.txt


## [0.8.1] - 2024-08-29

### Added

- New test environment for tox 'warnings-as-errors' to treat warnings
  as errors in tests. Run this environment in CI with latest python.

### Fixed

- Fixed DeprecationWarnings in mappings.py module.


## [0.8.0] - 2024-08-29

### Added

- Support Python 3.11 & 3.12.

### Changed

- Require Kuha Common 2.5.0 in requirements.txt.
- Require Py12fLogging 0.7.0 in requirements.txt.
- Require Tornado 6.4.1 in requirements.txt.
- Require ConfigArgParse 1.7 in requirements.txt.

### Removed

- Support for Python 3.6 & 3.7.


## [0.7.0] - 2024-04-30

### Added

- Add `external_link`, `external_link_role`, `external_link_uri` and
  `external_link_title` attributes to `Study.principal_investigators`.
- Map DDI-C `/codeBook/stdyDscr/citation/rspStmt/AuthEnty/ExtLink`
  values and attributes to `Study.principal_investigators`.

### Changed

- Require Kuha Common 2.4.0 in requirements.txt and setup.py.
- Change Kuha Common source url in requirements.txt (Implements
  [#41](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/41))


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
  [#33](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/33))
- Support for Related Publication identifiers. (Implements
  [#33](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/33))


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
  the result. (Implements [#27](https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/27))
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
