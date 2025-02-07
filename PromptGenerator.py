"""
Module: prompt_generator.py

This module defines a class `PromptGenerator` that generates creative image prompts
using OpenAI's API. It builds prompts based on various themes, styles, and
attributes, offering both random and structured prompt generation.
"""

import os
import random

from openai import OpenAI


class PromptGenerator:
    """
    A class for generating creative image prompts using OpenAI's API.
    It includes predefined subjects, attributes, actions, and styles for prompt construction.
    """

    def __init__(self):
        """
        Initializes the PromptGenerator with predefined lists and OpenAI API client.
        """
        api_key = os.environ["OPEN_AI_SECRET"]
        self.client = OpenAI(api_key=api_key)

        # Data for building priming prompts
        self.simple_prompts = [
            "Generate a creative image prompt.",
            "Generate a creative image prompt involving a stand of birch trees.",
            "Generate an image prompt involving a forest.",
            "Generate an image prompt involving a lake.",
            "Generate a creative image prompt about a cute puppy.",
            "Generate a creative image prompt about a cute cat.",
            "Generate an image prompt in the style of Thomas Kinkade.",
            "Generate an image prompt with a castle.",
            "Generate an image prompt of a girl reading a book.",
            "Generate an image prompt with a sentimental old car.",
            "Generate an image prompt with a cubist smiling woman.",
            "Generate an image prompt with a cubist avuncular gentleman.",
            "Generate an image prompt of a romantic couple dancing."
        ]

        self.subjects = [
            "lighthouse", "tree", "library", "clock", "mirror", "book",
            "city", "garden", "mountain", "ocean", "bird", "door",
            "mountain scape", "rocky shoreline", "busy city street",
            "taxicab"
        ]

        self.attributes = [
            "crystal", "mechanical", "floating", "ancient", "luminous",
            "paper", "giant", "miniature", "ethereal", "forgotten"
        ]

        self.actions = [
            "growing", "transforming", "dissolving", "emerging",
            "dancing", "floating", "merging", "unfolding", "resting"
        ]

        self.settings = [
            "in a dream", "under starlight", "between dimensions",
            "in the mist", "during an eclipse", "through time",
            "in reverse", "across seasons"
        ]

        self.heroic_animals = [
            "eagle", "bear", "tiger", "lion", "bison", "whale", "husky", "horse",
            "osprey", "jaguar", "wolf", "moose", "dragon", "cattle dog"
        ]

        self.cute_animals = [
            "puppy", "dog", "kitten", "cat", "otter", "penguin", "squirrel", "panda",
            "quokka", "capybara", "rabbit", "fox"
        ]

        self.artists = [
            "Pablo Picasso", "Alexander Calder", "Leonardo da Vinci", "Michelangelo",
            "Claude Monet", "Rembrandt van Rijn", "Frida Kahlo", "Diego Rivera",
            "Charles Rennie Mackintosh", "Gustav Klimt", "Henri de Toulouse-Lautrec",
            "Alphonse Mucha", "Georgia O'Keeffe"
        ]

        self.art_styles = [
            "Renaissance", "Baroque", "Rococo", "Neoclassicism", "Romanticism",
            "Impressionism", "Expressionism", "Cubism", "Surrealism", "Abstract Expressionism",
            "Minimalism", "watercolor", "art nouveau", "streamline moderne", "cubist", "pointillist"
        ]

    def get_image_prompt(self):
        """
        Generates an image prompt using OpenAI's API, either randomly or with a structured approach.

        :return: A creative image prompt as a string.
        """
        let_ai_create_by_itself = random.randrange(0, 100) <= 10
        if let_ai_create_by_itself:
            system_prompt = """You are a creative assistant generating extremely random and unique image prompts. 
            Avoid common themes. Focus on unexpected, unconventional, and bizarre combinations 
            of art style, medium, subjects, time periods, and moods. No repetition."""
            user_prompt = "Give me a completely random image prompt, something unexpected and creative!"
        else:
            system_prompt = """You are a creative assistant specializing in generating highly descriptive 
            and unique prompts for creating images. Ensure the prompts are vivid, imaginative, and unexpected."""
            user_prompt_raw = random.choice(
                [self.build_basic, self.build_really_random, self.build_with_style, self.build_animal])()
            user_prompt = f"Original prompt: \"{user_prompt_raw}\"\nRewrite it to make it more detailed and unique."

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=1
            )
            generated_prompt = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Failed to get prompt from AI: {e}")
            generated_prompt = self.build_really_random()

        return generated_prompt

    def build_animal(self):
        """Generates a prompt featuring an animal in a specific artistic style."""
        style = random.choice(self.art_styles) if random.randrange(0, 100) > 50 else random.choice(self.artists)
        subject = random.choice(self.cute_animals) if random.randrange(0, 100) > 50 else random.choice(
            self.heroic_animals)
        return f"A {subject} in the style of {style}"

    def build_basic(self) -> str:
        """Generates a simple descriptive prompt with an action and setting."""
        return f"A {random.choice(self.attributes)} {random.choice(self.subjects)} {random.choice(self.actions)} {random.choice(self.settings)}"

    def build_with_style(self) -> str:
        """Generates a stylized prompt with a selected art movement."""
        return f"{random.choice(self.art_styles)} style: {self.build_basic()}"

    def build_really_random(self) -> str:
        """Returns a completely random pre-defined prompt."""
        return random.choice(self.simple_prompts)
