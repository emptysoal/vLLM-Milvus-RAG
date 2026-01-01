# vLLM + Milvus 实现 RAG

![](https://milvus.io/docs/v2.6.x/assets/advanced_rag/hybrid_and_rerank.png)

图片来自 `Milvus` 官方网站

## 简介

**基本信息**

- 使用 `vLLM` 部署大模型，并结合 `Milvus` 实现 `RAG` ；
- 在 `documents` 目录中放入了我自己写的一些文档，既是本项目环境安装相关的，也作为本项目的检索数据使用；
- 支持全文检索、语义检索、混合检索；

**项目特点**

- 自己实现了混合检索，调用 `vLLM` 部署的 `bge-reranker-v2-m3` 模型；
- 自己实现了 chatflow 中的查询补全，实现携带上下文进行检索

## 环境

### 服务器

下面这些是我在服务器上安装的

- 安装 `docker`、`docker-compose`、`vllm`，参考 `documents` 目录下对应文档即可；
- 安装 `Milvus`，我使用的是 `docker-compose` 的方式，如下，源自官方文档：

```bash
wget https://github.com/milvus-io/milvus/releases/download/v2.6.7/milvus-standalone-docker-compose.yml -O docker-compose.yml

sudo docker compose up -d
```

镜像拉取成功，且成功启动服务后，在浏览器输入 `http://127.0.0.1:9091/webui` 查看相关信息

- 使用 `vLLM` 部署 `LLM` 、`Embedding`、`Rerank` 这 3 类大模型，参考 `documents` 目录下对应文档即可；

### 本地

项目中的代码的运行环境，也可以在服务器中创建 `conda` 虚拟环境，或使用 `docker` 容器运行

```bash
pip install requirements.txt
```

使用到的 `python` 库极少，主要就是 `pymilvus` 和 `openai`

## 文件介绍

```bash
项目目录
   |--- documents                   # 项目环境相关文档，同时后续存储至 Milvus 做测试数据
   |--- llm
   |      |--- llm.py               # 访问对话大模型的客户端
   |      |--- text_embedding.py    # 访问文本嵌入大模型的客户端
   |      |--- reranker.py          # 访问 rerank 大模型的客户端
   |--- config.py
   |--- create_collection.py        # 在 Milvus 中创建 Collection
   |--- doc_op.py                   # 文档拆分
   |--- insert_data.py              # 把拆分文档的稠密和稀疏向量存到 Milvus
   |--- search.py                   # 使用 Milvus 的检索功能
   |--- rag_workflow.py             # 工作流形式，根据用户查询，搜索相关文档并作答
   |--- rag_chatflow.py             # 对话流形式，根据用户查询，搜索相关文档并作答
```

## 运行

修改 `condig.py` 文件中的相关配置，对应自己的部署环境

- 工作流

```bash
python rag_workflow.py
```

- 对话流

```bash
python rag_chatflow.py
```




