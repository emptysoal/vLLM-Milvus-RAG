"""
    requests 客户端，访问自己使用 vLLM 部署的 Reranker 模型
    部署命令：
        vllm serve /workspace/models/BAAI/bge-reranker-v2-m3 --dtype=float16 --trust-remote-code
"""

import requests


class RerankerClient:
    def __init__(
            self,
            base_url="http://192.168.0.230:32806",
            model_name="/workspace/models/BAAI/bge-reranker-v2-m3"
    ):
        self.score_url = base_url + "/score"
        self.rerank_url = base_url + "/rerank"
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        self.model_name = model_name

    def score_request(self, text_1, text_2):
        data = {
            "model": self.model_name,
            "encoding_format": "float",
            "text_1": text_1,
            "text_2": text_2
        }
        response = requests.post(self.score_url, headers=self.headers, json=data)

        response_code = response.status_code
        response_data = response.json()
        score = response_data["data"]

        return {"code": response_code, "score": score}

    def rerank_request(self, query, documents):
        data = {
            "model": self.model_name,
            "query": query,
            "documents": documents
        }
        response = requests.post(self.rerank_url, headers=self.headers, json=data)

        response_code = response.status_code
        response_data = response.json()
        rerank_result = response_data["results"]

        return {"code": response_code, "results": rerank_result}


if __name__ == '__main__':
    reranker_client = RerankerClient()

    test_text_1 = "What is the capital of France?"
    test_text_2 = [
        "The capital of Brazil is Brasilia.",
        "The capital of France is Paris."
    ]
    score_ret = reranker_client.score_request(test_text_1, test_text_2)
    print(score_ret)

    test_query = "What is the capital of France?"
    test_documents = [
        "The capital of Brazil is Brasilia.",
        "The capital of France is Paris.",
        "Horses and cows are both animals"
    ]
    rerank_ret = reranker_client.rerank_request(test_query, test_documents)
    print(rerank_ret)
