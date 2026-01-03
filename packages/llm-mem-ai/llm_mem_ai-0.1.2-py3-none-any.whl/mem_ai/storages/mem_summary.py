import json
from typing import List


class MemorySummary:
    """记忆体对象"""

    def __init__(
        self, summary, session_id, user_id, message_ids: List[str], meta: List[str]
    ):
        self.summary = summary
        self.session_id = session_id
        self.user_id = user_id
        self.message_ids: List[str] = message_ids
        self.meta: List[str] = meta


def parse_memory_summary(dct):
    return MemorySummary(**dct)


def readJson(json_path: str):
    with open(json_path, "r", encoding="utf-8") as file:
        docs = json.load(file, object_hook=parse_memory_summary)
    return docs
