# ollama 的安装和使用

[TOC]

## 一. 安装 ollama

- 这里使用 `docker` 构建环境，以 `python:3.12.8` 为基础镜像

### 1. 下载安装文件

- 从 https://ollama.com/download/ollama-linux-amd64.tgz 下载 `ollama` 二进制包，得到 `ollama-linux-amd64.tgz` 文件；
- 把上述文件放到宿主机目录下，如：`/home/dhd/ollama`

### 2. 创建基础容器

- 使用基础镜像创建容器：

```bash
# 启动时把宿主机的 /home/dhd 目录挂载到容器的 /workspace 目录
docker run -it -v /home/dhd:/workspace python:3.12.8 bash
```

### 3. 安装

```bash
cd /workspace/ollama
cp ollama-linux-amd64.tgz /home
cd /home

# 解压并安装
tar -C /usr -xzf /home/ollama-linux-amd64.tgz
```

这会将 Ollama 二进制文件解压到 `/usr/bin/` 目录，可通过 `which ollama` 查看。

### 4. 保存镜像

- 把安装好环境的容器，保存为 `docker` 镜像

```bash
docker commit <container id> ollama-dhd:1.0
```

## 二. 启动服务

### 1. 启用环境

- 使用上面保存好的镜像运行：

```bash
docker run -it --gpus all --shm-size=32G --name dhd-ollama -p 32803:11434 -v /home/dhd:/workspace ollama-dhd:1.0 bash
```

其中 `11434` 为 `ollama` 服务的端口，把它映射为：`32803` 

### 2. 准备模型文件

- 安装 modelscope

```bash
pip install -i https://mirrors.aliyun.com/pypi/simple modelscope
```

- 创建并编辑模型下载代码

```bash
cd /workspace/ollama
mkdir models  # 创建存放模型的目录
vim download_model.py  # 创建并编辑模型下载代码
```

写入如下内容：

```python
from modelscope import snapshot_download

snapshot_download('Qwen/Qwen2.5-7B-Instruct-GGUF',
                  cache_dir='./models',
                  revision='master',
                  allow_patterns=['qwen2.5-7b-instruct-fp16.gguf'])
```

`:wq` 保存后，运行 `python download_model.py` 便开始下载，模型较大下载需要一段时间。

下载到 `models` 下的文件名比较奇怪，可以自行整理成如下形式：

```bash
/workspace/ollama/models
    |
    |---- Qwen2.5-7B-Instruct-GGUF
              |
              |---- qwen2.5-7b-instruct-fp16.gguf  # 模型参数文件
```

### 3. ollama运行模型

#### 3.1 启动服务

- 启动 `ollama` 服务：

```bash
# 默认绑定在 127.0.0.1（localhost） 的 11434 端口上，设置此环境变量，让外部也可以访问到
export OLLAMA_HOST=0.0.0.0:11434

ollama serve
```

之后可以新开个窗口执行下面所有命令，可以先执行 `ollama -v` 验证一下服务

#### 3.2 创建 Ollama 模型

- 创建 Modelfile

Modelfile 是一个文本文件，用于告诉 Ollama 如何使用你的模型文件。

```bash
cd /workspace/ollam/models/Qwen2.5-7B-Instruct-GGUF  # 进入模型文件存放目录
vim Modelfile
```

写入以下内容：

```Modelfile
FROM /workspace/ollama/models/Qwen2.5-7B-Instruct-GGUF/qwen2.5-7b-instruct-fp16.gguf

# set the temperature to 1 [higher is more creative, lower is more coherent]
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER repeat_penalty 1.05
PARAMETER top_k 20

TEMPLATE """{{ if .Messages }}
{{- if or .System .Tools }}<|im_start|>system
{{ .System }}
{{- if .Tools }}

# Tools

You are provided with function signatures within <tools></tools> XML tags:
<tools>{{- range .Tools }}
{"type": "function", "function": {{ .Function }}}{{- end }}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
{{- end }}<|im_end|>
{{ end }}
{{- range $i, $_ := .Messages }}
{{- $last := eq (len (slice $.Messages $i)) 1 -}}
{{- if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role "assistant" }}<|im_start|>assistant
{{ if .Content }}{{ .Content }}
{{- else if .ToolCalls }}<tool_call>
{{ range .ToolCalls }}{"name": "{{ .Function.Name }}", "arguments": {{ .Function.Arguments }}}
{{ end }}</tool_call>
{{- end }}{{ if not $last }}<|im_end|>
{{ end }}
{{- else if eq .Role "tool" }}<|im_start|>user
<tool_response>
{{ .Content }}
</tool_response><|im_end|>
{{ end }}
{{- if and (ne .Role "assistant") $last }}<|im_start|>assistant
{{ end }}
{{- end }}
{{- else }}
{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ end }}{{ .Response }}{{ if .Response }}<|im_end|>{{ end }}"""

# set the system message
SYSTEM """You are Qwen, created by Alibaba Cloud. You are a helpful assistant."""
```

- 创建模型

```bash
ollama create qwen2.5-7b-local -f ./Modelfile
```

这里的 `qwen2.5-7b-local` 是你为这个模型实例取的名字，可以自定义。

- 验证模型创建成功

```bash
ollama list
```

## 三. 访问模型服务

- 使用 ollama python 客户端调用：

在其他环境中，安装 ollama python 客户端：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ollama
```

编辑 python 客户端代码：

```python
import ollama

# 创建客户端并指定远程 Ollama 服务的地址
client = ollama.Client(host='http://<ip>:32803')

# 使用 chat 方法与模型对话
response = client.chat(
    model='qwen2.5-7b-local',
    messages=[
        {
            'role': 'user',
            'content': 'why sky is blue?',
        }
    ]
)

# 打印模型的回复
print(response['message']['content'])
```

注意：

如果在同一容器内运行上面的测试，端口为 `11434`，如果容器外，端口为 `32803`，因为端口做了映射；

上面的 `<ip>` 改为 ollama 服务所在宿主机的 IP

## 四. 参考链接

- https://qwen.readthedocs.io/en/v2.5/run_locally/ollama.html