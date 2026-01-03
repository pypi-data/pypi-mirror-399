from mem_ai.storages.vector_factory import register_vector_method
from mem_ai.storages.qdrant_help import qdrantHelp

register_vector_method("qdrant", qdrantHelp)
