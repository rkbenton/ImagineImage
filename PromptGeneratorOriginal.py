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
            "Generate a creative image prompt involving a stand of birch trees.",
            "Generate an image prompt of a stand of birch trees.",
            "Generate an image prompt of a forest.",
            "Generate an image prompt of a lake.",
            "Generate a creative image prompt with a cute puppy.",
            "Generate a creative image prompt with a cute cat.",
            "Generate an image prompt in the style of Thomas Kinkade.",
            "Generate an image prompt with a castle.",
            "Generate an image prompt of a girl reading a book.",
            "Generate an image prompt with a sentimental old car.",
            "Generate an image prompt with a cubist smiling woman.",
            "Generate an image prompt with a cubist avuncular gentleman.",
            "Generate an image prompt of a romantic couple dancing.",
            "Generate an image prompt of for an infinite grid of tessellated cubes.",
            "Generate an image prompt featuring an ancient tree with glowing runes.",
            "Generate a creative image prompt of a futuristic cityscape at dusk.",
            "Generate an image prompt of a mysterious library with floating books.",
            "Generate a creative image prompt of a lighthouse standing against a storm.",
            "Generate an image prompt featuring a hidden door covered in ivy.",
            "Generate a creative image prompt of an enchanted mirror reflecting another world.",
            "Generate an image prompt of a market street in a cyberpunk world.",
            "Generate an image prompt of a traveler standing before a vast, alien landscape.",
            "Generate an image prompt of a dimly lit café at midnight, steam rising from a lone cup of coffee, painted in soft impressionist brushstrokes.",
            "Generate an image prompt of a forgotten library with dust particles floating in golden light, books stacked haphazardly on an antique wooden desk.",
            "Generate an image prompt of a quiet city street after rain, neon reflections shimmering on the pavement, in a minimalist cyberpunk style.",
            "Generate an image prompt of a lone figure sketching in a notebook under a flickering streetlamp, soft pencil lines blending into the evening mist.",
            "Generate an image prompt of a vintage record player spinning an old vinyl, bathed in warm amber light, painted in a moody noir palette.",
            "Generate an image prompt of an old typewriter by a window, the paper filled with half-written poetry, with sunlight casting long shadows.",
            "Generate an image prompt of a cozy reading nook with an overstuffed chair, a half-empty teacup, and an open book under a dim lamp glow.",
            "Generate an image prompt of a film-inspired still of a woman looking out of a rain-streaked train window, her reflection blending with the blurred landscape.",
            "Generate an image prompt of a single candle flickering on a windowsill, illuminating the edges of dried flowers in a glass bottle.",
            "Generate an image prompt of a jazz musician playing the saxophone on a quiet rooftop, the soft city glow in the background, captured in deep chiaroscuro."
            "Generate an image prompt of a misty forest at dawn, where golden sunlight barely pierces through the dense canopy, casting soft, diffused shadows.",
            "Generate an image prompt of a lonely lighthouse standing against a vast, overcast sea, waves crashing gently against the cliffs in a muted color palette.",
            "Generate an image prompt of a desert at twilight, the last rays of sun painting the dunes in soft purples and deep oranges, with a single silhouette in the distance.",
            "Generate an image prompt of a fog-covered mountain range, where jagged peaks fade into the mist, captured in soft monochrome tones.",
            "Generate an image prompt of a meadow filled with wildflowers swaying in a light breeze, distant rolling hills barely visible under a dreamy golden haze.",
            "Generate an image prompt of a quiet lakeshore at midnight, the surface of the water reflecting the full moon, with only the ripples of a drifting leaf breaking the sGenerate an image prompt of aillness.",
            "Generate an image prompt of an autumn pathway lined with towering trees, their golden leaves scattered across the damp earth, disappearing into the morning fog.",
            "Generate an image prompt of a coastal cliff-side overlooking the ocean, with sea spray drifting into the air and seagulls gliding effortlessly above the waves.",
            "Generate an image prompt of a frozen tundra under the Northern Lights, where ice-covered rocks shimmer faintly in hues of green and violet.",
            "Generate an image prompt of a secluded waterfall hidden within an overgrown jungle, its clear waters cascading into a serene, crystal-blue pool surrounded by moss-covered stones."
            "Generate an image prompt of a mother and daughter dressed in Victorian garb having tea at a cafe in a modern setting.",
            "Generate an image prompt of snow falling on a conifer forest in the mountains",
            "Generate an image prompt of butterflies flying through a forest",
            "Generate an image prompt of a cheerful country cabin",
            "Generate an image prompt of a picturesque abandoned barn",
            "Generate an image prompt of a magic fountain in the middle of the desert",
            "Generate an image prompt of an oasis",
            "Generate an image prompt of a herd of horses majestically running across the Scottish moors",
            "Generate an image prompt of a humpback whale breaching a beautiful ocean",
            "Generate an image prompt of a diorama of a cute, overstuffed bookshop",
            "Generate an image prompt of a diorama of a flower shop",
            "Generate an image prompt of a single origami crane casting a long shadow on textured washi paper, morning light filtering through a window",
            "Generate an image prompt of abandoned ballet slippers on weathered wooden floorboards, dust particles floating in a shaft of sunlight",
            "Generate an image prompt of rain droplets on a coffee shop window at dusk, the neon signs outside creating bokeh effects through the glass",
            "Generate an image prompt of a vintage bicycle leaning against a moss-covered stone wall, ivy creeping around its wheels",
            "Generate an image prompt of scattered polaroid photos on a white bedsheet, soft morning light creating gentle shadows",
            "Generate an image prompt of a half-finished cup of tea with steam rising, sitting on a stack of worn poetry books",
            "Generate an image prompt of dried flowers pressed between the pages of an old journal, muted colors and delicate textures",
            "Generate an image prompt of a solitary streetlamp in fog, its light creating a soft halo in the mist",
            "Generate an image prompt of paint-stained hands holding a ceramic bowl, captured from above on a rustic wooden table",
            "Generate an image prompt of autumn leaves scattered across weathered piano keys, warm afternoon light streaming in",
            "Generate an image prompt of a single thread of spider silk catching morning dew, macro shot with natural bokeh",
            "Generate an image prompt of artist's brushes in a mason jar, silhouetted against a sunset-lit studio window"
            "Generate an image prompt of a dusty box of childhood toys in an attic, sunbeams highlighting a well-loved teddy bear",
            "Generate an image prompt of faded summer polaroids spread on a gingham picnic blanket, corners soft with age",
            "Generate an image prompt of an old drive-in movie theater at twilight, the neon sign flickering to life",
            "Generate an image prompt of a worn baseball glove and yellowed baseball cards on weathered wooden bleachers",
            "Generate an image prompt of grandmother's cookie jar on a vintage formica countertop, afternoon light streaming through lace curtains",
            "Generate an image prompt of rusted roller skates hanging from a tree branch, wildflowers growing beneath",
            "Generate an image prompt of a stack of handwritten letters tied with faded ribbon, postmarks from the 1960s visible",
            "Generate an image prompt of an old metal lunchbox with superhero designs, slightly rusted but still colorful",
            "Generate an image prompt of vinyl records scattered around a retro record player, dust motes dancing in sunset light",
            "Generate an image prompt of a forgotten treehouse with wind-worn wooden planks, childhood drawings still visible inside",
            "Generate an image prompt of an old carousel horse in storage, chipped paint revealing layers of colors underneath",
            "Generate an image prompt of a View-Master with scattered photo reels, casting colored shadows through stained glass",
            "Generate an image prompt of a weathered piano with childhood stickers still clinging to its sides, sheet music yellowed with age",
            "Generate an image prompt of bubble wands and chalk on a sun-bleached concrete porch, remnants of summer days past"
            "Generate an image prompt of a tiny door at the base of an ancient oak tree, with a welcome mat made of moss and toadstools",
            "Generate an image prompt of butterflies delivering mail between flowering teacups, each wing sealed with a tiny wax stamp",
            "Generate an image prompt of a friendly dragon running a bakery, wearing a flour-dusted apron while frosting cloud-shaped cookies",
            "Generate an image prompt of woodland creatures having a midnight tea party, fireflies providing the lighting",
            "Generate an image prompt of a rabbit librarian organizing books on shelves made of twisting tree branches, using a ladder of moonbeams",
            "Generate an image prompt of a family of mice living in a pumpkin house, with windows that glow warm and bright at dusk",
            "Generate an image prompt of garden gnomes painting rainbows onto morning dewdrops, using flower petals as their palettes",
            "Generate an image prompt of a gentle giant carefully watering his collection of tiny bonsai villages",
            "Generate an image prompt of mermaids running a floating ice cream parlor, serving sundaes on lily pads",
            "Generate an image prompt of stars being hung in the night sky by sleepy owls wearing night caps",
            "Generate an image prompt of a fox teaching young woodland creatures how to dance, using mushrooms as dance floor markers",
            "Generate an image prompt of cloud shepherds herding fluffy cumulus clouds with ribbons of sunlight",
            "Generate an image prompt of a witch's familiar running a cozy cat café, serving potions in teacups to magical creatures"
            "Generate an image prompt of a many-armed monster working as a professional gift wrapper, each arm holding different ribbons and papers with cheerful precision",
            "Generate an image prompt of a giant sea monster running a floating bed and breakfast, serving seaweed pancakes from its tentacle-kitchen",
            "Generate an image prompt of a shy cave monster who collects crystals, showing off his sparkling collection with gentle claws and a proud smile",
            "Generate an image prompt of a three-headed monster braiding each other's hair while sharing ice cream cones, all heads with different favorite flavors",
            "Generate an image prompt of a furry mountain monster operating a ski lodge, wearing a hand-knitted sweater and serving hot chocolate from his snow-cave",
            "Generate an image prompt of a group of small monsters having a pillow fight, floating feathers revealing their colorful hiding spots",
            "Generate an image prompt of a spotted monster running a lost and found for missing socks, carefully matching pairs with their tiny tentacles",
            "Generate an image prompt of a monster kindergarten teacher helping little monsters learn to control their friendly roars",
            "Generate an image prompt of a tall, gangly monster working as a crossing guard for fairy tale creatures, using its stretchy arms as safety barriers",
            "Generate an image prompt of a monster librarian with dozens of eyes, each reading a different book to small creatures at storytime",
            "Generate an image prompt of a fluffy monster running a cloud-brushing service, carefully grooming clouds into fun shapes",
            "Generate an image prompt of a gentle giant monster tending to a garden of night-blooming flowers, wearing tiny reading glasses to inspect each bloom"
            "Generate an image prompt of steam rising from a fresh espresso, curling into the shape of sleepy clouds while morning light catches the mist",
            "Generate an image prompt of a stack of pancakes catching golden sunlight, maple syrup slowly dripping down like amber waterfalls",
            "Generate an image prompt of a French press full of coffee viewed from above, creating a spiral galaxy of cream and coffee",
            "Generate an image prompt of morning light filtering through honey being drizzled onto warm toast, creating prismatic amber patterns",
            "Generate an image prompt of a perfectly poached egg breaking open, yolk flowing like liquid gold across artisanal sourdough",
            "Generate an image prompt of coffee beans scattered across weathered wood, morning sunbeams creating long shadows between each bean",
            "Generate an image prompt of a morning scene of croissant flakes catching light like gold leaf, beside a swirling café au lait",
            "Generate an image prompt of fresh berries tumbling onto yogurt, creating marble-like swirls in slow motion",
            "sunlight through a mason jar of orange juice, creating prisms across a rustic wooden breakfast table",
            "Generate an image prompt of a coffee cup on a windowsill, steam rising to meet the morning fog outside",
            "Generate an image prompt of butter melting on a hot waffle, creating rivers of gold between perfectly crisp squares",
            "Generate an image prompt of a barista crafting a leaf pattern in foam, captured at the moment the design completes",
            "Generate an image prompt of morning pastries in a vintage bakery case, soft bokeh from string lights reflecting in the glass",
            "Generate an image prompt of a spoon drizzling honey into tea, capturing the moment the golden spiral meets the surface",
            "Generate an image prompt of a cool animal listening contentedly to vinyl records on ultra high-end audio gear"
            "Generate an image prompt of a tired astronaut having a tea party with aliens on the moon, their helmets decorated with teacups",
            "Generate an image prompt of an old telephone booth in a field of wildflowers, its light glowing at dusk as butterflies circle",
            "Generate an image prompt of a jazz band of cats playing on a rooftop, their instruments gleaming in the sunset",
            "Generate an image prompt of a time-traveling mailman delivering letters between centuries, his bag spilling postcards from different eras",
            "Generate an image prompt of an ancient library where books float and rearrange themselves, dust motes sparkling like stars",
            "Generate an image prompt of a garden of clockwork flowers that chime on the hour, gears visible through glass petals",
            "Generate an image prompt of a whale swimming through clouds, trailing stardust and northern lights",
            "Generate an image prompt of a lighthouse keeper reading stories to seabirds, each bird wearing tiny reading glasses",
            "Generate an image prompt of a train station for paper airplanes, with tiny pilots checking their flight schedules",
            "Generate an image prompt of an underwater bicycle repair shop run by octopi, using bubbles as tool boxes",
            "Generate an image prompt of a grandmother teaching young clouds how to make snow, using knitting needles made of moonlight",
            "Generate an image prompt of a city built inside a massive terrarium, with tiny gardeners tending to the glass walls",
            "Generate an image prompt of a night market where dreams are sold in bottles, each one glowing a different color",
            "Generate an image prompt of a cartographer drawing maps of imaginary places, his ink creating real landscapes as it dries",
            "Generate an image prompt of a sleeping giant being used as a mountain range, complete with tiny ski lodges on his shoulders",
            "Generate an image prompt of a traveling circus performed by shadows, using the moon as their spotlight",
            "Generate an image prompt of a post office sorting room for lost wishes, each one carefully wrapped in starlight",
            "Generate an image prompt of a violin player serenading a garden, the flowers swaying to match each note",
            "Generate an image prompt of a collector of forgotten memories storing them in seashells along a beach",
            "Generate an image prompt of a repair shop for broken rainbows, with color swatches and light prisms everywhere",
            "Generate an image prompt of a group of trees practicing their autumn colors like actors rehearsing for a play",
            "Generate an image prompt of a seamstress sewing the edges of reality together, using threads made from sunset colors",
            "Generate an image prompt of a professor teaching young comets how to streak across the night sky with style",
            "Generate an image prompt of a windchime maker testing their creations with bottled breezes from different seasons",
            "Generate an image prompt of a collector of lost socks running a matchmaking service to reunite pairs"
        ]

        self.subjects = [
            "lighthouse", "tree", "library", "clock", "mirror", "book",
            "city", "garden", "mountain", "ocean", "bird", "door",
            "mountain scape", "rocky shoreline", "busy city street",
            "taxicab", "campfire", "bridge", "lantern", "castle", "waterfall",
            "train station", "cathedral", "harbor", "windmill", "statue", "cave",
            "country tavern", "thatched roof cottage", "castle", "shipwreck", "observatory",
            "tower", "fountain", "tunnel", "desert", "island", "forest path", "marketplace",
            "library", "book"
        ]

        self.attributes = [
            "crystal", "mechanical", "floating", "ancient", "luminous",
            "paper", "giant", "miniature", "ethereal", "forgotten",
        ]

        self.actions = [
            "growing", "transforming", "dissolving", "emerging",
            "dancing", "floating", "merging", "unfolding", "resting",
            "reflecting"
        ]

        self.settings = [
            "in a dream", "under starlight", "between dimensions",
            "in the mist", "during an eclipse", "through time",
            "in reverse", "across seasons", "by a lake", "in the mountains",
            "medieval village", "medieval village square"
        ]

        self.heroic_animals = [
            "eagle", "bear", "tiger", "lion", "bison", "whale", "husky", "horse",
            "osprey", "jaguar", "wolf", "moose", "dragon", "cattle dog", "unicorn",
            "badger", "husky", "gryphon"
        ]

        self.cute_animals = [
            "puppy", "dog", "kitten", "cat", "otter", "penguin", "squirrel", "panda",
            "quokka", "capybara", "rabbit", "fox", "hedgehog", "giraffe"
        ]

        self.artists = [
            "Pablo Picasso", "Alexander Calder", "Leonardo da Vinci", "Michelangelo",
            "Claude Monet", "Rembrandt van Rijn", "Frida Kahlo", "Diego Rivera",
            "Charles Rennie Mackintosh", "Gustav Klimt", "Henri de Toulouse-Lautrec",
            "Alphonse Mucha", "Georgia O'Keeffe", "Norman Rockwell", "Jean Giraud",
            "Brothers Hildebrandt", "Edward Hopper", "Gustave Courbet", "John Singer Sargent",
            "Johannes Vermeer", "Katsushika Hokusai", "Caravaggio", "Raphael"
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
        elif random.randrange(0, 100) <= 50:
            system_prompt = """You are a creative assistant specializing in generating highly descriptive 
            and unique prompts for creating images. Ensure the prompts are vivid and imaginative."""
            user_prompt_raw = self.build_from_simple_prompts()
            user_prompt = f"Original prompt: \"{user_prompt_raw}\"\nRewrite it to make it more detailed and unique."
        else:
            system_prompt = """You are a creative assistant specializing in generating highly descriptive 
            and unique prompts for creating images. Ensure the prompts are vivid, imaginative, and unexpected."""
            user_prompt_raw = random.choice(
                [self.build_basic, self.build_from_simple_prompts, self.build_with_style, self.build_animal])()
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
            generated_prompt = self.build_from_simple_prompts()

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

    def build_from_simple_prompts(self) -> str:
        """Returns a completely random pre-defined prompt."""
        return random.choice(self.simple_prompts)
