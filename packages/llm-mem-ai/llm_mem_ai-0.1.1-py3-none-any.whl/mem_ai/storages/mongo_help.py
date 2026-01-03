from typing import List
from pymongo import MongoClient
import uuid
from bson.binary import Binary
from datetime import datetime
from src.mem_ai.env_tools import config
from icecream import ic

class Mongo:
    def __init__(self, collection=config.MONGO_COLLECTION, db=config.MONGO_DB):
        # 1. 连接到 MongoDB 本地服务
        _client = MongoClient(config.MONGO_URI)
        # 2. 创建数据库和集合（集合名：chat_records）
        _db = _client[db]
        _collection = _db[collection]
        self.client = _client
        self.db = _db
        self.collection = _collection

    # 3. 插入聊天记录
    def insert_chat_record(
        self,
        user_id,
        messages,
        app_id="default",
        session_id=None,
    ):
        if not session_id:
            session_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_ids: List[str] = []
        for msg in messages:
            message_id = str(uuid.uuid4())
            message_ids.append(message_id)
            msg["message_id"] = message_id
            msg["timestamp"] = created_at
        record = {
            "app_id": app_id,
            "user_id": user_id,
            "session_id": session_id,
            "messages": messages,
            "created_at": created_at,
        }
        self.collection.insert_one(record)
        return {"session_id": session_id, "message_ids": message_ids}

    # 4. 查询所有与指定用户相关的聊天记录
    def find_chats_by_user(self, user_id):
        results = self.collection.find({"user_id": user_id})
        return results

    # 5. 查询指定会话的聊天记录
    def find_chat_by_session(self, session_id):
        doc = self.collection.find_one({"session_id": session_id})
        return doc

    # 6. 追加消息到现有会话（可选）
    def append_message_to_session(self, session_id, new_message):
        message_id = str(uuid.uuid4())
        new_message["message_id"] = message_id
        new_message["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.collection.update_one(
            {"session_id": session_id}, {"$push": {"messages": new_message}}
        )
        return {"session_id": session_id, "message_ids": [message_id]}

    def get_summary_record_message(
        self, user_id: str, session_id: str, message_ids: list[str]
    ):
        query = {
            "user_id": user_id,
            "session_id": session_id,
            "messages.message_id": {"$in": message_ids},
        }
        results = self.collection.find(query)
        return list(results)
