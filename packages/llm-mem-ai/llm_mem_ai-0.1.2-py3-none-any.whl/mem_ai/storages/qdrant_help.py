from mem_ai.ai_platform.plat_factory import LLMModelFactory
from mem_ai.storages.vector_base import VectorProvider
from mem_ai.env_tools import config
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    NearestQuery,
    VectorParams,
    Distance,
    PayloadSchemaType,
    Mmr,
    FormulaQuery,
    Prefetch,
    SumExpression,
    MultExpression,
    PointStruct,
)
from qdrant_client import QdrantClient
import uuid
from icecream import ic


class qdrantHelp(VectorProvider):
    """
    qdrantHelp 的 Docstring
    """

    def __init__(
        self, collection_name=config.QDRANT_COLLECTION, distance=Distance.COSINE
    ):
        client = (
            QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
            if config.QDRANT_API_KEY
            else QdrantClient(url=config.QDRANT_URL)
        )
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config.EMBEDDING_MODEL_DIM, distance=distance
                ),
            )
        llm = LLMModelFactory.get_llm(config.PLATFORM)
        self.client = client
        self.collection_name = collection_name
        self.llm = llm

    # 写向量数据
    def _upload_points(self, documents):
        """批量写入知识库Points"""
        points_res = []
        for idx, doc in enumerate(documents):
            id = str(uuid.uuid4())
            vtc = self.llm.txt2embeddings([doc.summary])[0]
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=id,
                        vector=vtc,
                        payload=doc.__dict__,
                    )
                ],
            )
            points_res.append(operation_info)
        return points_res

    def _upload_summary_point(self, point_id, document):
        """更新Summary Point"""
        vtc = self.llm.txt2embeddings([document.summary])[0]
        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vtc,
                    payload=document.__dict__,
                )
            ],
        )
        return operation_info

    # 写向量数据
    def _upload_summary_points(self, documents):
        """更新Summary Points"""
        points_res = []
        for idx, doc in enumerate(documents):
            id = str(uuid.uuid4())
            vtc = self.llm.txt2embeddings([doc.summary])[0]
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=id,
                        vector=vtc,
                        payload=doc.__dict__,
                    )
                ],
            )
            points_res.append(operation_info)
        return points_res

    # 查询Points
    def _query_points(
        self, query, prefetch=None, query_filter=None, with_payload=False, limit=3
    ):
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=prefetch,
            query=query,
            query_filter=query_filter,
            with_payload=with_payload,
            limit=limit,
        ).points
        return search_result

    def search_memory_process(
        self,
        vector,
        meta,
        session_id,
        user_id,
        score=0.4,
        limit=5,
    ):
        question_prefetch = Prefetch(query=vector, limit=limit)
        query = FormulaQuery(
            formula=SumExpression(
                sum=[
                    "$score",
                    MultExpression(
                        mult=[
                            score,
                            FieldCondition(
                                key="meta",
                                match=MatchAny(any=meta["meta"]),
                            ),
                        ]
                    ),
                ]
            )
        )
        query_filter = Filter(
            must=[
                FieldCondition(key="session_id", match=MatchValue(value=session_id)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            ]
        )
        question_qdrant_results = self._query_points(
            query=query,
            query_filter=query_filter,
            prefetch=question_prefetch,
            with_payload=True,
            limit=limit,
        )
        return question_qdrant_results

    def add_memory_process(self, documents, point_id=None):
        """
        追加记忆

        :param self: 说明
        :param point_id: 说明
        :param documents: 说明
        """
        if point_id:
            return self._upload_summary_point(point_id, documents)
        else:
            return self._upload_points(documents)
