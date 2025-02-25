import os
import os.path
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI


class ManualGenerator:

    def __init__(self):
        api_key = os.environ["OPEN_AI_SECRET"]
        self.client = OpenAI(api_key=api_key)

    @staticmethod
    def read_file(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content: str = file.read()
            return content
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except PermissionError:
            print(f"Error: No permission to read '{file_path}'.")
            return None
        except UnicodeDecodeError:
            # Try different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                return content
            except Exception as e:
                print(f"Error: Failed to decode file '{file_path}': {e}")
                return None
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            return None

    def get_image_from_dall_e(self, prompt: str, port_xy: tuple[int, int]) -> Image:
        """
        Sends the prompt and fetches an image from OpenAI's DALL·E service.

        :param prompt: The image prompt to send.
        :param port_xy: The size of the target viewport (width, height).
        :return: A PIL Image object or None on error.
        """
        # Define image size based on aspect ratio
        if port_xy[0] == port_xy[1]:
            img_siz = "1024x1024"
        elif port_xy[0] > port_xy[1]:
            img_siz = "1792x1024"
        else:
            img_siz = "1024x1792"

        # https://cookbook.openai.com/examples/dalle/image_generations_edits_and_variations_with_dall-e
        try:
            response = self.client.images.generate(
                model="dall-e-3",  # Choose between "dall-e-3" or "dall-e-2"
                prompt=prompt,
                size=img_siz,  # type: ignore
                quality="standard",  # Options: "hd", "standard"
                n=1,
            )
            image_url = response.data[0].url
        except Exception as e:
            print("Error fetching image url:", e)
            return None

        # Download and convert the image
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error fetching from {image_url}:", e)
            return None

        return img

    def produce_awesomeness(self, prompt_file_path: str, port_xy: tuple[int, int] = (1792, 1024),
                            output_dir: str = "experimental_output") -> [Path, Path]:
        """
        Generates an image and saves it to the specified directory.

        :param prompt_file_path: The path to the prompt.
        :param port_xy: The size of the target viewport (width, height).
        :param output_dir: The directory where output data is saved.
        :return: 2-part tuple; first part is the Path to the generated image
        file or None on error; second part is the Path to the saved prompt.
        """
        os.makedirs(output_dir, exist_ok=True)

        full_prompt = self.read_file(prompt_file_path)

        # Fetch the generated image
        img: Image = self.get_image_from_dall_e(full_prompt, port_xy)
        if img is not None:

            # Save image and prompt to disk, prefixing with timestamp
            formatted_date = datetime.now().strftime("%Y%m%dT%H%M%S")
            img_path = Path(output_dir, f"{formatted_date}_output_image.png")
            prompt_path = Path(output_dir, f"{formatted_date}_prompt.txt")

            # Save image as PNG
            try:
                img.save(img_path)
                print(f"Image saved to '{img_path}'")
            except IOError as e:
                print(f"Error writing image to file {img_path}: {e}")
                return None

            # Save prompt as text file (non-critical, but useful)
            try:
                with open(prompt_path, 'w') as f:
                    f.write(full_prompt)
                print(f"Prompt saved to '{prompt_path}'")
            except IOError as e:
                print(f"Error writing prompt to file {prompt_path}: {e}")
        else:
            print("Error: Failed to get image.")


if __name__ == "__main__":
    print("Service started!", file=sys.stdout, flush=True)
    load_dotenv()
    mg = ManualGenerator()
    mg.produce_awesomeness("experimental_prompts/floating_heads_poster.md")
    print("Done!", file=sys.stdout, flush=True)