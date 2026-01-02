# Changelog

All notable changes to the Graedin Cline SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-20

### Added
- Initial release of Graedin Cline Python SDK
- Synchronous client (`GraedinClient`) with full feature support
- Asynchronous client (`AsyncGraedinClient`) with full feature support
- Automatic retry logic with exponential backoff
- Fail-secure mode for production safety
- Comprehensive type hints throughout
- Custom exception types for better error handling
- Support for Python 3.8+
- Full test coverage with pytest
- Usage examples for common scenarios
- LangChain integration example
- Comprehensive documentation

### Features
- `check_prompt()` method for prompt security validation
- `health_check()` method for API health status
- Context manager support for both sync and async clients
- Configurable timeout and retry behavior
- Optional metadata support for auditing
- Request/response models with Pydantic validation

[1.0.0]: https://github.com/jdpahl122/graedin-cline/releases/tag/sdk-v1.0.0

