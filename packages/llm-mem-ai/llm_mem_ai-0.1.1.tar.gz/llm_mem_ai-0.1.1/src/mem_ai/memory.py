from typing import List
from src.mem_ai.storages.mem_summary import MemorySummary
from src.mem_ai.env_tools import config
from src.mem_ai.storages.mongo_help import Mongo
from src.mem_ai.ai_platform.plat_factory import LLMModelFactory
from src.mem_ai.storages.vector_factory import VectorFactory
from src.mem_ai.ai_platform.pmot_gen import (
    generateMetaMsg,
    generateUpdateSummaryAnswerQuestion,
    generateSummaryAnswerQuestion,
)
import json
from icecream import ic
from qdrant_client.models import (
    Distance,
)


class MemoryAI:
    def __init__(self):
        self.llm = LLMModelFactory.get_llm(config.PLATFORM)
        vector_config = {"distance": Distance.COSINE}
        self.vector = VectorFactory.get_vector(config.VECTOR, **vector_config)

    def get_memory(self, context, user_id, session_id=None, score=0.7):
        """
        记忆处理
        """
        # 存储原始对话信息
        message_ids, session_id = self._save_mongo_context(
            context=context, user_id=user_id, session_id=session_id
        )
        # 标准化问题数据
        question_qdrant_results = self._summary_question_context(
            context=context, user_id=user_id, session_id=session_id
        )
        question_context, summary_result = self._get_memory_context(
            question_qdrant_results, score
        )
        return question_context, session_id, summary_result, message_ids

    def set_memory(
        self,
        question_context,
        answer_context,
        user_id,
        session_id,
        message_ids=[],
        summary_result=None,
        mongo_collection=config.MONGO_COLLECTION,
    ):
        """
        set_memory 的 Docstring

        :param self: 说明
        """

        message_ids = self._append_mongo_context(
            context=answer_context,
            session_id=session_id,
            message_ids=message_ids,
            mongo_collection=mongo_collection,
        )
        if summary_result:
            """使用了中心思想记忆 ，追加新的聊天内容以及更新中心思想"""
            if summary_result.payload:
                doc_summary_session_id = summary_result.payload.get("session_id", None)
                doc_summary_user_id = summary_result.payload.get("user_id", None)
                doc_summary_message_ids: List[str] = summary_result.payload.get(
                    "message_ids", []
                )
                doc_summary_summary = summary_result.payload.get("summary", None)
                doc_summary_meta: List[str] = summary_result.payload.get("meta", [])
                summary_res = self.llm.llmcall(
                    generateUpdateSummaryAnswerQuestion(
                        doc_summary_summary,
                        json.dumps(
                            [
                                {"role": "user", "content": question_context},
                                {"role": "bot", "content": answer_context},
                            ]
                        ),
                    )
                )
                if summary_res:
                    json_summary = json.loads(summary_res)
                    # 合并消息ID
                    doc_summary_message_ids.extend(message_ids)
                    # 合并Meta
                    doc_summary_meta.extend(json_summary["meta"])
                    # 生成Summary 向量
                    query_ver = self.llm.txt2embeddings([json_summary["summary"]])[0]
                    doc: MemorySummary = MemorySummary(
                        summary=json_summary["summary"],
                        session_id=session_id,
                        user_id=user_id,
                        message_ids=doc_summary_message_ids,  # 需要去重复么？
                        meta=list(set(doc_summary_meta)),
                    )
                    self.vector.add_memory_process(
                        point_id=summary_result.id, documents=doc
                    )

        else:
            """未使用中心思想记忆，新建中心思想"""
            """为新的对话生成中心思想"""
            summary_res = self.llm.llmcall(
                generateSummaryAnswerQuestion(
                    json.dumps(
                        [
                            {"role": "user", "content": question_context},
                            {"role": "bot", "content": answer_context},
                        ]
                    )
                )
            )
            # 根据summary进行召回
            if summary_res:
                json_summary = json.loads(summary_res)
                # 生成Summary 向量
                # query_ver = self.llm.txt2embeddings([json_summary["summary"]])[0]
                doc: MemorySummary = MemorySummary(
                    summary=json_summary["summary"],
                    session_id=session_id,
                    user_id=user_id,
                    message_ids=message_ids,
                    meta=json_summary["meta"],
                )
                self.vector.add_memory_process(documents=[doc])

    def _get_mongo_context(
        self, message_ids, user_id, session_id, mongo_collection=config.MONGO_COLLECTION
    ):
        """
        查询MongoDB中的聊天记录

        :param self: 说明
        :param message_ids: 说明
        :param user_id: 说明
        :param session_id: 说明
        :param mongo_collection: 说明
        """
        mongo = Mongo(collection=mongo_collection)
        messages = mongo.get_summary_record_message(user_id, session_id, message_ids)
        return messages

    def _save_mongo_context(
        self,
        context,
        user_id,
        session_id=None,
        mongo_collection=config.MONGO_COLLECTION,
    ):
        """
        Mongo保存消息原始信息，Mongo进行存储,可以返回真正的聊天记录，如果不开启那只返回summary内容

        :param self: 说明
        :param context: 说明
        :param user_id: 说明
        :param session_id: 说明
        :param mongo_collection: 说明
        """
        message_ids = []
        if config.OPEN_CONTEXT_SAVE:
            # TODO 改为全局连接更好
            mongo = Mongo(collection=mongo_collection)
            # 写入用户会话
            if session_id:
                user_mongo_res = mongo.append_message_to_session(
                    new_message={"role": "user", "content": context},
                    session_id=session_id,
                )
                session_id = user_mongo_res["session_id"]
                message_ids.extend(user_mongo_res["message_ids"])
            else:
                user_mongo_res = mongo.insert_chat_record(
                    user_id=user_id, messages=[{"role": "user", "content": context}]
                )
                session_id = user_mongo_res["session_id"]
                message_ids.extend(user_mongo_res["message_ids"])
        return message_ids, session_id

    def _append_mongo_context(
        self,
        context,
        session_id,
        message_ids=[],
        mongo_collection=config.MONGO_COLLECTION,
    ):
        """
        AI回答后的结果追加

        :param self: 说明
        :param context: 说明
        :param session_id: 说明
        :param message_ids: 说明
        """
        if config.OPEN_CONTEXT_SAVE:
            mongo = Mongo(collection=mongo_collection)
            bot_mongo_res = mongo.append_message_to_session(
                new_message={"role": "bot", "content": context}, session_id=session_id
            )
            message_ids.extend(bot_mongo_res["message_ids"])
        return message_ids

    def _summary_question_context(self, context, session_id, user_id):
        """
        加工处理问题总结

        :param self: 说明
        :param context: 说明
        :param session_id: 说明
        :param user_id: 说明
        """
        question_meta_res = self.llm.llmcall(generateMetaMsg(context))
        # 有返回值
        if question_meta_res:
            json_question_meta_res = json.loads(question_meta_res)
            question_query_vector = self.llm.txt2embeddings([context])[0]
            return self.vector.search_memory_process(
                question_query_vector, json_question_meta_res, session_id, user_id
            )
        else:
            """TODO 语言模型调用失败"""
            return []

    def _get_memory_context(self, question_results, score=0.7):
        question_context = []
        summary_result = None
        # 有用的上下文
        if len(question_results) > 0:
            # for idx, r in enumerate(question_results):
            #     ic(r)
            question_result = max(question_results, key=lambda o: o.score)
            if question_result and question_result.score > score:
                summary_result = question_result
                # 可以作为上下文使用
                if question_result.payload:
                    question_session_id = question_result.payload.get(
                        "session_id", None
                    )
                    question_user_id = question_result.payload.get("user_id", None)
                    question_message_ids = summary_result.payload.get("message_ids", [])
                    # 根据消息ID查询Mongo的原始消息
                    if (
                        question_session_id
                        and question_user_id
                        and len(question_message_ids) > 0
                    ):
                        if config.OPEN_CONTEXT_SAVE:
                            # 启用Mongo时返回历史聊天信息
                            messages = self._get_mongo_context(
                                question_message_ids,
                                question_user_id,
                                question_session_id,
                            )
                            for message in messages:
                                for q_msg in question_message_ids:
                                    for msg in message["messages"]:
                                        if msg["message_id"] == q_msg:
                                            question_context.append(msg)
                        else:
                            # 不启用Mongo时只返回Summary信息
                            question_context.append(
                                summary_result.payload.get("summary", None)
                            )
        return question_context, summary_result
