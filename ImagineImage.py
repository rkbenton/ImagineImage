import os
import random
import sys
import time
import tkinter as tk  # Tkinter for GUI and configuration dialog
from pathlib import Path

import cv2
import cv2 as cv  # OpenCV library for image processing
import numpy as np  # NumPy for handling image arrays
from dotenv import load_dotenv

from ConfigMgr import ConfigMgr
from ImageGenerator import ImageGenerator
from PromptGenerator import PromptGenerator
from S3Manager import S3Manager


class ImagineImage:
    CONFIG_FILE = Path("app_config.json")
    WINDOW_NAME = "Imagine Image"

    def __init__(self):
        # Initialize Tkinter root and hide the root window
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Hide the main Tkinter root window
        self.config = None
        self.config_mgr = ConfigMgr()
        api_key = os.environ["OPEN_AI_SECRET"]
        self.prompt_generator = PromptGenerator(config_mgr=self.config_mgr, api_key=api_key)
        self.image_generator = ImageGenerator(prompt_generator=self.prompt_generator, api_key=api_key)
        self.s3_manager = S3Manager()

    def parse_display_duration(self) -> int:
        """
        Parses the display_duration string into seconds.
        The format of string is HH:MM:SS
        """
        try:
            duration_str: str = self.config["display_duration"]
            parts = [int(p) for p in duration_str.split(":")]
            while len(parts) < 3:
                parts.insert(0, 0)  # Fill missing values with zeros
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        except ValueError:
            return 3600  # 1 hour, 3600 seconds

    def delete_oldest_files(self, directory: str, min_files: int = 50):
        """
        Deletes the oldest files in a directory until only 'min_files' remain.

        :param directory: The path to the directory containing files.
        :param min_files: The minimum number of files to retain.
        """
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        # Get all files sorted by modification time (oldest first)
        files = sorted(dir_path.glob("*"), key=lambda f: f.stat().st_mtime)

        # Check if we need to delete any files
        if len(files) <= min_files:
            return  # Nothing to delete

        # Delete files until only 'min_files' remain
        for file in files[:len(files) - min_files]:
            try:
                file.unlink()
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

    def scale_image_to_fit_screen(self, screen_w: int, screen_h: int, img_w: int, img_h: int) -> tuple[int, int]:
        """
        Calculate new image dimensions to fit within the screen while maintaining aspect ratio.
        @return: tuple of new width and height of image
        """
        scale = min(screen_w / img_w, screen_h / img_h)
        return int(img_w * scale), int(img_h * scale)

    # def fetch_image_from_ai(self) -> cv2.typing.MatLike | None:
    #     """
    #     This will create a text prompt and use that when calling the
    #     image generation service. Then, it will write the image
    #     to disk. This method will the read the file and generate
    #     a cv2 image. Note that the image is *not* scaled at this time.
    #     @return: the image in cv2 format, or None in case of error
    #     """
    #     screen_width = self.tk_root.winfo_screenwidth()
    #     screen_height = self.tk_root.winfo_screenheight()
    #     image_dir: str = self.config["save_directory_path"]
    #     cv2_img = None
    #
    #     # request image from AI - it will write image to disk
    #     # note: image is *not* scaled to the display port; dimensions
    #     # are used to request approximate resolution from service.
    #     image_path: Path = self.image_generator.generate_image((screen_width, screen_height), image_dir)
    #     if image_path is not None:
    #         # read resulting image from disk
    #         cv2_img = cv2.imread(str(image_path))
    #     return cv2_img

    def get_random_image_from_disk(self) -> cv2.typing.MatLike | None:
        """
        Get a random image from the image directory if there is one.
        return: cv2 image or None
        """
        image_dir = Path(self.config["save_directory_path"])
        cv2_img = None
        if not (image_dir.exists() and image_dir.is_dir()):
            print(f"{image_dir} not found.")
            return None
        images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg"))
        if len(images) == 0:
            print("No images found in {str(image_dir}")
        if images:
            image_path = Path(random.choice(images))
            # cv2_img = cv.imread(cv.samples.findFile(image_path))
            cv2_img = self.get_image_from_disk(image_path)
        return cv2_img

    def get_image_from_disk(self, path_to_image_file: Path) -> cv2.typing.MatLike | None:
        """
        Get a specific image from the disk.
        return: cv2 image or None
        """
        try:
            cv2_img: cv2.typing.MatLike = cv.imread(str(path_to_image_file))
        except Exception as e:
            print(f"Failed to load {path_to_image_file}: {e}")
            return None
        return cv2_img

    def display_image(self, cv2_img: cv2.typing.MatLike) -> None:
        """
        Resizes the given cv2 image while maintaining aspect ratio,
        centers it on a black canvas, and displays it in the OpenCV window.
        """
        if cv2_img is None:
            print("display_image unable to display None cv2 image")
            return

        screen_width = self.tk_root.winfo_screenwidth()
        screen_height = self.tk_root.winfo_screenheight()

        # create black canvas
        np_canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        # size the image to fit the canvas
        h, w, _ = cv2_img.shape
        new_w, new_h = self.scale_image_to_fit_screen(screen_width, screen_height, w, h)
        resized = cv.resize(cv2_img, (new_w, new_h))

        # center the image in the canvas
        x_offset = (screen_width - new_w) // 2
        y_offset = (screen_height - new_h) // 2
        np_canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

        cv.imshow(self.WINDOW_NAME, np_canvas)

    def main(self):
        """
        Main function that initializes the display window, loads configuration, and shows images sequentially.
        """
        config_mgr = ConfigMgr()
        self.config = config_mgr.load_config()
        if self.config["full_screen"]:
            cv.namedWindow(self.WINDOW_NAME, cv.WND_PROP_FULLSCREEN)
            cv.setWindowProperty(self.WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        else:
            cv.namedWindow(self.WINDOW_NAME, cv.WINDOW_NORMAL)
            cv.resizeWindow(self.WINDOW_NAME, 640, 480)

        last_image_time = time.time() - 86400
        min_display_duration = self.parse_display_duration()
        save_dir_path = self.config["save_directory_path"]

        # initially, we will show a random image previously rendered
        # so that we avoid showing a blank screen while the next
        # image is fetched from the AI
        print(f"Initial image from disk at {save_dir_path}")
        current_image: cv2.typing.MatLike = self.get_random_image_from_disk()
        self.display_image(current_image)
        _ = cv.waitKey(1000)  # Wait 1 second for the image to display

        while True:
            if time.time() - last_image_time >= min_display_duration or current_image is None:
                print("Timer expired; getting new image.")
                screen_xy = (self.tk_root.winfo_screenwidth(), self.tk_root.winfo_screenheight())
                # purge older files from image_out
                self.delete_oldest_files(self.config["save_directory_path"], int(self.config["max_num_saved_files"]))
                # generate random prompt and use it to generate an image
                # then write it to disk
                current_image_path: Path = self.image_generator.generate_image(screen_xy, save_dir_path)
                print(f"New image from disk at {str(current_image_path)}")
                if current_image_path is not None:
                    # send the image to S3
                    self.s3_manager.upload_to_s3(current_image_path)
                    # read the new image off disk
                    current_image = self.get_image_from_disk(current_image_path)
                    if current_image is not None:
                        self.display_image(current_image)
                # reset time in all cases so we don't flood AI services
                last_image_time = time.time() # secs since epoch

            key = cv.waitKey(250)  # Wait for key press

            if key == ord('q') or key == ord('Q'):
                return  # Quit the application
            elif key == ord('f') or key == ord('F'):
                # go full screen
                cv.namedWindow(self.WINDOW_NAME, cv.WND_PROP_FULLSCREEN)
                cv.setWindowProperty(self.WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
                cv.waitKey(200)
                # remember choice in config
                self.config["full_screen"] = True
                # write config
                config_mgr.save_config(self.config)
            elif key == ord('s') or key == ord('S'):
                # Destroy the existing fullscreen window
                cv.destroyWindow(self.WINDOW_NAME)
                # Create new window in normal mode
                cv.namedWindow(self.WINDOW_NAME, cv.WINDOW_NORMAL)
                cv.resizeWindow(self.WINDOW_NAME, 640, 480)
                # Display current image in new window
                self.display_image(current_image)
                cv.waitKey(200)
                # remember choice in config
                self.config["full_screen"] = False
                # write config
                config_mgr.save_config(self.config)
            elif key == ord('o') or key == ord('O'):
                # Open the options dialog
                config_mgr.show_options_dialog(self.config)
                min_display_duration = self.parse_display_duration()

            time.sleep(0.2)  # in seconds


if __name__ == '__main__':
    print("Service started!", file=sys.stdout, flush=True)
    load_dotenv()

    app = ImagineImage()
    app.main()
