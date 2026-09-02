import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT = int(os.environ.get("PORT", 5001))
    DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
    ENV = os.environ.get("ENV", "development")

    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.environ.get("DB_NAME", "intucate_prompt_db")

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
    USE_MOCK_LLM = os.environ.get("USE_MOCK_LLM", "false").lower() in ("true", "1", "yes")

    DEFAULT_PROMPT_ID = "Education_Prompt"

    @classmethod
    def is_mock_llm(cls):
        """Returns True if we should use Mock LLM instead of real OpenAI."""
        if cls.USE_MOCK_LLM:
            return True
        if not cls.OPENAI_API_KEY:
            return True
        return False
