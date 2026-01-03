from mem_ai.ai_platform.plat_base import LLMModelProvider


class LLMModelFactory:
    _llms = {}

    @classmethod
    def get_llm(cls, method: str, **init_kwargs) -> LLMModelProvider:
        llm_class = cls._llms.get(method.lower())
        if not llm_class:
            raise ValueError(f"不支持的模型: {method}")
        # 使用传入的关键字参数实例化
        return llm_class(**init_kwargs)


def register_llm_method(name: str, llm_class: type):
    if not issubclass(llm_class, LLMModelProvider):
        raise TypeError("必须继承自 LLMModelProvider")
    LLMModelFactory._llms[name.lower()] = llm_class
