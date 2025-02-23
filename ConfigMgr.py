import json  # JSON library for configuration handling
import tkinter as tk  # Tkinter for GUI and configuration dialog
import tkinter.messagebox
from pathlib import Path
from typing import Dict, Any


class ConfigMgr:
    DEFAULT_DISPLAY_DURATION: str = "01:00:00"  # every hour

    LOCAL_CONFIG_FILE_NAME: str = "config_local.json"
    FACTORY_CONFIG_FILE_NAME: str = "config_factory.json"

    def __init__(self, config_file_name: str = LOCAL_CONFIG_FILE_NAME):
        self.config_file_path: Path = Path(config_file_name)
        self._config_cache: Dict[str, Any] = {}
        self._last_read_time: float = 0.0  # Stores last read timestamp

    def _is_config_modified(self) -> bool:
        """Check if the config file has been modified since the last read."""
        if not self.config_file_path.exists():
            return True  # If the file doesn't exist, treat it as modified

        last_modified = self.config_file_path.stat().st_mtime
        b = (last_modified - self._last_read_time) > 0.5
        return b

    def read_factory_config(self) -> dict:
        """
        Read the factory default file.
        """
        factory_config_file_path: Path = Path(self.FACTORY_CONFIG_FILE_NAME)
        with factory_config_file_path.open("r", encoding="utf-8") as file:
            the_data = json.load(file)
            loaded_config = {**the_data}
        return loaded_config

    def reset_to_factory_defaults(self):
        fconfig = self.read_factory_config()
        self.save_config(fconfig)

    def load_config(self) -> dict:
        """
        Load the app's configuration.
        - read in the config_factory.json default file
        - if config_local.json doesn't exist, write it using config_factory.json
        - read in the config_local.json file
            - merge in any new values found in config_factory.json
        - write the config_local.json file
        - ensure themes and image_out directories exist
        :return: a dictionary containing the configuration data
        """
        if self._config_cache and not self._is_config_modified():
            # we'll just use the cached version, then, shall we?
            return self._config_cache

        default_config = self.read_factory_config()

        # Write the config file if one does not exist
        if not self.config_file_path.exists():
            with self.config_file_path.open("w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4)  # type: ignore
                print(f"New config file written to: {self.config_file_path}")

        # Read in the config_local.json file.
        # Merge with default values to include any new items
        with self.config_file_path.open("r", encoding="utf-8") as file:
            the_data = json.load(file)
            loaded_config = {**default_config, **the_data}
            print(f"Full Read of config_local.json: {loaded_config}")
            self._config_cache = loaded_config
            self._last_read_time = self.config_file_path.stat().st_mtime

        self.validate_config_values(config_dict=loaded_config)

        # Write the file to ensure all new data is on file,
        # will update the cached version & last-read-date
        self.save_config(config=loaded_config)

        # Ensure themes directory exists
        themes_dir = Path(loaded_config["themes_directory"])
        if not themes_dir.exists():
            themes_dir.mkdir(parents=True, exist_ok=True)

        # Ensure save directory exists
        save_dir = Path(loaded_config["save_directory_path"])
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)

        print("Loaded config:\n" + json.dumps(loaded_config, indent=4))

        return loaded_config

    def save_config(self, config: Dict[str, Any]):
        """
        Saves the current configuration to the config_local.json file.
        This will remember when it was written.
        """
        with self.config_file_path.open("w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)  # type: ignore
        self._config_cache = config
        self._last_read_time = self.config_file_path.stat().st_mtime

    def validate_time_string(self, time_str: str) -> bool:
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            return 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59
        except ValueError:
            return False

    def validate_config_values(self, config_dict: Dict[str, Any]) -> None:
        """Validate configuration values; will raise exception if not valid."""
        errors = []

        duration_str: str = config_dict["display_duration"]
        if not self.validate_time_string(duration_str):
            errors.append(f"Invalid duration: '{duration_str}'. Use HH:MM:SS format")

        # Validate RGB values
        if len(config_dict['background_color']) != 7 or not config_dict['background_color'].startswith("#"):
            errors.append(f"Background be a hex color value (e.g. '#a1beef') Found: '{config_dict['background_color']}'")

        # Validate max files
        if config_dict["max_num_saved_files"] <= 0:
            errors.append("Maximum saved files must be greater than 0")

        # Validate save directory
        save_dir = Path(config_dict["save_directory_path"])
        if not save_dir.exists() or not save_dir.is_dir():
            errors.append("Save directory must be a valid directory path")

        # Validate active theme
        if not isinstance(config_dict["active_theme"], str) or not config_dict["active_theme"].strip():
            errors.append("Active theme must be a non-empty string.")

        # Validate active style
        if not isinstance(config_dict["active_style"], str) or not config_dict["active_style"].strip():
            errors.append("Active style must be a non-empty string.")

        # Validate themes directory
        themes_dir = Path(config_dict["themes_directory"])
        if not themes_dir.exists() or not themes_dir.is_dir():
            errors.append("Themes directory must be a valid directory path")

        if errors:
            raise ValueError("\n".join(errors))
