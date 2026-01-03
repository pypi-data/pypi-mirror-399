# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2025-12-12

### Added
- **Vidai Rename**: Complete rebranding from `WizzClient` to `Vidai`.
- **Examples**:
    - `examples/simple/`: Feature-focused examples (Streaming, Structured Output, Tools).
    - `examples/providers/`: Configuration examples for OpenAI, Anthropic, Gemini, DeepSeek, Vidai Server.
- **Verification**: New regression test suite located in `tests/regression/`.
- **Makefile**: Added `verify-all`, `test-regression`, `test-responses`, `test-proxy` targets.
- **Responses API**: Full object parity and polyfill support for `client.responses.create`.

### Changed
- Refactored `examples/` directory to separate legitimate usage examples from regression tests.
- Updated `pyproject.toml` metadata.
- Updated documentation (`docs/`) to reflect new branding and features.
- Cleaned up legacy code references.

### Fixed
- Fixed double-transformation bug in `client.py` for structured output.
- Fixed Gemini provider handling of `None` titles in schemas.
- Fixed 401/404 error handling robustness in regression suites.
