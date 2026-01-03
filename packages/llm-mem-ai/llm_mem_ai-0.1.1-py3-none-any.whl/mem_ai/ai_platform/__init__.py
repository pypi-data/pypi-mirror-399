from src.mem_ai.ai_platform.plat_factory import register_llm_method
from src.mem_ai.ai_platform.plat_dashscope import DashScopeProvider

register_llm_method("dashscope", DashScopeProvider)
