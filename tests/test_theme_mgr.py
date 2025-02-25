import os

import pytest

from Theme import Theme
from ThemeMgr import ThemeMgr

TEST_THEME_DIR_REL_PATH = 'test_themes'
CONFIG_FILE_NAME = 'test_config.json'

@pytest.fixture
def theme_test_setup():
    # setup
    print(f"Testing {TEST_THEME_DIR_REL_PATH} in {os.getcwd()}")
    assert os.path.exists(TEST_THEME_DIR_REL_PATH)
    # do the test with this...
    yield TEST_THEME_DIR_REL_PATH
    # cleanup
    if os.path.exists(TEST_THEME_DIR_REL_PATH + "/delete_me.yaml"):
        print(f"Deleting {TEST_THEME_DIR_REL_PATH}/delete_me.yaml")
        os.remove(TEST_THEME_DIR_REL_PATH + "/delete_me.yaml")


def test_get_theme_list(theme_test_setup):
    """Test retrieval of theme list."""
    mgr = ThemeMgr(theme_test_setup)
    assert "default" in mgr.get_theme_list()
    assert "creative" in mgr.get_theme_list()

    # Add a new theme
    new_theme = Theme(
        disk_name="delete_me.yaml",
        display_name="Custom Theme",
        description="A custom test theme.",
        system_prompt="Creative AI mode.",
        user_prompt="Enhance: \"{prompt}\"",
        prompts=["A magical forest", "A cyberpunk alley"],
        styles={"dreamy": "Soft glow, ethereal colors."}
    )
    mgr.write_theme(new_theme)
    assert "delete_me" in mgr.get_theme_list()


def test_get_theme(theme_test_setup):
    """Test retrieving an existing theme."""
    mgr = ThemeMgr(theme_test_setup)
    theme = mgr.get_theme("default")
    assert isinstance(theme, Theme)
    assert theme.disk_name == "default.yaml"


def test_write_theme(theme_test_setup):
    """Test writing a new theme to file."""
    mgr = ThemeMgr(theme_test_setup)
    new_theme = Theme(
        disk_name="delete_me.yaml",
        display_name="New Theme",
        description="A newly added theme.",
        system_prompt="AI creative mode.",
        user_prompt="Transform: \"{prompt}\"",
        prompts=["A floating castle", "An underwater city"],
        styles={"fantasy": "Whimsical, colorful lighting."}
    )
    mgr.write_theme(new_theme)

    assert os.path.exists(os.path.join(theme_test_setup, "delete_me.yaml"))
    saved_theme = mgr.get_theme("delete_me")
    assert saved_theme.display_name == "New Theme"


def test_delete_theme(theme_test_setup):
    """Test deleting a theme."""
    mgr = ThemeMgr(theme_test_setup)
    mgr.delete_theme("default")
    assert "default" not in mgr.get_theme_list()

    with pytest.raises(FileNotFoundError):
        mgr.get_theme("default")
