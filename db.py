import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock
from config import Config

logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None
    _is_mock = False

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                #MongoDB
                real_client = MongoClient(
                    Config.MONGO_URI,
                    serverSelectionTimeoutMS=2000,
                    connectTimeoutMS=2000
                )
                real_client.admin.command('ping')
                cls._client = real_client
                cls._db = cls._client[Config.DB_NAME]
                cls._is_mock = False
                logger.info("Connected to live MongoDB!")
            except Exception as err:
                #use in-memory fake DB
                logger.warning("MongoDB not found. Using in-memory mock DB. Error: %s", err)
                cls._client = mongomock.MongoClient()
                cls._db = cls._client[Config.DB_NAME]
                cls._is_mock = True
                cls.seed_default_prompts()

        return cls._client

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.get_client()
        return cls._db

    @classmethod
    def is_using_mock_db(cls):
        if cls._db is None:
            cls.get_client()
        return cls._is_mock

    @classmethod
    def get_prompts_collection(cls):
        return cls.get_db()["prompts"]

    @classmethod
    def get_history_collection(cls):
        return cls.get_db()["history"]

    @classmethod
    def seed_default_prompts(cls):
        prompts_col = cls.get_prompts_collection()
        default_prompt = {
            "_id": "Education_Prompt",
            "template": "You are an expert in education domain. Answer the following: {{userInput}}"
        }
        existing = prompts_col.find_one({"_id": "Education_Prompt"})
        if not existing:
            prompts_col.insert_one(default_prompt)
            logger.info("Seeded default prompt: Education_Prompt")

    @classmethod
    def ping(cls):
        try:
            db = cls.get_db()
            count = db["prompts"].count_documents({})
            return {
                "status": "connected",
                "is_in_memory_mock": cls._is_mock,
                "prompts_count": count
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
def get_db():
    return Database.get_db()

def seed_default_prompts(db=None):
    Database.seed_default_prompts()
