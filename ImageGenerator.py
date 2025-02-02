import os
import random
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image
from openai import OpenAI

from PromptGenerator import PromptGenerator


class ImageGenerator:

    def __init__(self):
        api_key = os.environ["OPEN_AI_SECRET"]
        self.client = OpenAI(api_key=api_key)
        self.prompt_generator = PromptGenerator()

    def get_image_prompt(self):
        system_prompt = """You are a creative assistant generating extremely random and unique image prompts. 
        Avoid common themes. Focus on unexpected, unconventional, and bizarre combinations 
        of art style, medium, subjects, time periods, and moods. No repetition. Prompts 
        should be 20 words or less and specify random artist, movie, tv show or time period 
        for the theme. Do not provide any headers or repeat the request, just provide the 
        updated prompt in your response."""

        user_prompt_fn = random.choice([
            self.prompt_generator.generate_basic,
            self.prompt_generator.generate_really_random,
            self.prompt_generator.generate_with_style
        ])
        user_prompt: str = user_prompt_fn()

        print(f"user_prompt: {user_prompt}")

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1
        )
        return response.choices[0].message.content.strip()

    def generate_dalle_image(self, prompt: str, port_xy: tuple[int, int]):
        # DALL·E 3 was trained to only generate
        # 1024x1024, 1024x1792 or 1792x1024
        # try to set aspect ratio according to the shape of the port
        if port_xy[0] == port_xy[1]:
            img_siz = "1024x1024"
        elif port_xy[0] > port_xy[1]:
            img_siz = "1792x1024"
        else:
            img_siz = "1024x1792"

        response = self.client.images.generate(
            model="dall-e-3",  # ["dall-e-3", "dall-e-2"]
            prompt=prompt,
            size=img_siz,
            quality="standard",  # ["hd", "standard"]
            n=1,
        )
        image_url = response.data[0].url

        # Download and convert image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img

    def generate_image(self, port_xy: tuple[int, int] = (1024, 1024),
                       image_directory: str = "image_out") -> Image.Image:
        try:
            # Get prompt from ChatGPT
            prompt = self.get_image_prompt()
            print(f"Generated prompt: {prompt}")

            # Generate image with DALL-E
            img = self.generate_dalle_image(prompt, port_xy)

            # save the image using the current datetime
            formatted_date = datetime.now().strftime("%Y%m%dT%H%M%S")
            img.save(f"{image_directory}/{formatted_date} output_image.png")
            with open(f"{image_directory}/{formatted_date} prompt.txt", 'w') as f:
                try:
                    f.write(prompt)
                except IOError as e:
                    print(f"Error writing to file: {e}")

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return img


        except Exception as e:
            print(f"Error generating image: {e}")
            return None
