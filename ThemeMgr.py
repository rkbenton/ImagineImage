import os
from typing import List

import yaml
from Theme import Theme


class ThemeMgr:
    """
    Manages Theme objects stored as YAML files in a designated directory.
    """

    def __init__(self, themes_dir: str):
        """
        Initializes ThemeMgr.
        Ensures the themes directory exists and creates a default theme if "default.yaml" is missing.
        """
        self.themes_dir = themes_dir
        os.makedirs(self.themes_dir, exist_ok=True)

        default_theme_path = os.path.join(self.themes_dir, "default.yaml")
        if not os.path.exists(default_theme_path):
            default_theme = Theme(
                disk_name="default.yaml",
                display_name="Default Theme",
                description="A basic default theme.",
                system_prompt="You are a creative AI.",
                user_prompt="Original prompt: \"{prompt}\"\nMake it more artistic and vivid.",
                prompts=["A serene landscape", "A futuristic skyline"],
                styles={"classic": "Muted tones, soft lighting."}
            )
            self.write_theme(default_theme)

    def get_theme_list(self) -> List[str]:
        """
        Returns a list of theme filenames (excluding the .yaml extension) in the themes directory.
        """
        return [f[:-5] for f in os.listdir(self.themes_dir) if f.endswith(".yaml")]

    def get_theme(self, disk_name: str) -> Theme:
        """
        Loads and returns a Theme object from a YAML file in the themes directory.
        """
        if not disk_name.endswith(".yaml"):
            disk_name += ".yaml"
        theme_path = os.path.join(self.themes_dir, f"{disk_name}")
        if not os.path.exists(theme_path):
            raise FileNotFoundError(f"Theme '{disk_name}' not found.")

        with open(theme_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return Theme(**data)

    def write_theme(self, the_theme: Theme) -> None:
        """
        Saves the given Theme object to a YAML file in the themes directory.
        """
        theme_path = os.path.join(self.themes_dir, the_theme.disk_name)
        with open(theme_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(the_theme.__dict__, file)

    def delete_theme(self, disk_name: str) -> None:
        """
        Deletes the specified theme YAML file from the themes directory.
        """
        if not disk_name.endswith(".yaml"):
            disk_name += ".yaml"

        theme_path = os.path.join(self.themes_dir, f"{disk_name}")
        if os.path.exists(theme_path):
            os.remove(theme_path)
        else:
            raise FileNotFoundError(f"Theme '{disk_name}' not found.")
