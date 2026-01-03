from src.mem_ai.env_tools import config
from src.mem_ai.ai_platform.plat_factory import LLMModelFactory, register_llm_method
from src.mem_ai.ai_platform.plat_dashscope import DashScopeProvider
from src.mem_ai.memory import MemoryAI
from src.mem_ai.ai_platform.pmot_gen import generateGeneralAnswerQuestion
from icecream import ic
import json


def test_llm_dim():
    llm = LLMModelFactory.get_llm(config.PLATFORM)
    assert llm.txt2embeddingsDim() == 1024


def test_llm_memory():
    memory = MemoryAI()
    llm = LLMModelFactory.get_llm(config.PLATFORM)
    question = "你好，我叫Jerry.s"
    user_id = "jerry.s.d"
    session_id = ""
    ic(f"----------Long Memory Search Start------------")
    question_context, session_id, summary_result, message_ids = memory.get_memory(
        question, user_id, session_id
    )
    ic(question_context)
    ic(session_id)
    ic(summary_result)
    ic(message_ids)
    ic(f"----------Long Memory Search End------------")
    ic(f"----------Answer Start------------")
    # for idx, r in enumerate(used_memory_content):
    #     ic(r)

    # 开始提问
    answer_res = llm.llmcall(
        generateGeneralAnswerQuestion(question, json.dumps(question_context[-10:]))
    )
    ic(answer_res)
    ic("----------Answer End------------")
    ic("----------Long Memory Add Start ------------")
    memory.set_memory(
        question, answer_res, user_id, session_id, message_ids, summary_result
    )
    ic("----------Long Memory Add End------------")
    assert answer_res != None


if __name__ == "__main__":
    test_llm_memory()
