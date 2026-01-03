# config.py
import os
from dotenv import load_dotenv
from icecream import ic

load_dotenv()


class MemEnvConfig:
    # AI LLM Model
    PLATFORM = os.getenv("PLATFORM", "dashscope")
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv(
        "BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ).lower()
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
    EMBEDDING_MODEL_DIM = int(os.getenv("EMBEDDING_MODEL_DIM", 1024))
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "yes"]

    # Vector
    VECTOR = os.getenv("VECTOR", "qdrant")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "mem_collection")
    # Mongo
    OPEN_CONTEXT_SAVE = os.getenv("OPEN_CONTEXT_SAVE", "False").lower() in [
        "true",
        "1",
        "yes",
    ]
    # mongodb://chat:chat@localhost:27017/chat_database?authSource=admin
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:mongo@localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "mem_database")
    MONGO_AUTH = os.getenv("MONGO_AUTH", "admin")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "mem_collection")
    MONGO_URI = (
        f"{MONGO_URL}/{MONGO_DB}?authSource={MONGO_AUTH}"
        if MONGO_AUTH
        else f"{MONGO_URL}/{MONGO_DB}"
    )

    @classmethod
    def validate(cls):
        if cls.PLATFORM == "dashscope" and not cls.API_KEY:
            raise ValueError("API_KEY is required!")
        if cls.VECTOR == "qdrant":
            if not cls.QDRANT_URL:
                raise ValueError("QDRANT_URL is required!")
        if cls.OPEN_CONTEXT_SAVE == True:
            if not cls.MONGO_URL or not cls.MONGO_DB or not cls.MONGO_COLLECTION:
                raise ValueError("Mongo save is Open and Mongo's info is required!")


config = MemEnvConfig()
config.validate()
if config.DEBUG == True:
    ic(f"PLATFORM:{config.PLATFORM}")
    ic(f"API_KEY:{config.API_KEY}")
    ic(f"BASE_URL:{config.BASE_URL}")
    ic(f"LLM_MODEL:{config.LLM_MODEL}")
    ic(f"EMBEDDING_MODEL:{config.EMBEDDING_MODEL}")
