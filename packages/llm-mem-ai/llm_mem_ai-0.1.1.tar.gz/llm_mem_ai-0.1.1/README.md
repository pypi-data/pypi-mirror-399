# llm-mem

## 项目简介

- 想制作一个简单可行的对话存储的记忆模块，可以分层，可以混合检索，当用户提问时可以命中局部记忆内容
- 这里使用的模型为阿里云百炼，dashscope.aliyuncs.com，其他平台会慢慢兼容

## 安装方法

## 使用示例

```python
# How to run
def test_llm_memory():
    memory = MemoryAI()
    
    question = "我想了解一下Springboot能做什么呢？"
    user_id = "jerry.s.d"
    session_id = ""

    # 获取长期记忆 question_context 为上下文的消息列表(可根据情况自行加工)
    question_context, session_id, summary_result, message_ids = memory.get_memory(
        question, user_id, session_id
    )

    # TODO 这里是正常调用语言模型的逻辑，或者智能体， 使用question_context 构建自己的上下文即可
    # 开始提问
    answer_res = "Do some function call LLM "

    # 追加新的信息进入长期记忆
    memory.set_memory(
        question, answer_res, user_id, session_id, message_ids, summary_result
    )
```

```conf
# .env相关配置
# =========== 模型相关配置 ===========
# dashscope 目前只兼容了dashscope
PLATFORM = "dashscope"
API_KEY ="sk-"
BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL="qwen-plus"
EMBEDDING_MODEL="text-embedding-v4"
EMBEDDING_MODEL_DIM=1024

# =========== 向量数据库相关配置 ===========
# qdrant 目前只兼容了qdrant
VECTOR = "qdrant"
QDRANT_URL = "http://localhost:6333"
QDRANT_API_KEY = "xxxxx"
QDRANT_COLLECTION = "mem_collection"
# =========== Mongo文档库相关配置 ===========
# 开启后自动存储聊天内容, TODO 对于False的情况，还没有进行测试
OPEN_CONTEXT_SAVE = "True"
# mongodb://chat:chat@localhost:27017/chat_database?authSource=admin
MONGO_URL = "mongodb://mongo:mongo@localhost:27017"
MONGO_DB = "mem_database"
MONGO_AUTH = "admin"
MONGO_COLLECTION = "mem_collection"

# 其他配置
DEBUG="False"
```

## Collaborate with your team
