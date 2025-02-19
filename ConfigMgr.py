import json  # JSON library for configuration handling
from pathlib import Path
import tkinter as tk  # Tkinter for GUI and configuration dialog
import tkinter.messagebox


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
            "max_num_saved_files": 250,  # per directory
            "save_directory_path": "image_out",
            "background_color": [0, 0, 0],
            "active_theme": ConfigMgr.DEFAULT_THEME_NAME,
            "active_style": ConfigMgr.DEFAULT_STYLE_NAME,
            "themes_directory": ConfigMgr.DEFAULT_THEMES_DIR_NAME,
        }

        # Write the config file if one does not exist
        if not self.config_file_path.exists():
            with self.config_file_path.open("w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4)  # type: ignore

        # Merge with default values to include missing keys
        with self.config_file_path.open("r", encoding="utf-8") as file:
            the_data = json.load(file)
            loaded_config = {**default_config, **the_data}

        # Write the file to ensure all new data is on file
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

    def show_options_dialog(self, config):
        dialog = tk.Toplevel()
        dialog.title("Options")
        dialog.geometry("600x500")
        dialog.grab_set()

        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Duration (HH:MM:SS format)
        tk.Label(main_frame, text="Display Duration (HH:MM:SS):").pack(anchor=tk.W)
        duration_var = tk.StringVar(value=config.get("display_duration", self.DEFAULT_DISPLAY_DURATION))
        duration_entry = tk.Entry(main_frame, textvariable=duration_var)
        duration_entry.pack(fill=tk.X)

        # Fullscreen
        fullscreen_var = tk.BooleanVar(value=config["full_screen"])
        tk.Checkbutton(main_frame, text="Full Screen", variable=fullscreen_var).pack(anchor=tk.W)
        # Custom Prompt
        tk.Label(main_frame, text="Custom Prompt:").pack(anchor=tk.W)
        prompt_var = tk.StringVar(value=config["custom_prompt"])
        tk.Entry(main_frame, textvariable=prompt_var).pack(fill=tk.X)

        # Embellish Prompt
        embellish_var = tk.BooleanVar(value=config["embellish_custom_prompt"])
        tk.Checkbutton(main_frame, text="Embellish Custom Prompt", variable=embellish_var).pack(anchor=tk.W)

        # Max Files
        tk.Label(main_frame, text="Maximum Saved Files:").pack(anchor=tk.W)
        max_files_var = tk.StringVar(value=str(config["max_num_saved_files"]))
        tk.Entry(main_frame, textvariable=max_files_var).pack(fill=tk.X)

        # Save Directory
        tk.Label(main_frame, text="Save Directory:").pack(anchor=tk.W)
        save_dir_var = tk.StringVar(value=config["save_directory_path"])
        dir_frame = tk.Frame(main_frame)
        dir_frame.pack(fill=tk.X)
        tk.Entry(dir_frame, textvariable=save_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(dir_frame, text="Browse", command=lambda: save_dir_var.set(
            tk.filedialog.askdirectory(initialdir=save_dir_var.get())
        )).pack(side=tk.RIGHT)

        # Background Color
        tk.Label(main_frame, text="Background Color (R,G,B):").pack(anchor=tk.W)
        color_frame = tk.Frame(main_frame)
        color_frame.pack(fill=tk.X)
        color_vars = []
        for i, val in enumerate(config["background_color"]):
            var = tk.StringVar(value=str(val))
            color_vars.append(var)
            tk.Entry(color_frame, textvariable=var, width=5).pack(side=tk.LEFT, padx=2)

        def save_changes():
            try:
                new_config = {
                    "display_duration": duration_var.get(),
                    "full_screen": fullscreen_var.get(),
                    "custom_prompt": prompt_var.get(),
                    "embellish_custom_prompt": embellish_var.get(),
                    "max_num_saved_files": int(max_files_var.get()),
                    "save_directory_path": save_dir_var.get(),
                    "background_color": [int(v.get()) for v in color_vars]
                }

                self.validate_config_values(new_config)
                config.update(new_config)
                print("Config updated successfully.")  # Debugging
            except ValueError as e:
                tk.messagebox.showerror("Error", f"Invalid input: {str(e)}")

            print("Closing dialog...")  # Debugging
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        tk.Button(button_frame, text="OK", command=save_changes).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

        dialog.wait_window()
        return config
