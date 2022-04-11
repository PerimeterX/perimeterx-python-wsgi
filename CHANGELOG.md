# Change Log

## [v3.3.0](https://github.com/PerimeterX/perimeterx-python-wsgi) (2022-04-11)
- Changed to new version of block page
- Configurable max buffer length
- Configurable px_backend_url
- Sending activities at the end of request cycle rather than beginning of the next one
- Removed problematic fields in Risk API request

## [v3.2.1](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-08-22)
- Upgrade dependency for security issue.

## [v3.2.0](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-03-17)
- Added support for enforced_specific_routes
- Added .json to the list of whitelisted extensions

## [v3.1.0](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-02-26)
- Refactor of px_logger to use native python logger
- Added support for bypass monitor mode header

## [v3.0.2](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-02-13)
- page requested pass_reason alignment
- better error handling for http errors
- better module_version reporting

## [v3.0.1](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-02-04)
- Monitor mode bug fix
- Better error handling

## [v3.0.0](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-01-28)
- Added GAE support
- Added PXHD support
- Updated VID source handling

## [v2.3.2](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-01-13)
- Changed requirements setting

## [v2.3.1](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-01-10)
- Changed requirements setting

## [v2.3.0](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-01-09)
- Added disabling of the request validation by property
- Minor bug fix

## [v2.2.1](https://github.com/PerimeterX/perimeterx-python-wsgi) (2019-01-03)
- Added async custom params
- Added dynamic module enabling/disabling
- Small performance boost
- Major refactoring 

## [v2.1.0](https://github.com/PerimeterX/perimeterx-python-wsgi) (2018-12-20)
- Added data enrichment
- Fixed mobile catpcha release
- Added an option to programmatically enable and disable the module
- Async custom params
- Fixed performance issues
- Major refactoring

## [v2.0.2](https://github.com/PerimeterX/perimeterx-python-wsgi) (2018-12-05)
- Fixed copying resources to package on pypi.

## [v2.0.0](https://github.com/PerimeterX/perimeterx-python-wsgi/compare/v1.0.17...HEAD) (2018-12-03)
- Added Major Enforcer functionalities: Mobile SDK, FirstParty, CaptchaV2, Block handling
- Added unit tests

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.2.0] - 2017-04-18
### Added
- Added UUID to page requested
- New block/captcha templates
- Delete captcha cookie after evaluation
- Sending original cookie value when decryption fails
