import json  # JSON library for configuration handling
import tkinter as tk  # Tkinter for GUI and configuration dialog
import tkinter.messagebox
from pathlib import Path

DEFAULT_DISPLAY_DURATION = "00:00:05"  # 5 seconds


class ConfigMgr:

    def __init__(self, config_file_path: Path = Path("app_config.json")):
        self.config_file_path = config_file_path

    def validate_time_string(self, time_str: str):
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            if 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59:
                return True
        except:
            return False
        return False

    def load_config(self):
        """
        Loads configuration settings from a JSON file. If the file does not exist, creates it with default values.
        """
        default_config = {
            "display_duration": DEFAULT_DISPLAY_DURATION,
            "full_screen": True,
            "custom_prompt": "",
            "embellish_custom_prompt": True,
            "max_num_saved_files": 200,
            "save_directory_path": "image_out",
            "background_color": [0, 0, 0]
        }

        if not self.config_file_path.exists():
            with self.config_file_path.open("w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4)  # type: ignore

        with self.config_file_path.open("r", encoding="utf-8") as file:
            # merge to include any values missing from the file
            the_data = json.load(file)
            config = default_config | the_data

        # create the output directory if it doesn't exist yet
        image_dir = Path(config["save_directory_path"])
        if not image_dir.exists():
            image_dir.mkdir(parents=True, exist_ok=True)

        print("Loaded config:\n" + json.dumps(config, indent=4))

        return config

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
        if 3 != len(config_dict['background_color']):
            errors.append(f"there should be 3 values in background_color, found: '{config_dict['background_color']}'")
        else:
            for color in config_dict["background_color"]:
                try:
                    c = int(color)
                    if not (0 <= color <= 255):
                        errors.append(f"Color value {color} must be between 0 and 255")
                except Exception as e:
                    errors.append(f"Color value {color} must be a number between 0 and 255. {e}")

        # Validate max files
        if config_dict["max_num_saved_files"] <= 0:
            errors.append("Maximum saved files must be greater than 0")

        # Validate save directory
        save_dir = Path(config_dict["save_directory_path"])
        if not save_dir.exists() or not save_dir.is_dir():
            errors.append("Save directory must be a valid directory path")

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
        duration_var = tk.StringVar(value=config.get("display_duration", DEFAULT_DISPLAY_DURATION))
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
