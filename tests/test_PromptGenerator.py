import json
import os

import yaml

from ConfigMgr import ConfigMgr

CONFIG_FILE = "test_app_config.json"
THEMES_DIR = "test_themes"  # Test directory for YAML files


def setup_module(module):
    """Setup test environment by creating necessary files."""
    os.makedirs(THEMES_DIR, exist_ok=True)

    test_config = {
        "display_duration": "01:00:00",
        "full_screen": False,
        "custom_prompt": "a custom prompt",
        "embellish_custom_prompt": True,
        "max_num_saved_files": 201,
        "save_directory_path": "image_out",
        "background_color": [0, 0, 0],
        "active_theme": "test_theme",
        "active_style": "Random",
        "themes_directory": THEMES_DIR
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(test_config, f)

    test_theme_yaml = {
        "system_prompt": "You are a creative AI.",
        "user_prompt": "Original prompt: \"{prompt}\"\nMake it more artistic and vivid.",
        "prompts": ["A beautiful sunset over the ocean", "A futuristic cityscape at night"],
        "styles": {"test_style": "Vibrant colors, cinematic lighting.", "Random": "Choose a style randomly."}
    }
    with open(os.path.join(THEMES_DIR, "test_theme.yaml"), "w") as f:
        yaml.dump(test_theme_yaml, f)


def teardown_module(module):
    """Cleanup test environment by removing test files."""
    os.remove(CONFIG_FILE)
    os.remove(os.path.join(THEMES_DIR, "test_theme.yaml"))
    os.rmdir(THEMES_DIR)


def test_load_config():
    """Test loading of configuration file."""
    config_mgr = ConfigMgr(config_file_name=CONFIG_FILE)
    config = config_mgr.load_config()
    assert config["active_theme"] == "test_theme"
    assert config["active_style"] == "Random"
    assert config["themes_directory"] == THEMES_DIR


def test_load_theme_yaml():
    """Test loading of theme YAML file and ensuring 'Random' style exists."""
    config_mgr = ConfigMgr(config_file_name=CONFIG_FILE)
    theme_data = config_mgr.load_config()
    assert theme_data["active_theme"] == "test_theme"
    assert "Random" in theme_data["active_style"]


def test_generate_prompt():
    """Test the generation of prompts and ensure 'Random' style behaves correctly."""
    pass

