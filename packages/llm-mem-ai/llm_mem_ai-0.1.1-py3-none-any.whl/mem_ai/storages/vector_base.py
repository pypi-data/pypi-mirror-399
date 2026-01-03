from abc import ABC, abstractmethod
from typing import List


class VectorProvider(ABC):
    """
    向量存储
    """

    # @abstractmethod
    # def uploadPoints(self, documents):
    #     """
    #     批量写入知识库Points

    #     :param self: 说明
    #     :param documents: 说明
    #     """
    #     pass

    # @abstractmethod
    # def uploadSummaryPoint(self, document, point_id):
    #     """
    #     更新Summary Point

    #     :param self: 说明
    #     :param document: 说明
    #     :param point_id: 说明

    #     """
    #     pass

    # @abstractmethod
    # def uploadSummaryPoints(self, documents):
    #     """
    #     批量更新Summary Points

    #     :param self: 说明
    #     :param documents: 说明
    #     """
    #     pass

    # @abstractmethod
    # def queryPoints(
    #     self, query, prefetch=None, query_filter=None, with_payload=False, limit=3
    # ):
    #     """
    #     根据条件查询Points

    #     :param self: 说明
    #     :param query: 说明
    #     :param prefetch: 说明
    #     :param query_filter: 说明
    #     :param with_payload: 说明
    #     :param limit: 说明
    #     """
    #     pass

    @abstractmethod
    def search_memory_process(
        self,
        vector,
        meta,
        session_id,
        user_id,
        score=0.4,
        limit=5,
    ):
        """
        记忆操作

        :param self: 说明
        :param vector: 说明
        :param meta: 说明
        :param session_id: 说明
        :param user_id: 说明
        :param score: 说明
        :param limit: 说明
        """
        pass

    @abstractmethod
    def add_memory_process(self, documents, point_id=None):
        pass
