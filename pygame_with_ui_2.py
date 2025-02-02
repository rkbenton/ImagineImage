from typing import Dict, List, Optional, Union
import pygame
import time
import json
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QGridLayout, QLabel, QSpinBox,
                             QLineEdit, QPushButton, QFileDialog, QWidget, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from dotenv import load_dotenv

# Load environment variables safely
load_dotenv()

CONFIG_PATH = Path("app_config.json")
FULL_SCREEN: bool = True

def load_config() -> Dict[str, Union[str, int, List[int], bool]]:
    """Loads configuration settings from a JSON file."""
    try:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config: {e}")
    return {"width": 800, "height": 600, "title": "Pygame Window", "full_screen": False}


def save_config(config: Dict[str, Union[str, int, List[int], bool]]) -> None:
    """Saves configuration settings to a JSON file."""
    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
    except IOError as e:
        print(f"Error saving config: {e}")


class ConfigDialog(QDialog):
    config_updated = pyqtSignal(dict)

    def __init__(self, config: Dict[str, Union[str, int, List[int], bool]], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Display Configuration")
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the user interface."""
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

        layout.addWidget(QLabel("Width:"), 0, 0)
        layout.addWidget(self.width_input, 0, 1)
        layout.addWidget(QLabel("Height:"), 1, 0)
        layout.addWidget(self.height_input, 1, 1)
        layout.addWidget(QLabel("Title:"), 2, 0)
        layout.addWidget(self.title_input, 2, 1)
        layout.addWidget(self.full_screen_checkbox, 3, 0, 1, 2)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button, 4, 0, 1, 2)

        self.setLayout(layout)

    def save_config(self) -> None:
        """Saves and emits the updated configuration."""
        self.config["width"] = self.width_input.value()
        self.config["height"] = self.height_input.value()
        self.config["title"] = self.title_input.text()
        self.config["full_screen"] = self.full_screen_checkbox.isChecked()
        self.config_updated.emit(self.config)
        save_config(self.config)
        self.accept()


class PygameApp:
    def __init__(self, config: Dict[str, Union[str, int, List[int], bool]]):
        pygame.init()
        self.config = config
        self.running = True
        self.set_screen()

    def set_screen(self):
        """
        Sets the Pygame display mode based on the config.
        Note: You can set the mode of the screen surface multiple times,
        but you might have to do pygame.display.quit() followed by pygame.display.init().
        See the pygame documentation here
        http://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
        """
        if not "full_screen" in config:
            self.config["full_screen"] = FULL_SCREEN
        # screen_mode may only be pygame.FULLSCREEN or pygame.RESIZABLE
        screen_mode = pygame.FULLSCREEN if self.config["full_screen"] else pygame.RESIZABLE

        flags = pygame.FULLSCREEN if self.config["full_screen"] else 0
        self.screen = pygame.display.set_mode((self.config["width"], self.config["height"]), flags)
        pygame.display.set_caption(self.config["title"])

    def event_loop(self) -> None:
        """Handles the Pygame event loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    elif event.key == pygame.K_COMMA:
                        self.open_config_dialog()
            self.screen.fill((0, 0, 0))  # Black background
            pygame.display.flip()
            time.sleep(0.01)  # Reduce CPU usage

    def open_config_dialog(self):
        """Opens the configuration dialog."""
        app = QApplication.instance() or QApplication([])
        dialog = ConfigDialog(self.config)
        if dialog.exec():
            self.config = dialog.config
            self.set_screen()

    def run(self) -> None:
        """Runs the Pygame loop and ensures proper cleanup."""
        try:
            self.event_loop()
        finally:
            pygame.quit()


if __name__ == "__main__":
    config = load_config()
    pygame_app = PygameApp(config)
    pygame_app.run()
