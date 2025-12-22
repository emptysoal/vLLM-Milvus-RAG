"""

"""

# Milvus 配置
MILVUS_URI = "http://192.168.0.235:19530"
COLLECTION_NAME = "hybrid_search"

# 模型服务
LLM_ENDPOINT = "http://192.168.0.230:32804/v1"
LLM_MODEL_NAME = "/workspace/models/Qwen2.5-3B-Instruct"
EMBEDDING_ENDPOINT = "http://192.168.0.230:32805/v1"
EMBEDDING_MODEL_NAME = "/workspace/models/BAAI/bge-m3"
RERANKER_ENDPOINT = "http://192.168.0.230:32806"
RERANKER_MODEL_NAME = "/workspace/models/BAAI/bge-reranker-v2-m3"

# 搜索参数
DEFAULT_LIMIT = 5
DEFAULT_SCORE_THRESHOLD = 0.5
CANDIDATE_MULTIPLIER = 1.5

# LLM参数
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.8
LLM_MAX_TOKENS = 512

# 大模型对话提示词参数
QUERY_SYSTEM_PROMPT = """你是一个专业的问答助手。请根据以下上下文回答问题：

{context}

## 回答要求：
1. 如果上下文与问题相关，请基于上下文给出准确回答
2. 如果上下文与问题无关，请基于你的知识回答
3. 保持回答简洁、专业
4. 如果上下文信息不足，可以适当补充说明
"""

# 大模型优化查询提示词参数
REWRITE_SYSTEM_PROMPT = """你是非常强大的助手，能够根据历史对话信息把用户当前提问的问题补充完整，使得当前提问在不结合上下文语境的情况下也能完整地表达语义，
你可以参考这个例子：
历史对话为：[{"role": "user", "content": "今天北京的天气怎么样？"}, 
{"role": "assistant", "content": "今天北京是晴天，气温20摄氏度。"}]
用户当前提问为："上海呢？"
你的输出可以是："上海今天的天气是雨天，气温25摄氏度。"
也就是说你能灵活地判断用户当前的提问是否完整，如果不完整则根据历史对话把提问补充成一个独立完整的问题。

## 限制
只输出补全后的提问，不要输出任何其他内容
"""
REWRITE_USER_PROMPT = """判断下面的问题是否完整，如果不完整并且存在历史对话，请利用历史对话补全，
历史对话:
{history}

当前提问:
{query}
"""
