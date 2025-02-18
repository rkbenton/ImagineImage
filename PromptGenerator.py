import os
import random

from ConfigMgr import ConfigMgr
from SimplePromptGenerator import SimplePromptGenerator
from Theme import Theme
from ThemeMgr import ThemeMgr

from openai import OpenAI

class PromptGenerator:
    FULL_PROMPT = 'full_prompt'
    SYSTEM_PROMPT = 'system_prompt'

    def __init__(self, config_mgr: ConfigMgr, api_key:str = None) -> None:
        """
        Initializes the PromptGenerator with configuration and OpenAI API client.
        :param config_mgr: ConfigMgr instance
        :param api_key: OpenAI API key; may be None--usually the case when running
        unit tests.
        """
        self.config_mgr = config_mgr
        self.config = self.config_mgr.load_config()
        self.theme_mgr = ThemeMgr(self.config["themes_directory"])
        if api_key:
            self.api_key = api_key
            self.client = OpenAI(api_key=api_key)
        else:
            self.api_key = None
            self.client = None

    def embellish_prompt(self, user_prompt: str, system_prompt: str):
        """
        Enhances the given user prompt using an AI model (GPT-4o-mini).
        You will typically call generate_prompt() first.
        Note: avoid calling in unit tests unless you mock the actual api.

        Args:
            user_prompt (str): The initial user-provided prompt.
            system_prompt (str): The system message to guide the AI's response.

        Returns:
            str: The AI-generated, embellished prompt.
        """
        try:

            # Send the user and system prompts to the AI model for enhancement
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Specifies the model to use
                messages=[
                    {"role": "system", "content": system_prompt},  # System message for AI guidance
                    {"role": "user", "content": user_prompt}  # The original user-provided prompt
                ],
                temperature=1  # Controls randomness; 1 allows more creative variation
            )

            # Extract and clean up the generated response from the AI
            generated_prompt = response.choices[0].message.content.strip()

        except Exception as e:
            # Handle errors gracefully by logging and falling back to a simpler prompt generator
            print(f"Failed to get prompt from AI: {e} will build one with SimplePromptGenerator")
            simple_generator = SimplePromptGenerator()
            generated_prompt = simple_generator.create_image_prompt().get(PromptGenerator.FULL_PROMPT)

        return generated_prompt  # Return the enhanced or fallback prompt

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
