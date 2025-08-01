import argparse
import logging
import os
import random
import sys
import time
import tkinter as tk
from pathlib import Path
import re

from PIL import Image, ImageTk
from dotenv import load_dotenv

from ConfigMgr import ConfigMgr
from ImageGenerator import ImageGenerator, ImGenError
from PromptGenerator import PromptGenerator
from RatingManager import RatingManager  # our previously defined rating manager
from S3Manager import S3Manager


class ImagineImage:
    CONFIG_FILE = Path(ConfigMgr.LOCAL_CONFIG_FILE_NAME)
    RATING_INSTRUCTIONS = "Use numbers 1-5 to rate, ←/→ to navigate, X to exit."
    UPDATE_INTERVAL = 250

    def __init__(self):
        self.config_mgr = ConfigMgr()
        self.config = self.config_mgr.load_config()
        api_key = os.environ["OPEN_AI_SECRET"]
        self.prompt_generator = PromptGenerator(config_mgr=self.config_mgr, api_key=api_key)
        self.image_generator = ImageGenerator(prompt_generator=self.prompt_generator, api_key=api_key)
        self.s3_manager = S3Manager()

        # Initialize TKInter root and create display widgets.
        self.tk_root = tk.Tk()
        self.tk_root.title("Imagine Image")

        self.window_width = 0
        self.window_height = 0
        self.window_position = 0
        self.set_window_default_size()

        self.tk_root.geometry(
            f"{self.window_width}x{self.window_height}+{self.window_position[0]}+{self.window_position[1]}")

        self.image_canvas = tk.Canvas(self.tk_root, highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        self.image_canvas.focus_set()
        self.current_tk_image = None
        self.image_id = None

        # Create an overlay text item on the canvas.
        # This text item can be updated later via itemconfig().
        self.info_text_id: int = self.image_canvas.create_text(
            10, 10,  # x, y position (top-left corner)
            width=self.image_canvas.winfo_width() - 20,  # initial width (will update)
            anchor="nw",
            text="",
            fill="white",
            font=("Helvetica", 12)
        )

        # set is_fullscreen to opposite of desired state to toggle flips to it
        self.is_fullscreen: bool = not self.config.get("full_screen", False)
        self.toggle_fullscreen()

        # Bind the canvas's configuration changes to update the overlay's size.
        self.image_canvas.bind("<Configure>", self.on_canvas_configure)

        # Normal mode variables.
        self.current_image = None  # holds a PIL Image for normal mode
        self.last_image_time = None  # sentinel value; None == starting up

        # Rating mode variables.
        self.rating_mode = False
        self.rating_manager = None

        # Bind key events.
        self.tk_root.bind("<Key>", self.on_key)

    def parse_display_duration(self) -> int:
        try:
            duration_str: str = self.config["display_duration"]
            parts = [int(p) for p in duration_str.split(":")]
            while len(parts) < 3:
                parts.insert(0, 0)
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        except ValueError:
            return 3600

    def delete_oldest_files(self, directory: str, min_files: int = 50):
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        files = sorted(dir_path.glob("*"), key=lambda f: f.stat().st_mtime)
        if len(files) <= min_files:
            return

        for file in files[:len(files) - min_files]:
            try:
                file.unlink()
                logger.info(f"Deleted: {file}")
            except Exception as e:
                logger.warn(f"Failed to delete {file}: {e}")

    def on_canvas_configure(self, event):
        """
        Callback for when the canvas is resized.
        Update the overlay rectangle and text width so that they span the width of the canvas.
        """
        # Determine a suitable height for the overlay background (e.g., 30 pixels).
        overlay_height = 30
        # Update the text item to have a width a little less than the full canvas width.
        self.image_canvas.itemconfig(self.info_text_id, width=event.width - 20)

    def scale_image_to_fit_screen(self, screen_w: int, screen_h: int, img_w: int, img_h: int) -> tuple[int, int]:
        scale = min(screen_w / img_w, screen_h / img_h)
        return int(img_w * scale), int(img_h * scale)

    def extract_rating(self, filename: Path) -> float:
        """
        :return: Look for a rating in the file name and
        return that value or 0.0 if not found"""
        match = re.search(r'r\[(\d+\.\d+)\]', str(filename))
        return float(match.group(1)) if match else 0.0

    def get_random_image_from_disk(self) -> Image.Image | None:
        # Assume images to be rated are stored in: save_directory_path/<theme_dir>
        self.config = self.config_mgr.load_config()

        theme_dir = self.config["active_theme"].replace(".yaml", "")
        image_dir = Path(self.config["save_directory_path"]) / theme_dir
        if not (image_dir.exists() and image_dir.is_dir()):
            logger.info(f"{image_dir} not found.")
            return None
        images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg"))
        if not images:
            logger.info(f"No images found in {str(image_dir)}")
            return None

        min_rating: float = float(self.config.get("minimum_rating_filter", 0.0))
        # if min_rating is less than 1.0, do not filter
        if min_rating < 1.0:
            return self.get_image_from_disk(random.choice(images))

        # find images of the given rating or above
        filtered_images = [img for img in images if self.extract_rating(img) >= min_rating]
        if len(filtered_images) == 0:
            logger.warning(f"No images found with min rating of >= {min_rating} in {str(image_dir)}")
            return self.get_image_from_disk(random.choice(images))

        return self.get_image_from_disk(random.choice(filtered_images))

    def get_image_from_disk(self, path_to_image_file: Path) -> Image.Image | None:
        try:
            pil_img = Image.open(str(path_to_image_file))
            return pil_img.convert("RGB")
        except Exception as e:
            logger.warning(f"Failed to load {path_to_image_file}: {e}")
            return None

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return r, g, b

    def display_image_tk(self, pil_img: Image.Image, bkgd_hex_color: str = "#000000") -> None:
        """
        Resize the given PIL image to fit within the current window while preserving
        its aspect ratio, center it on a background of the given color, and update the canvas.
        """
        if pil_img is None:
            logger.warn("display_image_tk: Received None image")
            return

        # Update idle tasks and get canvas dimensions.
        self.tk_root.update_idletasks()
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 600

        # Create a background using Pillow.
        r, g, b = ImagineImage.hex_to_rgb(bkgd_hex_color)
        background = Image.new("RGB", (canvas_width, canvas_height), (r, g, b))

        # Calculate the new image dimensions while preserving aspect ratio.
        orig_w, orig_h = pil_img.size
        new_w, new_h = self.scale_image_to_fit_screen(canvas_width, canvas_height, orig_w, orig_h)
        resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Center the resized image on the background.
        x_offset = (canvas_width - new_w) // 2
        y_offset = (canvas_height - new_h) // 2
        background.paste(resized, (x_offset, y_offset))

        # Convert the background image to a PhotoImage.
        tk_image = ImageTk.PhotoImage(background)
        self.current_tk_image = tk_image  # Save a reference to prevent garbage collection.

        # Update or create the image item on the canvas.
        if self.image_id is None:
            self.image_id = self.image_canvas.create_image(0, 0, anchor="nw", image=tk_image)
        else:
            self.image_canvas.itemconfig(self.image_id, image=tk_image)

        # Ensure the overlay text remains on top.
        self.image_canvas.tag_raise(self.info_text_id)

    def update_image(self):
        """
        In normal mode, periodically update the displayed image.
        When in rating mode, skip normal updates.
        """
        if self.rating_mode:
            # In rating mode, do not update from normal mode.
            self.tk_root.after(ms=self.UPDATE_INTERVAL, func=self.update_image)
            return

        # First time? Do some extra work...
        if self.last_image_time is None:
            self.last_image_time = time.time() - 86400  # trigger immediate update afterwards
            if not self.config["local_files_only"]:
                # grab a random image and display it immediately so we don't have a blank screen
                # while we generate a new prompt and a new image
                logger.info("Setting up first image")
                self.current_image = self.get_random_image_from_disk()
                self.display_image_tk(self.current_image, self.config["background_color"])
                self.tk_root.after(500, self.update_image)
                return

        min_display_duration = self.parse_display_duration()
        now = time.time()
        if now - self.last_image_time >= min_display_duration or self.current_image is None:
            logger.info("Timer expired; getting new image.")
            self.config = self.config_mgr.load_config()
            self.delete_oldest_files(self.config["save_directory_path"], int(self.config["max_num_saved_files"]))

            if self.config["local_files_only"]:
                self.current_image = self.get_random_image_from_disk()
            else:
                output_file_info = None
                self.image_canvas.itemconfig(self.info_text_id, text="")
                screen_xy = (self.tk_root.winfo_screenwidth(), self.tk_root.winfo_screenheight())
                try:
                    output_file_info: [Path, Path] = self.image_generator.generate_image(
                        screen_xy, self.config["save_directory_path"]
                    )
                    image_path: Path = output_file_info[0]
                    prompt_path: Path = output_file_info[1]
                    logger.info(f"New image from disk at {str(image_path)}")
                    if image_path is not None:
                        theme_name = self.prompt_generator.get_theme_name().replace(".yaml", "")
                        s3_key_img = f"{theme_name}/{os.path.basename(image_path)}"
                        logger.info(f"Saving image to S3 at {s3_key_img}")
                        self.s3_manager.upload_to_s3(image_path, s3_key_img)
                        s3_key_prompt = f"{theme_name}/{os.path.basename(prompt_path)}"
                        logger.info(f"Saving prompt to S3 at {s3_key_prompt}")
                        self.s3_manager.upload_to_s3(prompt_path, s3_key_prompt)
                        self.current_image = self.get_image_from_disk(image_path)
                except ImGenError as e:
                    logger.error(e, stack_info=True, exc_info=True)
                    self.image_canvas.itemconfig(self.info_text_id, text=str(e))
            self.last_image_time = now

        if self.current_image:
            self.display_image_tk(self.current_image, self.config["background_color"])
        self.tk_root.after(ms=self.UPDATE_INTERVAL, func=self.update_image)

    def enter_rating_mode(self):
        """Switch to rating mode: initialize RatingManager and display the first unrated image."""
        self.image_canvas.itemconfig(self.info_text_id, text="")
        self.rating_mode = True
        # Initialize RatingManager with our S3 manager.
        self.rating_manager = RatingManager(self.s3_manager)
        # Assume images to rate are stored under: save_directory_path/<active_theme without .yaml>
        self.config_mgr.load_config()
        theme_dir = self.config["active_theme"].replace(".yaml", "")
        logger.info(f"Beginning to rate images from {theme_dir}")
        image_dir = str(Path(self.config["save_directory_path"]) / theme_dir)
        self.rating_manager.start_rating(image_dir)
        num_to_rate = self.rating_manager.num_remaining_to_rate()

        self.image_canvas.itemconfig(self.info_text_id,
                                     text=f"Rating Mode:\n{self.RATING_INSTRUCTIONS}"
                                          f"\nThere are {num_to_rate} images to rate")
        self.update_rating_display()

    def exit_rating_mode(self):
        """Exit rating mode and return to normal mode."""
        self.rating_mode = False
        self.rating_manager = None
        self.image_canvas.itemconfig(self.info_text_id, text="")

    def update_rating_display(self):
        """Update the display to show the current rating image and info from RatingManager."""
        if self.rating_manager is None or not self.rating_manager.rating_list:
            self.image_canvas.itemconfig(self.info_text_id,
                                         text="Rating Mode: No images to rate.\n"
                                              "Hit X to exit.")
            return

        current_file = self.rating_manager.rating_list[self.rating_manager.current_index]
        logger.info(f"Updating rating display with {current_file}")
        pil_img = self.get_image_from_disk(Path(current_file))
        self.display_image_tk(pil_img, self.config["background_color"])

        # Update the info label with filename and current rating (if any).
        filename = Path(current_file).name
        num_to_rate = self.rating_manager.num_remaining_to_rate()
        self.image_canvas.itemconfig(self.info_text_id, text=
        f"Rating Mode\n{self.RATING_INSTRUCTIONS}\n"
        f"File: {filename}\nThere are {num_to_rate} images to rate")

    def on_key(self, event):
        key = event.keysym.lower()
        logger.info(f"got key: '{key}'")
        if self.rating_mode:
            # In rating mode, process rating and navigation keys.
            if key in ['1', '2', '3', '4', '5']:
                rating_value = float(key)
                current_file = self.rating_manager.rating_list[self.rating_manager.current_index]
                self.rating_manager.rate_file(current_file, rating_value)
                self.update_rating_display()
            elif key == "left":
                try:
                    self.rating_manager.prev()
                    self.update_rating_display()
                except Exception as e:
                    logger.info("Already at first image.")
                    self.image_canvas.itemconfig(self.info_text_id, text="Already at first image.")

            elif key == "right":
                try:
                    self.rating_manager.next()
                    self.update_rating_display()
                except Exception as e:
                    logger.info("Already at last image. Hit X to exit rating mode.")
                    self.image_canvas.itemconfig(self.info_text_id, text="No more images.")
            elif key == 'x':
                self.exit_rating_mode()
            else:
                # Ignore other keys in rating mode.
                pass
        else:
            # Normal mode key handling.
            if key == 'q':
                self.tk_root.quit()
            elif key == 'r':
                self.enter_rating_mode()
            elif key == 't':
                self.toggle_fullscreen()

    def update_info_text(self, msg: str):
        self.image_canvas.itemconfig(
            self.info_text_id,
            text=f"{msg:str}"
        )

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            logger.info(f"Entering full screen mode.")
            # let windowing system update itself so we get proper window size
            self.tk_root.update_idletasks()
            # Save current window position and size before going fullscreen
            self.window_width = self.tk_root.winfo_width()
            self.window_height = self.tk_root.winfo_height()
            self.window_position = (self.tk_root.winfo_x(), self.tk_root.winfo_y())

            # initial values may be zero, thus default to 200 minimums; well catch
            # that and set it to something more reasonable
            if self.window_width <= 200 and self.window_height <= 200:
                self.set_window_default_size()
            # Go fullscreen
            self.tk_root.attributes("-fullscreen", True)
            self.is_fullscreen = True

            # Update the info text to show current state
        else:
            # Exit fullscreen and restore previous dimensions
            logger.info(f"Entering small screen mode.")
            self.tk_root.attributes("-fullscreen", False)
            self.is_fullscreen = False

            # Restore previous window size and position
            self.tk_root.geometry(
                f"{self.window_width}x{self.window_height}+{self.window_position[0]}+{self.window_position[1]}")

    def main(self):
        self.config = self.config_mgr.load_config()
        # Start the normal mode image update loop.
        self.tk_root.after(100, self.update_image)
        self.tk_root.mainloop()

    def set_window_default_size(self):
        self.window_width = self.tk_root.winfo_screenwidth() // 2
        self.window_height = self.tk_root.winfo_screenheight() // 2
        self.window_position = (50, 50)  # Default x, y position


if __name__ == '__main__':
    print("Service started!", file=sys.stdout, flush=True)
    load_dotenv()

    # set up arg parser
    parser = argparse.ArgumentParser(
        description='Make interesting images with AI)',
        epilog="Definitely alpha software!")

    parser.add_argument('--log-level', action="store", choices=['info', 'debug', 'warning', 'error'],
                        default='info', help="set logging level")
    parser.add_argument('--log-mode', action="store", choices=['append', 'overwrite'],
                        default='overwrite', help="append to logging or start fresh")

    cli_args = parser.parse_args()

    # set log level
    loglevel: str = cli_args.log_level.upper()
    numeric_level = getattr(logging, loglevel.upper(), 20)  # 20 INFO, 10 DEBUG
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {loglevel}')
    if cli_args.log_level is not None:
        print(f"Logging level: {cli_args.log_level} ({numeric_level})")

    log_filemode: str = 'a' if cli_args.log_mode.casefold() == 'append' else 'w'  # 'a' == append, 'w' over-write
    # build the logger
    logging.basicConfig(
        filename="logfile.log", encoding='utf-8',
        level=numeric_level,
        filemode=log_filemode,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )
    logger = logging.getLogger(__name__)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    logger.info(f"args = {cli_args}")

    app = ImagineImage()
    app.main()
