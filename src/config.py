import os


def config():
    development = os.getenv("ENVIRONMENT") != "Production"

    if development:
        pass
    else:
        pass
