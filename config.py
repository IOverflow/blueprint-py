from dotenv import load_dotenv
import os


def config():
    load_dotenv()
    development = os.getenv("ENVIRONMENT") != "Production"

    if development:
        pass
    else:
        pass
