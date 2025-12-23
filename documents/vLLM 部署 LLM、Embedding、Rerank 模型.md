# vLLM 部署 LLM、Embedding、Rerank 模型

## 一. 简介

- 使用 `vLLM` 部署 3 种类型的语言模型，包括：`LLM`、`Embedding`、`Reranker`；
- 部署好之后，可以直接添加至 `dify` 平台

## 二. 服务启动及测试

### 2.1 LLM

- 启动服务

```bash
vllm serve /workspace/models/Qwen2.5-3B-Instruct --dtype=float16 --tensor-parallel-size 2 --enable-auto-tool-choice --tool-call-parser hermes --trust-remote-code
```

- 测试服务

```python
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://<ip>:32804/v1"
model_name_or_path = "/workspace/models/Qwen2.5-3B-Instruct"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model=model_name_or_path,
    messages=[
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": "Tell me something about large language models."},
    ],
    temperature=0.7,
    top_p=0.8,
    max_tokens=512,
    extra_body={
        "repetition_penalty": 1.05,
    },
)
print("Chat response:", chat_response)
```

### 2.2 Embedding

- 启动服务

```bash
vllm serve /workspace/models/BAAI/bge-m3 --dtype=float16 --trust-remote-code
```

- 测试服务

```python
from openai import OpenAI
import numpy as np

# 1. 创建客户端，指向本地vLLM服务
client = OpenAI(
    api_key="",  # vLLM不需要真实的API密钥，可以随便填
    base_url="http://192.168.0.230:32805/v1"  # 关键：指向你的vLLM服务地址
)

# 2. 准备文本
texts = ["你好，世界", "Hello, world", "深度学习"]

# 3. 调用嵌入接口（与调用OpenAI Embeddings API完全一致）
response = client.embeddings.create(
    model="/workspace/models/BAAI/bge-m3",  # 与 --served-model-name 参数指定的名称一致
    input=texts
)

# 4. 处理结果
embeddings = [np.array(data.embedding) for data in response.data]
print(f"生成了 {len(embeddings)} 个向量")
print(f"每个向量的维度：{len(embeddings[0])}")  # BGE-M3输出1024维向量
```

### 2.3 Reranker

- 启动服务

```bash
vllm serve /workspace/models/BAAI/bge-reranker-v2-m3 --dtype=float16 --trust-remote-code
```

- 测试服务

该服务存在 2 种访问方式：

1. 访问 `/score` 路由

```bash
# 单次推理 (Single inference)
curl -X 'POST' \
  'http://192.168.0.230:32806/score' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "/workspace/models/BAAI/bge-reranker-v2-m3",
  "encoding_format": "float",
  "text_1": "What is the capital of France?",
  "text_2": "The capital of France is Paris."
}'

# 批量推理
curl -X 'POST' \
  'http://192.168.0.230:32806/score' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "/workspace/models/BAAI/bge-reranker-v2-m3",
  "text_1": "What is the capital of France?",
  "text_2": [
    "The capital of Brazil is Brasilia.",
    "The capital of France is Paris."
  ]
}'
```

2.  访问 `/rerank` 路由

```bash
curl -X 'POST' \
  'http://192.168.0.230:32806/rerank' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "/workspace/models/BAAI/bge-reranker-v2-m3",
  "query": "What is the capital of France?",
  "documents": [
    "The capital of Brazil is Brasilia.",
    "The capital of France is Paris.",
    "Horses and cows are both animals"
  ]
}'
```

**备注： rerank路由不同于上面 2 个，它的路由中没有 /v1**

## 三. 集成至 dify

1. 模型供应商选择 `OpenAI-API-compatible` ；
2. 分别配置 `LLM`、`Text Embedding`、`Rerank` 模型即可，注意添加 `Rerank` 时 `URL` 里不要有 `/v1`

## 四. 参考

- https://vllm.hyper.ai/docs/inference-and-serving/openai_compatible_server
- https://github.com/vllm-project/vllm/tree/v0.8.0/examples/online_serving