"""
    OpenAI 客户端，访问自己使用 vLLM 部署的 Embedding 模型
    部署命令：
        vllm serve /workspace/models/BAAI/bge-m3 --dtype=float16 --trust-remote-code
"""

from typing import List
from openai import OpenAI


class EmbeddingClient:
    def __init__(
            self,
            url="http://192.168.0.230:32805/v1",
            model_name_or_path="/workspace/models/BAAI/bge-m3"
    ):
        self.model_name_or_path = model_name_or_path
        self.openai_client = OpenAI(
            api_key="",  # vLLM不需要真实的API密钥，可以随便填
            base_url=url  # 关键：指向你的vLLM服务地址
        )

    # 定义一个函数，使用 OpenAI 客户端生成文本嵌入。以 BAAI/bge-m3 模型为例。
    def emb_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        response = self.openai_client.embeddings.create(
            model=self.model_name_or_path,
            input=texts
        )
        return [embedding.embedding for embedding in response.data]


if __name__ == '__main__':
    embedding_client = EmbeddingClient()

    test_texts = ["This is a test", "Today is sunny"]

    text_embeddings = embedding_client.emb_texts(test_texts)
    embedding_dim = len(text_embeddings[0])
    print(embedding_dim)
    print(text_embeddings[0][:10])

    """
    1024
    [-0.0192718505859375, 0.0218353271484375, -0.045654296875, -0.01055908203125, -0.01763916015625, -0.01910400390625, 
     0.0400390625, 0.03863525390625, 0.017303466796875, 0.00446319580078125]
    """
