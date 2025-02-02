from typing import Dict, List, Optional, Tuple, Union, TextIO
import pygame
import time
import os
import json
from PIL import Image
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QSpinBox, QLineEdit, QPushButton, QFileDialog, QWidget)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv


class ConfigDialog(QDialog):
    """
    Dialog window for configuring display settings.

    Parameters:
        config (Dict[str, Union[str, int, List[int]]]): Current configuration dictionary
        parent (Optional[QWidget]): Parent widget for the dialog
    """

    def __init__(self, config: Dict[str, Union[str, int, List[int]]], parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.config: Dict[str, Union[str, int, List[int]]] = config
        self.setWindowTitle("Display Configuration")
        self.setup_ui()

    def setup_ui(self) -> None:
        """Initialize and layout all UI elements in the dialog."""
        layout = QVBoxLayout()

        # Image Directory
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Image Directory:")
        self.dir_edit = QLineEdit(str(self.config.get('image_directory', '')))
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)

        # Display Time
        time_layout = QHBoxLayout()
        time_label = QLabel("Display Time (seconds):")
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 3600)
        self.time_spin.setValue(int(self.config.get('display_time', 5)))
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_spin)
        layout.addLayout(time_layout)

        # Background Color
        bg_layout = QHBoxLayout()
        bg_label = QLabel("Background Color (R,G,B):")
        self.bg_edit = QLineEdit(','.join(map(str, self.config.get('background_color', [0, 0, 0]))))
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_edit)
        layout.addLayout(bg_layout)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_directory(self) -> None:
        """Open file dialog for selecting image directory."""
        directory: str = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.dir_edit.setText(directory)

    def get_config(self) -> Dict[str, Union[str, int, List[int]]]:
        """
        Get the current configuration from dialog inputs.

        Returns:
            Dict[str, Union[str, int, List[int]]]: Configuration dictionary with updated values
        """
        try:
            bg_color: List[int] = [int(x.strip()) for x in self.bg_edit.text().split(',')]
            return {
                'image_directory': self.dir_edit.text(),
                'display_time': self.time_spin.value(),
                'background_color': bg_color
            }
        except ValueError:
            # Return default values if parsing fails
            return {
                'image_directory': self.dir_edit.text(),
                'display_time': self.time_spin.value(),
                'background_color': [0, 0, 0]
            }


class ConfigManager:
    """
    Manages loading and saving of display configuration.

    Parameters:
        config_file (str): Path to the configuration file
    """

    def __init__(self, config_file: str = 'display_config.json') -> None:
        self.config_file: str = config_file
        self.default_config: Dict[str, Union[str, int, List[int]]] = {
            'image_directory': '',
            'display_time': 5,
            'background_color': [0, 0, 0]
        }
        self.config: Dict[str, Union[str, int, List[int]]] = self.load_config()

    def load_config(self) -> Dict[str, Union[str, int, List[int]]]:
        """
        Load configuration from file or return defaults if file doesn't exist.

        Returns:
            Dict[str, Union[str, int, List[int]]]: Loaded configuration dictionary
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, config: Dict[str, Union[str, int, List[int]]]) -> None:
        """
        Save configuration to file.

        Parameters:
            config (Dict[str, Union[str, int, List[int]]]): Configuration to save
        """
        try:
            with open(self.config_file, 'w', encoding ='utf8') as config_out:
                json.dump(config, config_out, indent=4)  # type: TextIO
            self.config = config
        except Exception as e:
            print(f"Error saving config: {e}")


class FullscreenDisplay:
    """
    Main display class for fullscreen image slideshow with configuration.

    This class handles the display of images in fullscreen mode, configuration
    management, and user interaction for settings adjustment.
    """

    def __init__(self) -> None:
        pygame.init()
        self.app: QApplication = QApplication([])
        self.config_manager: ConfigManager = ConfigManager()

        # screen_info: pygame.Surface = pygame.display.Info()
        screen_info = pygame.display.Info()
        self.screen_width: int = screen_info.current_w
        self.screen_height: int = screen_info.current_h

        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.FULLSCREEN
        )
        pygame.mouse.set_visible(True)

    def show_config_dialog(self) -> bool:
        """
        Display configuration dialog and save changes if accepted.

        Returns:
            bool: True if configuration was updated, False otherwise
        """
        dialog: ConfigDialog = ConfigDialog(self.config_manager.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config: Dict[str, Union[str, int, List[int]]] = dialog.get_config()
            self.config_manager.save_config(new_config)
            return True
        return False

    def load_and_resize_image(self, image_path: str) -> pygame.Surface:
        """
        Load and resize image to fit screen while maintaining aspect ratio.

        Parameters:
            image_path (str): Path to the image file

        Returns:
            pygame.Surface: Resized image as Pygame surface
        """
        pil_image: Image.Image = Image.open(image_path)

        img_ratio: float = pil_image.width / pil_image.height
        screen_ratio: float = self.screen_width / self.screen_height

        if screen_ratio > img_ratio:
            height: int = self.screen_height
            width: int = int(height * img_ratio)
        else:
            width: int = self.screen_width
            height: int = int(width / img_ratio)

        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)

        mode: str = pil_image.mode
        size: Tuple[int, int] = pil_image.size
        data: bytes = pil_image.tobytes()

        pygame_image = pygame.image.fromstring(data, size, mode)
        return pygame_image

    def display_image(self, image_path: str) -> bool:
        """
        Display an image fullscreen with centered positioning.

        Parameters:
            image_path (str): Path to the image file

        Returns:
            bool: True if successful, False if error occurred
        """
        try:
            pygame_image: pygame.Surface = self.load_and_resize_image(image_path)

            image_width: int
            image_height: int
            image_width, image_height = pygame_image.get_size()

            x: int = (self.screen_width - image_width) // 2
            y: int = (self.screen_height - image_height) // 2

            bg_color: List[int] = self.config_manager.config.get('background_color', [0, 0, 0])
            self.screen.fill(bg_color)

            self.screen.blit(pygame_image, (x, y))
            pygame.display.flip()

            return True
        except Exception as e:
            print(f"Error displaying image: {e}")
            return False

    def run(self) -> None:
        """
        Run the slideshow with configuration and user interaction.

        This method handles the main loop of the application, including:
        - Loading and displaying images
        - Handling user input (mouse clicks, keyboard)
        - Configuration updates
        - Timing between images
        """
        running: bool = True
        while running:
            config: Dict[str, Union[str, int, List[int]]] = self.config_manager.config
            image_folder: str = str(config['image_directory'])
            display_time: int = int(config['display_time'])

            if not os.path.exists(image_folder):
                print(f"Image directory not found: {image_folder}")
                time.sleep(1)
                continue

            image_files: List[str] = [
                f for f in os.listdir(image_folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ]

            for image_file in image_files:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            break
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.show_config_dialog():
                            break

                if not running:
                    break

                image_path: str = os.path.join(image_folder, image_file)
                if self.display_image(image_path):
                    time.sleep(display_time)

        pygame.quit()


def main() -> None:
    """Initialize and run the fullscreen display application."""
    # https://pypi.org/project/python-dotenv/
    load_dotenv()  # load .env vars into environment variables
    # Make sure OPENAI_API_KEY environment variable is set
    if 'OPEN_AI_SECRET' not in os.environ:
        print("Please set OPENAI_API_KEY environment variable")
        return
    display: FullscreenDisplay = FullscreenDisplay()
    display.run()


if __name__ == "__main__":

    main()