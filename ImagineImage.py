import os
import random
import sys
import time
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from dotenv import load_dotenv

from ConfigMgr import ConfigMgr
from ImageGenerator import ImageGenerator
from PromptGenerator import PromptGenerator
from S3Manager import S3Manager


class ImagineImage:
    CONFIG_FILE = Path(ConfigMgr.LOCAL_CONFIG_FILE_NAME)

    def __init__(self):
        # Initialize TKInter root
        self.tk_root = tk.Tk()
        self.tk_root.title("Imagine Image")
        self.tk_root.geometry("800x600")
        # Create a label to display the image
        self.tk_label = tk.Label(self.tk_root)
        self.tk_label.pack(fill=tk.BOTH, expand=True)

        self.config = None
        self.config_mgr = ConfigMgr()
        api_key = os.environ["OPEN_AI_SECRET"]
        self.prompt_generator = PromptGenerator(config_mgr=self.config_mgr, api_key=api_key)
        self.image_generator = ImageGenerator(prompt_generator=self.prompt_generator, api_key=api_key)
        self.s3_manager = S3Manager()

        # Bind key events for interaction
        self.tk_root.bind("<Key>", self.on_key)

        self.current_image = None  # Will hold a PIL Image
        self.last_image_time = time.time() - 86400  # Force immediate update

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
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

    def scale_image_to_fit_screen(self, screen_w: int, screen_h: int, img_w: int, img_h: int) -> tuple[int, int]:
        scale = min(screen_w / img_w, screen_h / img_h)
        return int(img_w * scale), int(img_h * scale)

    def get_random_image_from_disk(self) -> Image.Image | None:
        theme_dir_name = self.config["active_theme"].replace(".yaml", "")
        image_dir = Path(self.config["save_directory_path"]) / theme_dir_name
        if not (image_dir.exists() and image_dir.is_dir()):
            print(f"{image_dir} not found.")
            return None
        images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg"))
        if len(images) == 0:
            print(f"No images found in {str(image_dir)}")
            return None
        image_path = random.choice(images)
        return self.get_image_from_disk(image_path)

    def get_image_from_disk(self, path_to_image_file: Path) -> Image.Image | None:
        try:
            pil_img = Image.open(str(path_to_image_file))
            pil_img = pil_img.convert("RGB")
            return pil_img
        except Exception as e:
            print(f"Failed to load {path_to_image_file}: {e}")
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
        Resize the given PIL image to fit within the current TKInter window while preserving its
        aspect ratio, center it on a background of the given color, and update the display.
        """
        if pil_img is None:
            print("display_image_tk: Received None image")
            return

        # Force update to get the current dimensions of the label widget.
        self.tk_root.update_idletasks()
        window_width = self.tk_label.winfo_width()
        window_height = self.tk_label.winfo_height()

        # If the label hasn't been rendered yet, fallback to the root dimensions or defaults.
        if window_width <= 1 or window_height <= 1:
            window_width = self.tk_root.winfo_width()
            window_height = self.tk_root.winfo_height()
        if window_width <= 1 or window_height <= 1:
            window_width, window_height = 800, 600

        # Create a background canvas using Pillow.
        r, g, b = ImagineImage.hex_to_rgb(bkgd_hex_color)
        canvas = Image.new("RGB", (window_width, window_height), (r, g, b))

        # Get original image size.
        orig_w, orig_h = pil_img.size
        # Calculate new dimensions to fit within the window while preserving aspect ratio.
        new_w, new_h = self.scale_image_to_fit_screen(window_width, window_height, orig_w, orig_h)
        # Resize using LANCZOS (the modern replacement for ANTIALIAS).
        resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Center the resized image on the canvas.
        x_offset = (window_width - new_w) // 2
        y_offset = (window_height - new_h) // 2
        canvas.paste(resized, (x_offset, y_offset))

        # Convert the canvas to a PhotoImage and update the label.
        tk_image = ImageTk.PhotoImage(canvas)
        self.tk_label.config(image=tk_image)
        self.tk_label.image = tk_image  # Keep a reference.

    def on_key(self, event):
        """
        Handle key events:
          - 'q': quit
          - 'f': fullscreen
          - 's': windowed mode
          - 'o': open options dialog
        """
        key = event.keysym.lower()
        if key == 'q':
            self.tk_root.quit()
        elif key == 'f':
            self.tk_root.attributes("-fullscreen", True)
            self.config["full_screen"] = True
            self.config_mgr.save_config(self.config)
        elif key == 's':
            self.tk_root.attributes("-fullscreen", False)
            self.config["full_screen"] = False
            self.config_mgr.save_config(self.config)
        elif key == 'o':
            self.config = self.config_mgr.load_config()
            self.config_mgr.show_options_dialog(self.config)

    def update_image(self):
        """
        Periodically update the displayed image. If the display duration has elapsed
        or no image is loaded, obtain a new image from disk or generate one.
        """
        min_display_duration = self.parse_display_duration()
        now = time.time()

        if now - self.last_image_time >= min_display_duration or self.current_image is None:
            print("Timer expired; getting new image.")
            self.config = self.config_mgr.load_config()
            self.delete_oldest_files(self.config["save_directory_path"], int(self.config["max_num_saved_files"]))

            if self.config["local_files_only"]:
                self.current_image = self.get_random_image_from_disk()
            else:
                screen_xy = (self.tk_root.winfo_screenwidth(), self.tk_root.winfo_screenheight())
                output_file_info: [Path, Path] = self.image_generator.generate_image(screen_xy,
                                                                                     self.config["save_directory_path"])
                image_path: Path = output_file_info[0]
                prompt_path: Path = output_file_info[1]
                print(f"New image from disk at {str(image_path)}")
                if image_path is not None:
                    s3_key_img = f"{self.prompt_generator.get_theme_name()}/{os.path.basename(image_path)}"
                    print(f"Saving image to S3 at {s3_key_img}")
                    self.s3_manager.upload_to_s3(image_path, s3_key_img)
                    s3_key_prompt = f"{self.prompt_generator.get_theme_name()}/{os.path.basename(prompt_path)}"
                    print(f"Saving prompt to S3 at {s3_key_prompt}")
                    self.s3_manager.upload_to_s3(prompt_path, s3_key_prompt)
                    self.current_image = self.get_image_from_disk(image_path)
            self.last_image_time = now

        # Update the TKInter display with the current image.
        self.display_image_tk(self.current_image, self.config["background_color"])
        self.tk_root.after(250, self.update_image)

    def main(self):
        """
        Load configuration and start the TKInter main loop.
        """
        config_mgr = ConfigMgr()
        self.config = config_mgr.load_config()
        self.tk_root.after(0, self.update_image)
        self.tk_root.mainloop()


if __name__ == '__main__':
    print("Service started!", file=sys.stdout, flush=True)
    load_dotenv()
    app = ImagineImage()
    app.main()
