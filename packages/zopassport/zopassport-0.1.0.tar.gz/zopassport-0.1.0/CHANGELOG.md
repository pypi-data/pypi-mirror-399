# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive exception hierarchy for better error handling
- Encrypted file storage adapter with password and key-based encryption
- Automatic token refresh with configurable intervals
- HTTP retry logic with exponential backoff
- Rate limit detection and handling
- Enhanced logging system with configurable levels
- Type hints throughout the codebase
- Comprehensive test suite (unit, integration, e2e)
- CI/CD pipeline with GitHub Actions
- Security audit and best practices documentation
- Complete API documentation

### Changed
- Refactored all modules to use specific exception types
- Improved error messages with contextual details
- Enhanced storage adapters with better error handling
- Updated configuration options for retry and timeout settings

### Fixed
- Token refresh logic now properly handles expiry times
- Storage operations now properly handle file I/O errors
- Network errors now include proper retry logic

## [0.1.0] - 2025-01-01

### Added
- Initial release
- Phone-based OTP authentication
- Session persistence with file storage
- User profile management
- Avatar generation and polling
- Wallet balance and transaction support
- Support for Base and Avalanche networks

[Unreleased]: https://github.com/ZoHouse/zopassport/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ZoHouse/zopassport/releases/tag/v0.1.0
