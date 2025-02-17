import json
import yaml
import random
import os
from typing import Dict, Any

CONFIG_FILE: str = "app_config.json"
THEMES_DIR: str = "themes"  # Directory where YAML files are stored


class PromptGenerator:
    def __init__(self, config_file: str = CONFIG_FILE, themes_dir: str = THEMES_DIR) -> None:
        self.config_file = config_file
        self.themes_dir = themes_dir
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load app configuration from JSON file."""
        with open(self.config_file, "r") as f:
            return json.load(f)

    def load_theme_yaml(self, theme_name: str) -> Dict[str, Any]:
        """Load the YAML file for the given theme."""
        theme_file: str = os.path.join(self.themes_dir, f"{theme_name.lower().replace(' ', '_')}.yaml")

        if not os.path.exists(theme_file):
            print(f"Warning: Theme '{theme_name}' not found. Defaulting to 'creative'.")
            return self.load_theme_yaml("creative")

        with open(theme_file, "r") as f:
            theme_data = yaml.safe_load(f)

        # Ensure "Random" is an option in styles
        if "styles" in theme_data and "Random" not in theme_data["styles"]:
            theme_data["styles"]["Random"] = "Choose a style randomly."

        return theme_data

    def generate_prompt(self) -> str:
        """Generate a themed prompt with an optional style."""
        theme_name: str = self.config.get("active_theme", "creative")
        active_style: str = self.config.get("active_style", "Random")

        theme_data: Dict[str, Any] = self.load_theme_yaml(theme_name)

        system_prompt: str = theme_data.get("system_prompt", "")
        user_prompt_template: str = theme_data.get("user_prompt",
                                                   "Original prompt: \"{prompt}\"\nRewrite it to make it more detailed and unique.")

        prompts: list[str] = theme_data.get("prompts", [])
        styles: Dict[str, str] = theme_data.get("styles", {})

        if not prompts:
            print(f"Error: No prompts found for theme '{theme_name}'. Defaulting to 'creative'.")
            theme_data = self.load_theme_yaml("creative")
            prompts = theme_data.get("prompts", [])
            styles = theme_data.get("styles", {})

        prompt: str = random.choice(prompts)

        # Select style
        if active_style == "Random" or active_style not in styles:
            available_styles = [s for s in styles if s != "Random"]
            style_text: str = styles[random.choice(available_styles)] if available_styles else ""
        else:
            style_text: str = styles[active_style]

        final_prompt: str = f"{prompt} {style_text}"
        formatted_user_prompt: str = user_prompt_template.format(prompt=final_prompt)

        return f"{system_prompt}\n{formatted_user_prompt}" if system_prompt else formatted_user_prompt


if __name__ == "__main__":
    generator = PromptGenerator()
    print(generator.generate_prompt())
    print("done")
