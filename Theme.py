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
