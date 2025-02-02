from dotenv import load_dotenv

from PygameApp import PygameApp

if __name__ == "__main__":
    load_dotenv()
    pygame_app = PygameApp()
    pygame_app.run()
