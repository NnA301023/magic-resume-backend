import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    TS_HOST = os.getenv("TYPESENSE_HOST", None)
    TS_PORT = os.getenv("TYPESENSE_PORT", None)
    TS_KEY  = os.getenv("TYPESENSE_API_KEY", None)
    TS_COL  = os.getenv("TYPESENSE_COLLECTION", None)

    API_KEY = os.getenv("GROQ_API_KEY", None)
    MODEL_NAME = os.getenv("MODEL_NAME", None)
    YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY", None)

settings = Settings()