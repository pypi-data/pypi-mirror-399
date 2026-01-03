# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.5.2] - 2025-12-29
### Fixed
- config pydantic sourceline resolution [5dee7196b](https://gitlab.com/unitelabs/cdk/python-cdk/commit/5dee7196b53f471000769a654d8ff253e5a16be9)

## [V0.5.1] - 2025-12-29
### Fixed
- add check for valid cloud_server_endpoint.hostname [63ba71ce1](https://gitlab.com/unitelabs/cdk/python-cdk/commit/63ba71ce1d9cf2f47ce95ee3b3c52c7bd3104000)

## [V0.5.0] - 2025-12-03
### Added
- finalize cicd standardization across unitelabs gitlab org [b1040fd70](https://gitlab.com/unitelabs/cdk/python-cdk/commit/b1040fd70595a63a96c6abc2ea9c283ced758318)
- sila constrants should accept python native types [ab67038e3](https://gitlab.com/unitelabs/cdk/python-cdk/commit/ab67038e3bd95199e1c078eb9bdb0770f27c956b)
- allow create app setting via envvar [73161c6b7](https://gitlab.com/unitelabs/cdk/python-cdk/commit/73161c6b7a6c7446ecef1c3fe08c271840c9a201)

### Fixed
- add pypi package release [8012df196](https://gitlab.com/unitelabs/cdk/python-cdk/commit/8012df196aa421bf414c89640aa30afd390662bf)
- fix config show for optional dataclasses [3a65678e4](https://gitlab.com/unitelabs/cdk/python-cdk/commit/3a65678e40bd3cf040461b69356bfe256f8b88ad)
- ABC SiLA handler resolution [f2c15e6de](https://gitlab.com/unitelabs/cdk/python-cdk/commit/f2c15e6dec8b35839081896419e22db5f00a3406)

## [V0.4.0] - 2025-11-14
### Added
- integrate changelogs [c62e1529d](https://gitlab.com/unitelabs/cdk/python-cdk/commit/c62e1529d0b1270575b829981ef96518efcf5846)
- feat(DEV-19) setup comprehensive configuration system [53a6e4a10](https://gitlab.com/unitelabs/cdk/python-cdk/commit/53a6e4a10ce9fbf09390a81dcd19729a93253d41)
- setup comprehensive configuration system [53a6e4a10](https://gitlab.com/unitelabs/cdk/python-cdk/commit/53a6e4a10ce9fbf09390a81dcd19729a93253d41)
- update sila python [3dd464ba2](https://gitlab.com/unitelabs/cdk/python-cdk/commit/3dd464ba2ac44cef478a8b1e66fcb4bb8c18143d)
- Switch to google based docstrings for sila interface definitions [90f3f25ec](https://gitlab.com/unitelabs/cdk/python-cdk/commit/90f3f25ecd2e640b54568856311357a47c84bd37)
- src/unitelabs/cdk/sila/metadata/metadatum.py:194: Metadatum.intercept(context): Parameter was added as required
- src/unitelabs/cdk/sila/data_types/convert_data_type.py:10: to_sila(responses): Parameter was added as required
- src/unitelabs/cdk/features/core/authorization_service/authorization_service.py:22: AccessToken.intercept(context): Parameter was added as required
- src/unitelabs/cdk/cli/certificate.py:19: generate(config_path): Parameter was added as required
- src/unitelabs/cdk/cli/certificate.py:19: generate(embed): Parameter was added as required
- src/unitelabs/cdk/cli/certificate.py:19: generate(non_interactive): Parameter was added as required
- src/unitelabs/cdk/cli/start.py:17: start(config_path): Parameter was added as required
- src/unitelabs/cdk/cli/dev.py:19: dev(config_path): Parameter was added as required
- src/unitelabs/cdk/cli/dev.py:70: process(config_path): Parameter was added as required
- src/unitelabs/cdk/cli/dev.py:70: process(config): Parameter was added as required

### Changed
- src/unitelabs/cdk/__init__.py:18: __version__: Attribute value was changed: version('unitelabs_cdk') -> version('unitelabs-cdk')
- src/unitelabs/cdk/sila/data_types/any.py:8: Any: Public object points to a different kind of object: attribute -> class
- src/unitelabs/cdk/cli/certificate.py:19: generate(uuid): Positional parameter was moved
- src/unitelabs/cdk/cli/certificate.py:19: generate(host): Positional parameter was moved
- src/unitelabs/cdk/cli/certificate.py:19: generate(target): Positional parameter was moved
- src/unitelabs/cdk/cli/start.py:17: start(verbose): Positional parameter was moved
- src/unitelabs/cdk/cli/dev.py:19: dev(verbose): Positional parameter was moved
- src/unitelabs/cdk/cli/dev.py:70: process(verbose): Positional parameter was moved

### Removed
- src/unitelabs/cdk/__init__.py:0: Config: Public object was removed
- src/unitelabs/cdk/sila/__init__.py:0: IntermediateResponse: Public object was removed
- src/unitelabs/cdk/sila/__init__.py:0: Parameter: Public object was removed
- src/unitelabs/cdk/sila/__init__.py:0: Response: Public object was removed
- src/unitelabs/cdk/sila/utils.py:0: humanize: Public object was removed
- src/unitelabs/cdk/sila/utils.py:0: parse_docs: Public object was removed
- src/unitelabs/cdk/sila/data_types/__init__.py:0: from_sila: Public object was removed
- src/unitelabs/cdk/sila/data_types/convert_data_type.py:10: to_sila(data_type): Parameter was removed
- src/unitelabs/cdk/sila/data_types/convert_data_type.py:10: to_sila(feature): Parameter was removed
- src/unitelabs/cdk/sila/data_types/__init__.py:0: CustomDataType: Public object was removed
- src/unitelabs/cdk/sila/data_types/convert_data_type.py:0: Any: Public object was removed
- src/unitelabs/cdk/sila/data_types/convert_data_type.py:0: from_sila: Public object was removed
- src/unitelabs/cdk/sila/commands/__init__.py:0: <module>: Public object was removed
- src/unitelabs/cdk/features/weighing/weighing_service/weighing_service_base.py:26: WeighingServiceBase.__init__(args): Parameter was removed
- src/unitelabs/cdk/cli/certificate.py:0: config: Public object was removed
- src/unitelabs/cdk/cli/start.py:17: start(tls): Parameter was removed
- src/unitelabs/cdk/cli/start.py:17: start(cert): Parameter was removed
- src/unitelabs/cdk/cli/start.py:17: start(key): Parameter was removed
- src/unitelabs/cdk/cli/start.py:17: start(log_config): Parameter was removed

[Unreleased]: https://gitlab.com/unitelabs/cdk/python-cdk/compare/v0.5.2...HEAD
[v0.5.2]: https://gitlab.com/unitelabs/cdk/python-cdk/compare/v0.5.1...v0.5.2
[V0.5.1]: https://gitlab.com/unitelabs/cdk/python-cdk/compare/v0.5.0...v0.5.1
[V0.5.0]: https://gitlab.com/unitelabs/cdk/python-cdk/compare/v0.4.0...v0.5.0
[V0.4.0]: https://gitlab.com/unitelabs/cdk/python-cdk/compare/v0.3.10...v0.4.0
