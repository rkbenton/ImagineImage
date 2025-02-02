from typing import Dict, List, Optional, Union
import pygame
import time
import json
import random
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QGridLayout, QLabel, QSpinBox,
                             QLineEdit, QPushButton, QFileDialog, QWidget, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from dotenv import load_dotenv

CONFIG_PATH = Path("app_config.json")
IMAGE_DIR = Path("image_out")
FULL_SCREEN: bool = True
DEFAULT_BG_COLOR = (128, 128, 128)  # Neutral gray
DEFAULT_DISPLAY_DURATION = "00:00:05"  # 5 seconds


class ConfigDialog(QDialog):
    config_updated = pyqtSignal(dict)

    def __init__(self, config: Dict[str, Union[str, int, List[int], bool]], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Display Configuration")

        # Set up the user interface
        layout = QGridLayout()
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 1920)
        self.width_input.setValue(self.config.get("width", 800))
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 1080)
        self.height_input.setValue(self.config.get("height", 600))
        self.title_input = QLineEdit(self.config.get("title", "Pygame Window"))
        self.full_screen_checkbox = QCheckBox("Full Screen")
        self.full_screen_checkbox.setChecked(self.config.get("full_screen", False))
        self.display_duration_input = QLineEdit(self.config.get("display_duration", DEFAULT_DISPLAY_DURATION))
        self.background_color_input = QLineEdit(
            ",".join(map(str, self.config.get("background_color", DEFAULT_BG_COLOR)))
        )
        self.image_directory_input = QLineEdit(self.config.get("image_directory", "image_out"))

        layout.addWidget(QLabel("Width:"), 0, 0)
        layout.addWidget(self.width_input, 0, 1)
        layout.addWidget(QLabel("Height:"), 1, 0)
        layout.addWidget(self.height_input, 1, 1)
        layout.addWidget(QLabel("Title:"), 2, 0)
        layout.addWidget(self.title_input, 2, 1)
        layout.addWidget(self.full_screen_checkbox, 3, 0, 1, 2)
        layout.addWidget(QLabel("Display Duration (HH:MM:SS):"), 4, 0)
        layout.addWidget(self.display_duration_input, 4, 1)
        layout.addWidget(QLabel("Background Color (R,G,B):"), 5, 0)
        layout.addWidget(self.background_color_input, 5, 1)
        layout.addWidget(QLabel("Image Directory:"), 6, 0)
        layout.addWidget(self.image_directory_input, 6, 1)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button, 7, 0, 1, 2)

        self.setLayout(layout)


    def write_config(self, config: Dict[str, Union[str, int, List[int], tuple[int,...], bool]]) -> None:
        """Saves configuration settings to a JSON file."""
        try:
            with CONFIG_PATH.open("w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)  # type:ignore
        except IOError as e:
            print(f"Error saving config: {e}")

    def save_config(self) -> None:
        """Saves and emits the updated configuration."""
        self.config["width"] = self.width_input.value()
        self.config["height"] = self.height_input.value()
        self.config["title"] = self.title_input.text()
        self.config["full_screen"] = self.full_screen_checkbox.isChecked()
        self.config["display_duration"] = self.display_duration_input.text()
        self.config["background_color"] = tuple(map(int, self.background_color_input.text().split(",")))
        self.config["image_directory"] = self.image_directory_input.text()
        self.config_updated.emit(self.config)
        self.write_config(config=self.config)
        self.accept()
