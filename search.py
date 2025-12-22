"""
    执行检索
"""

from typing import List, Dict
from pymilvus import MilvusClient

from llm.text_embedding import EmbeddingClient
from llm.reranker import RerankerClient
from config import *


class Searcher:
    def __init__(
            self,
            milvus_uri=MILVUS_URI,
            milvus_collection_name=COLLECTION_NAME,
            limit=DEFAULT_LIMIT,
            score_threshold=DEFAULT_SCORE_THRESHOLD
    ):
        self.client = MilvusClient(uri=milvus_uri)  # Milvus 客户端
        self.collection_name = milvus_collection_name  # 本项目使用的 Milvus collection 名称

        self.embedding_client = EmbeddingClient(
            url=EMBEDDING_ENDPOINT,
            model_name_or_path=EMBEDDING_MODEL_NAME
        )
        self.reranker_client = RerankerClient(
            base_url=RERANKER_ENDPOINT,
            model_name=RERANKER_MODEL_NAME
        )

        self.limit = limit
        self.score_threshold = score_threshold

    def full_text_search(self, query: str, limit: int = 0) -> List:
        """
            全文搜索（词汇检索）
        稀疏搜索利用 BM25 算法查找包含特定关键词或短语的文档。这种传统的搜索方法擅长于精确的术语匹配，在用户确切知道自己在寻找什么的情况下尤为有效。
        :param query: 用于搜索的查询
        :param limit: TopK
        :return: [{"id": "", "distance": float, "entity": {"title": "", "content": ""}}, ...]
        """
        # BM25 sparse vectors
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query],
            anns_field="sparse_vector",
            limit=limit if limit > 0 else self.limit,
            output_fields=["title", "content"]
        )
        return results[0] if results else []

    def semantic_search(self, query: str, limit: int = 0) -> List:
        """
            语义搜索（向量检索）
        密集搜索使用向量 Embeddings 来查找具有相似含义的文档，即使它们没有完全相同的关键词。这种方法有助于理解上下文和语义，非常适合自然语言查询。
        :param query: 用于搜索的查询
        :param limit: TopK
        :return: [{"id": "", "distance": float, "entity": {"title": "", "content": ""}}, ...]
        """
        # Generate embedding for query
        query_embedding = self.embedding_client.emb_texts([query])[0]

        # Semantic search using dense vectors
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            anns_field="dense_vector",
            limit=limit if limit > 0 else self.limit,
            output_fields=["title", "content"]
        )
        return results[0] if results else []

    @staticmethod
    def _merge_results(sparse_results: List, dense_results: List) -> List[Dict]:
        """合并并去重结果"""
        seen_ids = set()
        merged = []

        total_results = sparse_results + dense_results
        for result in total_results:
            chunk_id = result["id"]
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                merged.append(
                    {
                        "id": chunk_id,
                        "title": result["entity"]["title"],
                        "content": result["entity"]["content"]
                    }
                )

        return merged

    def hybrid_search(self, query: str, limit: int = 0, score_threshold: float = -1) -> List:
        """
            混合搜索
        混合搜索结合了全文搜索和语义密集检索。这种平衡的方法充分利用了两种方法的优势，从而提高了搜索的准确性和稳健性
        :param query: 用于搜索的查询
        :param limit: TopK
        :param score_threshold: 搜索结果过滤阈值
        :return:  [{"id": "", "distance": 0.9, "entity": {"title": "", "content": ""}}, ...]
        """
        limit = limit if limit > 0 else self.limit
        score_threshold = score_threshold if score_threshold >= 0 else self.score_threshold

        sparse_results = self.full_text_search(query, limit=int(limit * CANDIDATE_MULTIPLIER))
        dense_results = self.semantic_search(query, limit=int(limit * CANDIDATE_MULTIPLIER))

        merged_results = self._merge_results(sparse_results, dense_results)
        # [{"id": "", "title": "", "content": ""}, ...]
        if not merged_results:
            return []

        # 提取文档内容
        documents = [result["content"] for result in merged_results]

        # rerank
        ret = self.reranker_client.rerank_request(query, documents)
        rerank_result = ret["results"] if ret["code"] == 200 else []
        # [{"index": int, "document": {"text": ""}, "relevance_score": float}, ...]
        if not rerank_result:
            return []

        # 过滤结果
        results = rerank_result[:limit]  # Top K
        results = [result for result in results if result["relevance_score"] > score_threshold]  # score threshold
        # print(results)
        # [{'index': 1, 'document': {'text': '123'}, 'relevance_score': 0.9970703125},
        #  {'index': 4, 'document': {'text': '456'}, 'relevance_score': 0.978515625}]

        # format, 把输出格式保持与全文检索、语义检索一致
        final_results = []
        for result in results:
            origin_res_idx = result["index"]
            final_results.append(
                {
                    "id": merged_results[origin_res_idx]["id"],
                    "distance": result["relevance_score"],
                    "entity": {
                        "title": merged_results[origin_res_idx]["title"],
                        "content": result["document"]["text"]
                    }
                }
            )

        for result in final_results:
            print("已阅读来自文档《{}》的文本段。".format(result["entity"]["title"]))
        print()

        return final_results


if __name__ == '__main__':
    searcher = Searcher()

    # Example query for search
    question = "docker-compose怎么安装？"

    # res = searcher.full_text_search(question)
    # res = searcher.semantic_search(question)
    res = searcher.hybrid_search(question)
    print(res)
