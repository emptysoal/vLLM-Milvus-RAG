"""
    RAG 入口
    单论对话，相当于工作流，只处理一次查询问答
"""

from search import Searcher
from llm.llm import LLMClient
from config import *

searcher = Searcher()
llm_client = LLMClient(
    url=LLM_ENDPOINT,
    model_name_or_path=LLM_MODEL_NAME
)


search_type_dict = {
    "full_text": searcher.full_text_search,
    "semantic": searcher.semantic_search,
    "hybrid": searcher.hybrid_search
}


def run(query, search_type="hybrid"):
    # 知识检索
    search_results = search_type_dict[search_type](query)
    # Format retrieved documents into context
    context = "\n\n".join([doc_info["entity"]["content"] for doc_info in search_results])

    # 为语言模型定义系统和用户提示。该提示与从 Milvus 检索到的文档组装在一起。
    system_prompt = QUERY_SYSTEM_PROMPT.format(context=context)
    user_prompt = f"我的提问是：{query}"

    stream_response = llm_client.chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return stream_response


if __name__ == '__main__':
    question = "docker-compose怎么安装？"

    # 将问题和检索到的内容传给大模型，得到回答
    response = run(question)

    # 流式输出回复
    print("开始作答。。。\n")
    for chunk in response:
        # 每个 chunk 是一个 ChatCompletionChunk 对象
        if chunk.choices[0].delta.content is not None:
            # 打印当前得到的文本片段
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n\nFinished!")
