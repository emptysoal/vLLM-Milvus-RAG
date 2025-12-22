"""
    在 Milvus 中创建 Collection
"""

from pymilvus import MilvusClient, DataType, Function, FunctionType
from config import *

client = MilvusClient(uri=MILVUS_URI)
collection_name = COLLECTION_NAME

"""为全文搜索设置 Collections"""
# 中文文本分析器配置
analyzer_params = {
    "type": "chinese",
    "stop_words": ["的", "了"]
}

# 测试 analyzer_params
# text = "Milvus 的内置分析器预先配置了特定的标记化器和过滤器，使您可以立即使用，而无需自己定义这些组件。"
# result = client.run_analyzer(text,analyzer_params)
# print(result)

# Collections Schema 和 BM25 功能
schema = MilvusClient.create_schema()
schema.add_field(
    field_name="id",
    datatype=DataType.VARCHAR,
    is_primary=True,
    auto_id=True,
    max_length=100
)
schema.add_field(
    field_name="title",
    datatype=DataType.VARCHAR,
    max_length=200
)
schema.add_field(
    field_name="content",
    datatype=DataType.VARCHAR,
    max_length=65535,
    analyzer=analyzer_params,
    enable_match=True,  # Enable text matching
    enable_analyzer=True  # Enable text analysis
)
schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
schema.add_field(
    field_name="dense_vector",
    datatype=DataType.FLOAT_VECTOR,
    dim=1024
)
schema.add_field(field_name="metadata", datatype=DataType.JSON)

# Define BM25 function to generate sparse vectors from text
bm25_function = Function(
    name="bm25",
    function_type=FunctionType.BM25,
    input_field_names=["content"],
    output_field_names="sparse_vector"
)

# Add the function to schema
schema.add_function(bm25_function)

# 索引和 Collections 创建
index_params = MilvusClient.prepare_index_params()
index_params.add_index(
    field_name="sparse_vector",
    index_type="SPARSE_INVERTED_INDEX",
    metric_type="BM25"
)
index_params.add_index(
    field_name="dense_vector",
    index_type="AUTOINDEX",
    metric_type="COSINE"
)

# 检查 Collections 是否已存在，如果已存在，则删除它
if client.has_collection(collection_name):
    client.drop_collection(collection_name)
client.create_collection(
    collection_name=collection_name,
    schema=schema,
    index_params=index_params
)
print(f"Collection '{collection_name}' created successfully")
