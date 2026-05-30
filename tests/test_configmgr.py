import pytest
from pathlib import Path
import json
from ConfigMgr import ConfigMgr


@pytest.fixture
def temp_config_file(tmp_path):
    """Creates a temporary config file for testing"""
    config_file = tmp_path / "test_config.json"
    return config_file


@pytest.fixture
def config_mgr(temp_config_file):
    """Creates a ConfigMgr instance with temporary config file"""
    return ConfigMgr(temp_config_file)


@pytest.fixture
def sample_config():
    """Returns a sample valid configuration"""
    return {
        "display_duration": "01:00:00",
        "full_screen": True,
        "max_num_saved_files": 250,
        "minimum_rating_filter": 1.0,
        "save_directory_path": "image_out",
        "background_color": "#aabbcc",
        "active_theme": "creative.yaml",
        "active_style": "random",
        "themes_directory": "themes"
    }


class TestConfigMgr:
    def test_init(self, config_mgr):
        """Test initialization with custom path"""
        assert isinstance(config_mgr.config_file_path, Path)

    def test_validate_time_string_valid(self, config_mgr):
        """Test time string validation with valid inputs"""
        assert config_mgr.validate_time_string("00:00:05")
        assert config_mgr.validate_time_string("23:59:59")
        assert config_mgr.validate_time_string("01:30:00")
        assert config_mgr.validate_time_string("01:01:01")
        assert config_mgr.validate_time_string("1:1:1")
        assert config_mgr.validate_time_string("2:2:2")

    def test_validate_time_string_invalid(self, config_mgr):
        """Test time string validation with invalid inputs"""
        invalid_times = [
            "24:00:00",  # Hours too high
            "00:60:00",  # Minutes too high
            "00:00:60",  # Seconds too high
            "invalid",  # Not a time
            "",  # Empty string
            "00:00",  # Missing seconds
        ]
        for time in invalid_times:
            assert not config_mgr.validate_time_string(time)

    def test_load_config_new_file(self, config_mgr):
        """Test loading config when file doesn't exist"""
        config = config_mgr.load_config()
        assert config["display_duration"] == ConfigMgr.DEFAULT_DISPLAY_DURATION
        assert config["full_screen"] is True
        assert isinstance(config["max_num_saved_files"], int)
        assert isinstance(config["minimum_rating_filter"], float)
        assert config["background_color"] == "#000000"
        assert config["active_theme"] == "creative.yaml"
        assert config["active_style"] == "random"
        assert config["themes_directory"] == "themes"

    def test_save_and_load_config(self, config_mgr, sample_config):
        """Test saving and loading configuration"""
        config_mgr.save_config(sample_config)
        loaded_config = config_mgr.load_config()
        assert loaded_config == sample_config

    def test_validate_config_values(self, config_mgr, sample_config, tmp_path):
        """Test configuration validation"""
        # Set up valid directory
        valid_dir = tmp_path / "valid_dir"
        valid_dir.mkdir()
        sample_config["save_directory_path"] = str(valid_dir)

        # Test valid config
        config_mgr.validate_config_values(sample_config)

        # Test invalid configurations
        invalid_configs = [
            ({"display_duration": "25:00:00"}, "Invalid duration"),
            ({"background_color": "Aardvark"}, "background_color should be a hex color value"),
            ({"max_num_saved_files": 0}, "Maximum saved files"),
            ({"save_directory_path": "nonexistent_dir"}, "Save directory"),
        ]

        for invalid_values, expected_error in invalid_configs:
            invalid_config = sample_config.copy()
            invalid_config.update(invalid_values)
            with pytest.raises(ValueError, match=expected_error):
                config_mgr.validate_config_values(invalid_config)

    def test_config_file_encoding(self, config_mgr, sample_config):
        """Test config file is saved with UTF-8 encoding"""
        sample_config["active_theme"] = "测试中文"  # Test with non-ASCII characters
        config_mgr.save_config(sample_config)

        # Read the file directly to check encoding
        with config_mgr.config_file_path.open('r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data["active_theme"] == "测试中文"

    def test_default_config_structure(self, config_mgr):
        """Test that all required keys are present in default config"""
        config = config_mgr.load_config()
        required_keys = {
            "display_duration",
            "full_screen",
            "max_num_saved_files",
            "minimum_rating_filter",
            "save_directory_path",
            "background_color",
            'active_theme',
            'active_style',
            'themes_directory',
            'local_files_only'
        }
        assert set(config.keys()) == required_keys
