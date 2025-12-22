"""
    RAG 入口
    多轮对话，相当于 chatflow，可携带上下文查询
"""

from typing import List

from search import Searcher
from llm.llm import LLMClient
from config import *


class RAGChatFlow:
    def __init__(self):
        self.searcher = Searcher()  # 检索器，包含全文检索、语义检索、混合检索
        self.llm_client = LLMClient(
            url=LLM_ENDPOINT,
            model_name_or_path=LLM_MODEL_NAME
        )
        self.max_history_length = 10

    def search_context(self, query, search_type="hybrid"):
        """根据用户输入从知识库（Milvus）搜索相关内容"""
        search_type_dict = {
            "full_text": self.searcher.full_text_search,
            "semantic": self.searcher.semantic_search,
            "hybrid": self.searcher.hybrid_search
        }
        # 知识检索
        search_results = search_type_dict[search_type](query)
        # Format retrieved documents into context
        context = "\n\n".join([doc_info["entity"]["content"] for doc_info in search_results])
        return context

    def enrich_query_with_history(self, messages: List, query: str, dialogue_rounds: int = 3) -> str:
        """
            根据历史对话，补全当前提问
        :param messages: 历史对话
        :param query: 当前提问
        :param dialogue_rounds: 使用最近的几轮对话来补全
        :return: 补全后的提问
        """
        if len(messages) == 1:  # 只有系统提示，即对话刚开始
            return query

        # 提取最近的几轮对话
        history = messages[1:][::-1]  # 去掉系统提示，并倒序排列对话历史
        valid_history = history[:2 * dialogue_rounds][::-1]

        system_prompt = REWRITE_SYSTEM_PROMPT
        user_prompt = REWRITE_USER_PROMPT.format(history=str(valid_history), query=query)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.llm_client.chat(messages, stream=False)

        return response

    @staticmethod
    def drop_history(messages: List, keep_num: int = 10):
        """删除较久的对话，只保留最近的对话"""
        # 提取最近的几轮对话
        system_message = messages[0]
        history = messages[1:][::-1]  # 去掉系统提示，并倒序排列对话历史
        valid_history = history[:2 * keep_num][::-1]

        messages.clear()
        messages.append(system_message)
        messages.extend(valid_history)

    def run(self):
        # 存储历史对话
        messages = [{"role": "system", "content": ""}]  # 先把系统提示置为空，后面随着每轮对话根据知识检索做自动变更

        while True:
            # 用户输入
            query = input(">>> ")
            if query.lower() in ["quit", "bye", "break", "exit"]:
                break
            if not query:
                continue

            # 补全提问，并使用补全后的提问去检索知识库
            rich_query = self.enrich_query_with_history(messages, query)
            print("=======", rich_query)
            context = self.search_context(rich_query)

            # 组织系统和用户提示。该提示与从 Milvus 检索到的文档组装在一起。
            messages[0]["content"] = QUERY_SYSTEM_PROMPT.format(context=context)
            messages.append({"role": "user", "content": query})

            # 调用大模型生成回复
            stream_response = self.llm_client.chat(messages)

            # 流式输出回复
            print("开始作答。。。\n")
            assistant_completion = ""
            for chunk in stream_response:
                # 每个 chunk 是一个 ChatCompletionChunk 对象
                if chunk.choices[0].delta.content is not None:
                    # 打印当前得到的文本片段
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    assistant_completion += chunk.choices[0].delta.content  # 收集大模型回复
            print()
            assistant_completion += "\n"

            messages.append({"role": "assistant", "content": assistant_completion})
            self.drop_history(messages, keep_num=self.max_history_length)


if __name__ == '__main__':
    rag_chat_flow = RAGChatFlow()

    rag_chat_flow.run()
