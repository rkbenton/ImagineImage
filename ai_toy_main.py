import sys
import os
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from datetime import datetime
from dotenv import load_dotenv


class ImageGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        api_key = os.environ["OPEN_AI_SECRET"]
        self.client = OpenAI(api_key = api_key)
        self.setWindowTitle("AI Image Generator")
        self.setGeometry(100, 100, 1024, 1200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # Create buttons
        generate_button = QPushButton("Generate")
        generate_button.clicked.connect(self.generate_image)
        layout.addWidget(generate_button)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        # Generate initial image
        self.generate_image()

    def get_image_prompt(self):
        system_prompt = """You are a creative assistant generating extremely random and unique image prompts. 
        Avoid common themes. Focus on unexpected, unconventional, and bizarre combinations 
        of art style, medium, subjects, time periods, and moods. No repetition. Prompts 
        should be 20 words or less and specify random artist, movie, tv show or time period 
        for the theme. Do not provide any headers or repeat the request, just provide the 
        updated prompt in your response."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate a creative image prompt."}
            ],
            temperature=1
        )
        return response.choices[0].message.content.strip()

    def generate_dalle_image(self, prompt):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # Download and convert image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img

    def generate_image(self):
        try:
            # Get prompt from ChatGPT
            prompt = self.get_image_prompt()
            print(f"Generated prompt: {prompt}")

            # Generate image with DALL-E
            img = self.generate_dalle_image(prompt)

            # save the image
            # Get current datetime
            formatted_date = datetime.now().strftime("%Y%m%dT%H%M%S")
            img.save(f"image_out/{formatted_date} output_image.png")

            # Convert PIL Image to QPixmap and display
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            # Scale pixmap to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(1024, 1024, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"Error generating image: {e}")


def main():

    # https://pypi.org/project/python-dotenv/
    # load_dotenv()  # load .env vars into environment variables
    # Make sure OPENAI_API_KEY environment variable is set
    if 'OPEN_AI_SECRET' not in os.environ:
        print("Please set OPENAI_API_KEY environment variable")
        return

    app = QApplication(sys.argv)
    window = ImageGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()