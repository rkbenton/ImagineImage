# Changelog

## [v1.1.0]
### Added
- Implemented dependency injection for prompt and image generators.
- Integrated a new `PromptGenerator`.
- Re-inserted missing options dialog.
- Now retains the most recent theme used for later file-saving operations.
- The `generate_image` function now writes to theme subdirectories.
- Added many more prompts to `independence_day.yaml` and other theme files.
- We now use YAML files to describe themes used to generate image prompts.

### Changed
- Numerous changes to write to S3 theme prefixes (i.e., folders).
- Refactored `ImageGenerator.py` to use the new `PromptGenerator`.
- Refactored `PromptGenerator.py` to improve structure.
- Repurposed the old prompt generator to serve as a fallback.
- Updated unit tests to reflect recent changes.
- Updated `ConfigMgr` significantly.
- Updated `requirements.txt`.
- Removed an unused function.

### Fixed
- Fixed a bug in `parse_display_duration`.

### Removed
- Removed unnecessary `main` function.
- Removed `app_config.json` from `.gitignore`.
