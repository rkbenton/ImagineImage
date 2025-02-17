import pytest

from Theme import Theme


def test_theme_initialization():
    theme = Theme(
        disk_name="xyz.yaml",
        display_name="Arbor Day",
        description="All about the Trees!",
        system_prompt="Test AI.",
        user_prompt="Modify: \"{prompt}\".",
        prompts=["Test prompt 1", "Test prompt 2"],
        styles={"style1": "Description 1", "style2": "Description 2"}
    )

    assert theme.disk_name == "xyz.yaml"
    assert theme.display_name == "Arbor Day"
    assert theme.description == "All about the Trees!"
    assert theme.system_prompt == "Test AI."
    assert theme.user_prompt == "Modify: \"{prompt}\"."
    assert theme.prompts == ["Test prompt 1", "Test prompt 2"]
    assert theme.styles == {"style1": "Description 1", "style2": "Description 2"}


def test_theme_empty_prompts():
    theme = Theme(
        disk_name="xyz.yaml",
        display_name="Arbor Day",
        description="All about the Trees!",
        system_prompt="Test AI.",
        user_prompt="Modify: \"{prompt}\".",
        prompts=[],
        styles={"style1": "Description 1"}
    )
    assert theme.prompts == []


def test_theme_empty_styles():
    theme = Theme(
        disk_name="xyz.yaml",
        display_name="Arbor Day",
        description="All about the Trees!",
        system_prompt="Test AI.",
        user_prompt="Modify: \"{prompt}\".",
        prompts=["Test prompt 1"],
        styles={}
    )

    assert theme.styles == {}

def test_theme_loading():
    mgr = ThemeMgr("themes")
    a_list = mgr.get_theme_list()
    print(f"The following themes are available:{str(a_list)}")
    some_file=a_list[1] + ".yaml"
    print(f"getting {some_file}")
    a_theme = mgr.get_theme(some_file)
    print(a_theme)
    print("\n\n")


if __name__ == "__main__":
    pytest.main()
