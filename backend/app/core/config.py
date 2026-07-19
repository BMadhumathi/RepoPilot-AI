from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings:

    PROJECT_NAME = "RepoPilot AI"

    REPOSITORY_DIR = BASE_DIR.parent / "repositories"

    CHROMA_DB = BASE_DIR.parent / "chromadb"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


settings = Settings()

print("Loaded .env from:", ENV_PATH)
print("Gemini Key Found:", settings.GEMINI_API_KEY is not None)