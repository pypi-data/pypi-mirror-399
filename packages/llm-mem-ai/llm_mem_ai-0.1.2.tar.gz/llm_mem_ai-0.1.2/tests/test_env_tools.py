from mem_ai.env_tools import config
from icecream import ic

def test_env_debug():
    assert config.DEBUG == True


def test_env_llm_model():
    assert config.LLM_MODEL == "qwen-plus"

def test_env_url():
    assert config.BASE_URL == "https://dashscope.aliyuncs.com/compatible-mode/v1"

def test_env_dim():
    assert config.EMBEDDING_MODEL_DIM == 1024

if __name__ == "__main__":
    ic(config.__dict__)
