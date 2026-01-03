from mem_ai.env_tools import config
from mem_ai.ai_platform.plat_factory import LLMModelFactory, register_llm_method
from mem_ai.ai_platform.plat_dashscope import DashScopeProvider
from mem_ai.memory import MemoryAI
from mem_ai.ai_platform.pmot_gen import generateGeneralAnswerQuestion
import json
from icecream import ic


def test_llm_memory():
    memory = MemoryAI()
    llm = LLMModelFactory.get_llm(config.PLATFORM)
    question = "我想了解一下Springboot能做什么呢？"
    user_id = "jerry.s.d"
    session_id = ""
    ic("----------Long Memory Search Start------------")
    question_context, session_id, summary_result, message_ids = memory.get_memory(
        question, user_id, session_id
    )
    ic(question_context)
    ic(session_id)
    ic(summary_result)
    ic(message_ids)
    ic("----------Long Memory Search End------------")
    ic("----------Answer Start------------")
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


if __name__ == "__main__":
    test_llm_memory()
