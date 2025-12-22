"""
    OpenAI 客户端，访问自己使用 vLLM 部署的 LLM 语言大模型
    部署命令：
        vllm serve /workspace/models/Qwen2.5-3B-Instruct --dtype=float16 --tensor-parallel-size 2
            --enable-auto-tool-choice --tool-call-parser hermes --trust-remote-code
"""

from openai import OpenAI


class LLMClient:
    def __init__(
            self,
            url="http://192.168.0.230:32804/v1",
            model_name_or_path="/workspace/models/Qwen2.5-3B-Instruct"
    ):
        self.model_name_or_path = model_name_or_path
        self.openai_client = OpenAI(
            api_key="",  # vLLM不需要真实的API密钥，可以随便填
            base_url=url  # 关键：指向你的vLLM服务地址
        )

    # 定义一个函数，使用 OpenAI 客户端生成文本。
    def chat(self, messages, stream=True):
        chat_response = self.openai_client.chat.completions.create(
            model=self.model_name_or_path,
            messages=messages,
            temperature=0.7,
            top_p=0.8,
            max_tokens=512,
            stream=stream,
            extra_body={
                "repetition_penalty": 1.05,
            },
        )
        return chat_response if stream else chat_response.choices[0].message.content


if __name__ == '__main__':
    llm_client = LLMClient()

    # test_messages = [
    #     {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    #     {"role": "user", "content": "Tell me something about large language models."},
    # ]
    #
    # stream_response = llm_client.chat(test_messages)
    # for chunk in stream_response:
    #     # 每个 chunk 是一个 ChatCompletionChunk 对象
    #     if chunk.choices[0].delta.content is not None:
    #         # 打印当前得到的文本片段
    #         print(chunk.choices[0].delta.content, end="", flush=True)

    test_messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": "李白是诗人吗？"},
    ]

    response = llm_client.chat(test_messages, stream=False)
    print(response)
