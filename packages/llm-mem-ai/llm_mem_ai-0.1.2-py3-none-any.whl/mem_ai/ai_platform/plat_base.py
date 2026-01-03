from abc import ABC, abstractmethod
from typing import List


class LLMModelProvider(ABC):
    """
    LLMModelProvider 模型的抽象类
    """

    @abstractmethod
    def llmcall(self, messages, json=False, stream=False):
        pass

    @abstractmethod
    def txt2embeddings(self, inputs) -> List[List[float]]:
        """
        输入的内容向量化
        
        :param self: LLMModelProvider
        :param inputs: 文本信息
        :return: 多维度向量
        :rtype: List[List[float]]
        """
        pass

    @abstractmethod
    def txt2embeddingsDim(self) -> int:
        """
        获取设定模型维度
        
        :param self: LLMModelProvider
        :return: dim
        :rtype: int
        """
        pass
