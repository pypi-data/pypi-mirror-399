from mem_ai.ai_platform.plat_base import LLMModelProvider
from typing import List
from openai import OpenAI
from mem_ai.env_tools import config
from icecream import ic


class DashScopeProvider(LLMModelProvider):

    def __init__(self):
        client = OpenAI(
            api_key=config.API_KEY,
            base_url=config.BASE_URL,
        )
        self.client = client

    def llmcall(self, messages, json=False, stream=False):
        completion = self.client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=stream,
        )
        if json:
            return completion.model_dump_json()
        else:
            return completion.choices[0].message.content

    def txt2embeddings(self, inputs) -> List[List[float]]:
        res: List[List[float]] = []
        for inp in inputs:
            embed: List[float] = []
            completion = self.client.embeddings.create(
                model="text-embedding-v4",
                input=inp,
                dimensions=1024,
                encoding_format="float",
            )
            embeddings_data = completion.data
            for data in embeddings_data:
                embed.extend(data.embedding)
            res.append(embed)
        return res

    def txt2embeddingsDim(self):
        return config.EMBEDDING_MODEL_DIM
