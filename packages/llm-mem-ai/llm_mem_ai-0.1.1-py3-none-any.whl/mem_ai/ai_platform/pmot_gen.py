from icecream import ic


def generateMetaMsg(content):
    """
    生成写入向量库的title以及meta，
    是否也要生成一些问题？
    """
    prompt = f"""
    你是一个内容理解专家，可以总结提炼对话内容。一定要包含关于事件描述的关键信息，比如人物，时间，地点，对话的中心思想等必要信息。并突出显示所有提到的实体、实体类型、事实和关键信息，比如人名、地名、日期、数字等。总结时必须包含这些值，并标记为关键事实。并且生成一些关于对话内容可能被提问的问题。比如：用户提到 “我叫XXXX”,这时可以生成的问题“我刚才说我叫什么名字？”
    ### 要求：
    1. 数据结构必须符合JSON Schema结构：
    {{
        "title": "字符串，包含对话的总结内容，包括关键事实和生成的问题",
        "meta": ["字符串数组，包含从总结中提取的标签，重点关注实体、类型、事实和关键信息"]
    }}
    - "title"属性为字符串，存储的内容为总结提炼对话内容,包括关键事实和生成的问题。
    - “meta”属性为字符串数组，提取规则为对总结提炼对话内容打出合理的标签，特别关注提到的实体、实体类型，事实和关键信息，包括人名、地名、日期、数字等。标签需要是多个，并给出一些与标签词义相近的同义词，比如，“人名”，“姓名”。
    2. 只输出JSON对象，不要输出其他任何额外文本。保证JSON语法正确。
    """
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": content,
        },
    ]
    return messages


def generateQuestionMsg(question, context=""):
    """
    问题扩写
    """
    prompt = f"""
    你是一个内容理解专家，擅长理解用户的问题，并进行提问扩写。
    要求：
    1. 基于上下文背景分析理解用户问题。上下文:{context}
    2. 将用户问题不改变愿意的情况下保留原始问题，并扩写3个相似问题。
    3. 数据结果以json字符串数组形式输出，只输出JSON对象，不要输出其他任何额外文本。保证JSON语法正确。
    json字符串示例: ["原始问题","扩写问题1","扩写问题2","扩写问题3"]
    """
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": question,
        },
    ]
    return messages


def generateAnswerQuestion(question, context=""):
    """
    问题回答
    """
    prompt = f"""
    你是一个内容理解专家，擅长理解并回答用户的问题。
    要求：
    1. 基于上下文背景分析并回答用户问题。上下文:{context}
    2. 回答要有合理的上下文依据，不可以凭空捏造，不需要建议。如果上下文不存在，请回答请转人工咨询。
    3. 如果用户提问的问题意图不明确，不能命中单条上下文，或者不匹配上下文描述的内容，这时需要结合上下文进行反问提问，让用户补全意图直到意图明确，或者可直接建议转人工咨询。
    3. 上下中的很多名称为专有名称，不要随意修正，比如，金牌助手，金牌顾问
    4. 输出原文引用

    """
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": question,
        },
    ]
    return messages


def generateGeneralAnswerQuestion(question, context=""):
    """
    问题回答
    """
    prompt = f"""
    你是一个通用问题回答助手。如果有上下问：{context},请参照上下文回答，并输出上下文引用。如果没有，则直接回答。

    """
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": question,
        },
    ]
    return messages


def generateSummaryAnswerQuestion(context):
    """中心思想总结"""
    prompt = f"""
    你是一个内容理解专家，可以总结提炼对话内容。一定要包含关于事件描述的关键信息，比如人物，时间，地点，对话的中心思想等必要信息。并突出显示所有提到的实体、实体类型、事实和关键信息，比如人名、地名、日期、数字等。总结时必须包含这些值，并标记为关键事实。并且生成一些关于对话内容可能被提问的问题。比如：用户提到 “我叫XXXX”,这时可以生成的问题“我刚才说我叫什么名字？”
    ### 要求：
    1. 数据结构必须符合JSON Schema结构：
    {{
        "summary": "字符串，包含对话的总结内容，包括关键事实和生成的问题",
        "meta": ["字符串数组，包含从总结中提取的标签，重点关注实体、类型、事实和关键信息"]
    }}
    - "summary"属性为字符串，存储的内容为总结提炼对话内容,包括关键事实和生成的问题。
    - “meta”属性为字符串数组，提取规则为对总结提炼对话内容打出合理的标签，特别关注提到的实体、实体类型，事实和关键信息，包括人名、地名、日期、数字等。标签需要是多个，并给出一些与标签词义相近的同义词，比如，“人名”，“姓名”。
    2. 只输出JSON对象，不要输出其他任何额外文本。保证JSON语法正确。
    ### 补充：对话的数据结构说明，
    1. 数据结构为： [
        {{
            "role": "bot",
            "content": "",
        }},
        {{
            "role": "user",
            "content": "",
        }},
    ]
    - 'role'='user'的content为用户说的内容
    - 'role'='bot'的content为机器人说话的内容
    """
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": context,
        },
    ]
    return messages


def generateUpdateSummaryAnswerQuestion(summary, context):
    """中心思想总结"""
    prompt = f"""
    你是一个内容理解专家，需要在现有背景信息基础上,追加并总结对话内容。需要包含关于事件描述的关键信息，变化信息，比如人物，时间，地点，对话的中心思想等必要信息。
    ### 现有背景信息如下：
    {summary}

    ### 总结要求：
    1. 数据结构必须符合JSON Schema结构：
    {{
        "summary": "",
        "meta": [""],
    }}
    - "summary"属性为字符串，存储的内容为总结提炼对话内容。
    - “meta”属性为字符串数组，提取规则为对总结提炼对话内容打出合理的标签，可以是多个。
    2. 只输出JSON对象，不要输出其他任何额外文本。保证JSON语法正确。
    ### 补充：对话的数据结构说明，
    1. context数据结构为： [
        {{
            "role": "bot",
            "content": "",
        }},
        {{
            "role": "user",
            "content": "",
        }},
    ]
    - 'role'='user'的content为用户说的内容
    - 'role'='bot'的content为机器人说话的内容
    """
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": context,
        },
    ]
    return messages
