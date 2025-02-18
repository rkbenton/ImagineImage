"""
Module: image_generator.py

This module defines a class `ImageGenerator` that generates images using OpenAI's DALL·E model.
It constructs prompts from the `PromptGenerator` and fetches images accordingly.
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image
from openai import OpenAI

from PromptGenerator import PromptGenerator


class ImageGenerator:
    """
    A class for generating images using OpenAI's DALL·E model.
    It integrates a `PromptGenerator` to construct creative prompts and fetches images accordingly.
    """

    def __init__(self, prompt_generator: PromptGenerator, api_key):
        """
        Initializes the ImageGenerator with OpenAI API client and a PromptGenerator instance.
        """
        self.client = OpenAI(api_key=api_key)
        self.prompt_generator = prompt_generator

    def get_image_from_service(self, prompt: str, port_xy: tuple[int, int]) -> Image:
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
                size=img_siz,
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

    def generate_image(self, port_xy: tuple[int, int] = (1024, 1024),
                       image_directory: str = "image_out") -> Path | None:
        """
        Generates an image and saves it to the specified directory.

        :param port_xy: The size of the target viewport (width, height).
        :param image_directory: The directory where the image will be saved.
        :return: Path to the generated image file or None on error.
        """
        # Generate local prompt data
        prompt_data: dict[str, str] = self.prompt_generator.generate_prompt()

        # Embellish the prompt using ChatGPT
        embellished_prompt = self.prompt_generator.embellish_prompt(
            prompt_data[PromptGenerator.FULL_PROMPT],
            prompt_data[PromptGenerator.SYSTEM_PROMPT])

        # Fetch the generated image
        img: Image = self.get_image_from_service(embellished_prompt, port_xy)
        if img is None:
            print("Image generation failed")
            return None

        # Save image and prompt to disk, prefixing with timestamp
        formatted_date = datetime.now().strftime("%Y%m%dT%H%M%S")
        img_path = Path(image_directory, f"{formatted_date}_output_image.png")
        prompt_path = Path(image_directory, f"{formatted_date}_prompt.txt")

        # Save image as PNG
        try:
            img.save(img_path)
        except IOError as e:
            print(f"Error writing image to file {img_path}: {e}")
            return None

        # Save prompt as text file (non-critical, but useful)
        try:
            with open(prompt_path, 'w') as f:
                f.write(embellished_prompt)
        except IOError as e:
            print(f"Error writing prompt to file {prompt_path}: {e}")

        return img_path
