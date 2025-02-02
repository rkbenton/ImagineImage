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

# Load environment variables safely
load_dotenv()

CONFIG_PATH = Path("app_config.json")
IMAGE_DIR = Path("image_out")
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


class PygameApp:
    def __init__(self, config: Dict[str, Union[str, int, List[int], bool]]):
        pygame.init()
        self.config = config
        self.running = True
        self.set_screen()
        self.last_image_time = time.time()
        self.current_image = None
        self.load_random_image()

    def set_screen(self):
        """
        Sets the Pygame display mode based on the config.
        """
        if "full_screen" not in self.config:
            self.config["full_screen"] = FULL_SCREEN
        flags = pygame.FULLSCREEN if self.config["full_screen"] else 0
        self.screen = pygame.display.set_mode((self.config["width"], self.config["height"]), flags)
        pygame.display.set_caption(self.config["title"])

    def load_random_image(self):
        """Loads a random image from the image_out directory."""
        if IMAGE_DIR.exists() and IMAGE_DIR.is_dir():
            images = list(IMAGE_DIR.glob("*.png")) + list(IMAGE_DIR.glob("*.jpg")) + list(IMAGE_DIR.glob("*.jpeg"))
            if images:
                image_path = random.choice(images)
                image = Image.open(image_path)
                image = image.convert("RGB")
                image = image.resize((self.config["width"], self.config["height"]), Image.LANCZOS)
                self.current_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

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

            # Load a new image every 5 seconds
            if time.time() - self.last_image_time >= 5:
                self.load_random_image()
                self.last_image_time = time.time()

            self.screen.fill((0, 0, 0))  # Black background
            if self.current_image:
                self.screen.blit(self.current_image, (0, 0))
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
