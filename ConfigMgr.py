import json  # JSON library for configuration handling
from pathlib import Path


class ConfigMgr:
    DEFAULT_DISPLAY_DURATION: str = "01:00:00"  # every hour
    DEFAULT_THEME_NAME: str = "creative"
    DEFAULT_STYLE_NAME: str = "Random"
    DEFAULT_THEMES_DIR_NAME: str = "themes"

    def __init__(self, config_file_name: str = "app_config.json"):
        self.config_file_path: Path = Path(config_file_name)
        print(f"config_path is a {type(config_file_name)}")
        print(f"self.config_file_path is a {type(self.config_file_path)}")

        print(f"ConfigMgr init. File: {config_file_name}")

    def validate_time_string(self, time_str: str) -> bool:
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            return 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59
        except ValueError:
            return False

    def load_config(self):
        """
        Loads configuration settings from a JSON file. If the file does not exist, creates it with default values.
        """
        default_config = {
            "display_duration": ConfigMgr.DEFAULT_DISPLAY_DURATION,
            "full_screen": True,
            "custom_prompt": "",
            "embellish_custom_prompt": True,
            "max_num_saved_files": 200,
            "save_directory_path": "image_out",
            "background_color": [0, 0, 0],
            "active_theme": ConfigMgr.DEFAULT_THEME_NAME,
            "active_style": ConfigMgr.DEFAULT_STYLE_NAME,
            "themes_directory": ConfigMgr.DEFAULT_THEMES_DIR_NAME
        }

        if not self.config_file_path.exists():
            with self.config_file_path.open("w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4)  # type: ignore

        with self.config_file_path.open("r", encoding="utf-8") as file:
            # Merge with default values to include missing keys
            the_data = json.load(file)
            loaded_config = {**default_config, **the_data}

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

    def save_config(self, config):
        """
        Saves the current configuration to the app_config.json file.
        """
        with self.config_file_path.open("w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)  # type: ignore

    def validate_config_values(self, config_dict):
        """Validate configuration values"""
        errors = []

        duration_str: str = config_dict["display_duration"]
        if not self.validate_time_string(duration_str):
            errors.append(f"Invalid duration: '{duration_str}'. Use HH:MM:SS format")

        # Validate RGB values
        if len(config_dict['background_color']) != 3:
            errors.append(f"Background color must have 3 values, found: '{config_dict['background_color']}'")
        else:
            for color in config_dict["background_color"]:
                if not isinstance(color, int) or not (0 <= color <= 255):
                    errors.append(f"Color value {color} must be a number between 0 and 255.")

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


if __name__ == "__main__":
    config_mgr = ConfigMgr()
    config = config_mgr.load_config()

    print("Current Theme:", config["active_theme"])
    print("Current Style:", config["active_style"])
    print("done")
