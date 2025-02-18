import random

from ConfigMgr import ConfigMgr
from Theme import Theme
from ThemeMgr import ThemeMgr


class PromptGenerator:
    FULL_PROMPT = 'full_prompt'
    SYSTEM_PROMPT = 'system_prompt'

    def __init__(self, config_mgr: ConfigMgr) -> None:
        self.config_mgr = config_mgr
        self.config = self.config_mgr.load_config()
        self.theme_mgr = ThemeMgr(self.config["themes_directory"])

    def generate_prompt(self) -> dict[str, str]:
        """
        Generate a themed prompt based on theme chosen in the config file.
        Returns: dictionary of prompt data; keys are "full_prompt", and "system_prompt"
        """
        self.config = self.config_mgr.load_config()
        active_theme_name = self.config["active_theme"]
        theme_data: Theme = self.theme_mgr.get_theme(active_theme_name)

        system_prompt: str = theme_data.system_prompt
        user_prompt_template: str = theme_data.user_prompt

        # pick a base prompt out of the list
        original_prompt: str = random.choice(theme_data.prompts)

        # select style
        active_style = self.config["active_style"]
        if active_style == "random" or active_style not in theme_data.styles:
            available_styles = [s for s in theme_data.styles if s != "random"]
            style_text: str = random.choice(available_styles)
        else:
            style_text: str = theme_data.styles[active_style]

        # apply user_prompt_template to the base prompt and styles
        full_prompt: str = user_prompt_template.format(prompt=original_prompt)
        full_prompt += f" and use the following style: {style_text}"

        result = {
            self.FULL_PROMPT: full_prompt,
            self.SYSTEM_PROMPT: system_prompt
        }

        return result
