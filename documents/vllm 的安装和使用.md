# vllm 的安装和使用

[TOC]

## 一. 安装 vllm

- 这里使用 `docker` 构建环境，以 `python:3.12.8` 为基础镜像

### 1. 创建基础容器

- 使用基础镜像创建容器：

```bash
docker run -it python:3.12.8 bash
```

### 2. 安装

```bash
pip install -i https://mirrors.aliyun.com/pypi/simple vllm==0.8.0
```

### 3. 保存镜像

- 把安装好环境的容器，保存为 `docker` 镜像

```bash
docker commit <container id> vllm-dhd:0.8.0
```

## 二. 启动服务

### 1. 准备模型文件

- 从  `https://huggingface.co` 上下载模型文件，比如： `Qwen2.5-7B-Instruct` ，宿主机存放目录为： `/home/dhd/models/Qwen2.5-7B-Instruct`

### 2. 启用环境

- 使用上面保存好的镜像创建 `docker` 容器：

```bash
docker run -it --gpus all --shm-size=32G -v /home/dhd:/workspace -p 32804:8000 vllm-dhd:0.8.0 bash
```

其中 `-v` 把宿主机 `/home/dhd` 目录挂载到容器的 `/workspace` 目录；

其中 `8000` 为 `vllm` 服务的端口，把它映射为：`32804` ；

### 3. 开启服务

- 运行：

```bash
vllm serve /workspace/models/Qwen2.5-7B-Instruct --dtype=half --tensor-parallel-size 4 --enable-auto-tool-choice --tool-call-parser hermes --trust-remote-code
```

## 三. 访问服务

### 1. 安装客户端

- 在其他环境中运行：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple openai==2.8.1
```

### 2. 访问 vllm 服务

- 编辑如下代码：

```python
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://<ip>:32804/v1"
model_name_or_path = "/workspace/models/Qwen2.5-7B-Instruct"

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

运行前把上面的 `<ip>` 换成 `vllm` 服务所在宿主机的 `ip`

## 四. 参考链接

- https://qwen.readthedocs.io/en/v2.5/deployment/vllm.html