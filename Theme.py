from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Theme:
    # unique name used for filename
    disk_name: str
    # name used in lists
    display_name: str
    # short and punchy description
    description: str

    system_prompt: str
    user_prompt: str
    prompts: List[str]
    styles: Dict[str, str]


# Example usage
if __name__ == "__main__":
    test_theme = Theme(
        disk_name="foo.yaml",
        display_name="Arbor Day",
        description="All about the Trees!",
        system_prompt="You are a creative AI.",
        user_prompt="Original prompt: \"{prompt}\"\nMake it more artistic and vivid.",
        prompts=[
            "A beautiful sunset over the ocean",
            "A futuristic cityscape at night"
        ],
        styles={
            "test_style": "Vibrant colors, cinematic lighting.",
            "Random": "Choose a style randomly."
        }
    )

    print(test_theme)
