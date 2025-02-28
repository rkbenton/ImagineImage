# Changelog

## [v1.2.0]

## Added

- Added rating functionality
    - First pass at rating functionality (37860cd)
    - Added minimum_rating_filter to config_factory.json model (ab88a8f)
    - Added RatingManager.py (789c9ed)
- Added documentation
    - Added RaspiBuildOut.md document (b881d17)
    - Updated ReadMe.md to include rating commands (df6258d)
- Added "Local files only" feature (4f278d7)
- Added logging and config via argparse (9659174)
- Added functions for S3 file handling (6b4ba90)
- Added many more prompts to the theme files
- Added git log capture hinting to ReadMe.md (5952a8e)

## Modified

- Configuration system enhancements
    - Renamed config files to be clearer and to begin with "config" (5320fbd)
    - Added `config_local.json` to .gitignore (080aa66)
    - Cleanup of config files (ea1da56)
    - Removed unused custom_prompt from configs (a55f5d0)
    - Updated types and data in app configs (6fc446f)
    - ConfigMgr.py now caches config, will re-load from disk if mod date changes (7185170)
    - ConfigMgr.py now loads default data from factory_config.json (c93fd52)
    - On load, ConfigMgr.py re-writes file, thus including any new values (5ce3757)
    - Now calling validate_config_values (077c2d0)
    - Changes to support active_theme now being a filename (27cf6f6)

## Improved

- UI improvements
    - Improved text rendering (8b73ae8)
    - Replaced cv2 with tkinter (d47a083)
    - Image canvas now uses config's background_color (29bc61b)

## Updated

- S3 integration changes
    - Numerous changes to write to S3 theme prefixes (i.e. folders) (70d1a83)
    - Now retains most recent theme used for later file-saving ops (d61d832)
    - The generate_image function now writes to theme subdirs (7861b80)
- Updated unit tests (d686a6e)
- 
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
