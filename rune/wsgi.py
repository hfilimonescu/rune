from dotenv import load_dotenv

from rune import create_app

# Load the default config files, just like `flask run` does
load_dotenv('.flaskenv')
load_dotenv('.env')


application = app = create_app()
