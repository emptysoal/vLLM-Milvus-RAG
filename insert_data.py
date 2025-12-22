"""
    插入数据
"""

from tqdm import tqdm
from pymilvus import MilvusClient

from llm.text_embedding import EmbeddingClient
from doc_op import split_docs
from config import *

client = MilvusClient(uri=MILVUS_URI)
collection_name = COLLECTION_NAME

embedding_client = EmbeddingClient(
    url=EMBEDDING_ENDPOINT,
    model_name_or_path=EMBEDDING_MODEL_NAME
)

# embedding document chunks
file_dir = "./documents"
doc_name_chunk_list = split_docs(file_dir)  # [{"doc_name": "", "doc_chunk": ""}, {}, ...]
texts = [doc_name_chunk["doc_chunk"] for doc_name_chunk in doc_name_chunk_list]
embeddings = embedding_client.emb_texts(texts)

# Prepare entities for insertion
entities = []
for i, doc_chunk_info in enumerate(tqdm(doc_name_chunk_list, desc="Creating embeddings")):
    entity = {
        "title": doc_chunk_info["doc_name"],
        "content": doc_chunk_info["doc_chunk"],
        "dense_vector": embeddings[i],
        "metadata": doc_chunk_info.get("metadata", {})
    }
    entities.append(entity)

# Insert data
client.insert(collection_name=collection_name, data=entities)
print(f"Inserted {len(entities)} documents")
