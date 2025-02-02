import json
import random
import time
from pathlib import Path
from typing import Dict, List, Union

import pygame
from PIL import Image
from PyQt6.QtWidgets import (QApplication)

from ConfigDialog import ConfigDialog

CONFIG_PATH = Path("app_config.json")
IMAGE_DIR = Path("image_out")
FULL_SCREEN: bool = True
DEFAULT_BG_COLOR = (128, 128, 255)
DEFAULT_DISPLAY_DURATION = "00:00:05"  # 5 seconds


class PygameApp:
    def __init__(self):
        pygame.init()
        self.config: Dict[str, Union[str, int, List[int], bool]] = self.load_config()
        self.running = True
        self.screen = None
        self.set_screen()
        self.last_image_time = time.time()
        self.current_image = None
        self.display_duration = 5
        self.image_position = None

    def load_config(self) -> Dict[str, Union[str, int, List[int], bool]]:
        """Loads configuration settings from a JSON file."""
        try:
            if CONFIG_PATH.exists():
                with CONFIG_PATH.open("r", encoding="utf-8") as file:
                    config = json.load(file)
            else:
                config = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            config = {}

        config.setdefault("width", 800)
        config.setdefault("height", 600)
        config.setdefault("title", "Pygame Window")
        config.setdefault("full_screen", False)
        config.setdefault("display_duration", DEFAULT_DISPLAY_DURATION)
        config.setdefault("background_color", DEFAULT_BG_COLOR)
        config.setdefault("image_directory", "image_out")

        image_dir = Path(config["image_directory"])
        if not image_dir.exists():
            image_dir.mkdir(parents=True, exist_ok=True)

        return config

    def parse_display_duration(self, duration_str: str) -> int:
        """Parses a HH:MM:SS string into seconds."""
        try:
            parts = [int(p) for p in duration_str.split(":")]
            while len(parts) < 3:
                parts.insert(0, 0)  # Fill missing values with zeros
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        except ValueError:
            return 5  # Default to 5 seconds

    def set_screen(self):
        """
        Sets the Pygame display mode based on the config.
        Note: You can set the mode of the screen surface multiple times,
        but you might have to do pygame.display.quit() followed by pygame.display.init().
        See the pygame documentation here
        http://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
        """
        if "full_screen" not in self.config:
            self.config["full_screen"] = pygame.FULLSCREEN
        # screen_mode may only be pygame.FULLSCREEN or pygame.RESIZABLE
        screen_mode = pygame.FULLSCREEN if self.config["full_screen"] else pygame.RESIZABLE

        self.screen = pygame.display.set_mode((self.config["width"], self.config["height"]), screen_mode)
        color_value = tuple(self.config["background_color"])  # type: ignore
        self.screen.fill(color=color_value)  # type: ignore
        pygame.display.set_caption(self.config["title"])

    # def load_random_image(self):
    #     """Loads a random image from the configured image directory."""
    #     image_dir = Path(self.config["image_directory"])
    #     if image_dir.exists() and image_dir.is_dir():
    #         images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg"))
    #         if images:
    #             image_path = random.choice(images)
    #             image = Image.open(image_path)
    #             image = image.convert("RGB")
    #             image = image.resize((self.config["width"], self.config["height"]), Image.LANCZOS)
    #             self.current_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    def load_random_image(self):
        """Loads a random image from the configured image directory while maintaining its aspect ratio."""
        image_dir = Path(self.config["image_directory"])
        if image_dir.exists() and image_dir.is_dir():
            images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg"))
            if images:
                image_path = random.choice(images)
                image = Image.open(image_path)
                image = image.convert("RGB")
                screen_width, screen_height = self.config["width"], self.config["height"]

                # Maintain aspect ratio
                image.thumbnail((screen_width, screen_height), Image.LANCZOS)
                self.current_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

                # Calculate position to center the image
                self.image_position = (
                    (screen_width - image.size[0]) // 2,
                    (screen_height - image.size[1]) // 2
                )
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

            # Load a new image based on the configured duration in seconds
            self.display_duration = self.parse_display_duration(self.config["display_duration"])
            if time.time() - self.last_image_time >= self.display_duration or self.current_image is None:
                self.load_random_image()
                self.last_image_time = time.time()

                self.screen.fill(tuple(self.config["background_color"]))  # Configurable background color
                if self.current_image:
                    self.screen.blit(self.current_image, self.image_position)
                pygame.display.flip()
                time.sleep(0.1)  # Reduce CPU usage

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
