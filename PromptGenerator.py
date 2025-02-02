import random


class PromptGenerator:
    def __init__(self):
        self.simple_prompts: [str] = [
            "Generate a creative image prompt.",
            "Generate a creative image prompt involving a stand of birch trees.",
            "Generate a image prompt involving a forest.",
            "Generate a image prompt involving a lake.",
            "Generate a creative image prompt about a cute puppy.",
            "Generate a creative image prompt about a cute cat.",
            "Generate an image prompt in the style of Thomas Kinkade.",
            "Generate an image prompt with a castle.",
            "Generate an image prompt a girl reading a book.",
            "Generate an image prompt with a sentimental old car.",
            "Generate an image prompt with a cubist smiling woman.",
            "Generate an image prompt with a cubist avuncular gentleman.",
            "Generate an image prompt of a romantic couple dancing.",
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
            "in the mist", "during eclipse", "through time",
            "in reverse", "across seasons"
        ]

        self.styles = [
            "steampunk", "art nouveau", "cyberpunk", "baroque",
            "minimalist", "surrealist", "gothic", "watercolor",
            "streamline moderne", "cubist", "pointillist"
        ]

    def generate_basic(self) -> str:
        return f"A {random.choice(self.attributes)} {random.choice(self.subjects)} {random.choice(self.actions)} {random.choice(self.settings)}"

    def generate_with_style(self) -> str:
        return f"{random.choice(self.styles)} style: {self.generate_basic()}"

    def generate_really_random(self) -> str:
        return random.choice(self.simple_prompts)
