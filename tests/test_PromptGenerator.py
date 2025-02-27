import json
import os
from pathlib import Path

import pytest

from ConfigMgr import ConfigMgr
from PromptGenerator import PromptGenerator

CONFIG_FILE_NAME = "test_app_config.json"
TEST_THEMES_DIR_NAME = "test_themes"  # Test directory for YAML files
TEST_THEME_FILE_NAME = "default.yaml"


@pytest.fixture
def config_mgr():
    config_file_path: Path = Path(CONFIG_FILE_NAME)
    if os.path.exists(config_file_path):
        os.remove(config_file_path)
    config_data = {
        "display_duration": "01:00:00",
        "full_screen": True,
        "max_num_saved_files": 200,
        "minimum_rating": 1.4,
        "save_directory_path": "image_out",
        "background_color": "#334455",
        "active_theme": "creative",
        "active_style": "realistic",
        "themes_directory": TEST_THEMES_DIR_NAME
    }
    # write the data and use it in creating a new ConfigMgr
    with config_file_path.open("w", encoding="utf-8") as file:
        json.dump(config_data, file, indent=4)  # type: ignore
    config_mgr = ConfigMgr(CONFIG_FILE_NAME)

    # go to town
    yield config_mgr

    # cleanup
    if os.path.exists(config_file_path):
        os.remove(config_file_path)


def test_generate_simple_prompt(config_mgr):
    """Test the generation of prompts"""
    config =config_mgr.load_config()
    config["active_style"]="realistic"
    config_mgr.save_config(config)
    prompt_generator = PromptGenerator(config_mgr)
    result = prompt_generator.generate_prompt()
    print("result: {}".format(result))
    full_prompt = result[PromptGenerator.FULL_PROMPT]
    system_prompt = result[PromptGenerator.SYSTEM_PROMPT]
    # see that basic prompt is in there
    assert "floating islands" in full_prompt or "futuristic city" in full_prompt
    # see that user_prompt embellishment is in there
    assert "more detailed" in full_prompt
    assert "photorealistic" in full_prompt
    assert "highly imaginative AI" in system_prompt

def test_generate_random_prompt(config_mgr):
    """Test the generation of prompts and ensure 'random' style behaves correctly."""
    config =config_mgr.load_config()
    config["active_style"]="random"
    config_mgr.save_config(config)

    styles = set()
    # run it a bunch and ensure that the "random" style is
    # picking up different styles in the remaining set of styles
    for _ in range(25):
        prompt_generator = PromptGenerator(config_mgr)
        result = prompt_generator.generate_prompt()
        full_prompt = result[PromptGenerator.FULL_PROMPT]
        style_part = full_prompt.split("use the following style: ")[1]  # Returns remainder of string
        styles.add(style_part)
    print(f"{len(styles)} distinct styles found")
    assert len(styles) == 3  # 4 styles in file minus "random" style
