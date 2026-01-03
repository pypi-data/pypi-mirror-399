from src.mem_ai.storages.vector_base import VectorProvider


class VectorFactory:
    _vectors = {}

    @classmethod
    def get_vector(cls, method: str, **init_kwargs) -> VectorProvider:
        vector_class = cls._vectors.get(method.lower())
        if not vector_class:
            raise ValueError(f"不支持的模型: {method}")
        # 使用传入的关键字参数实例化
        return vector_class(**init_kwargs)


def register_vector_method(name: str, vector_class: type):
    if not issubclass(vector_class, VectorProvider):
        raise TypeError("必须继承自 VectorProvider")
    VectorFactory._vectors[name.lower()] = vector_class
