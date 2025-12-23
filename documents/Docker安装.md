# Docker及其相关组件安装

[toc]

- 基于`Ubuntu20.04`，对于其他  `Linux `系统同理

## 1 更换apt源

**1.1 查看系统版本**

- 输入以下命令：

```bash
cat /etc/lsb-release
```

- 输出内容如下：

```bash
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=20.04
DISTRIB_CODENAME=focal
DISTRIB_DESCRIPTION="Ubuntu 20.04.6 LTS"
```

可以看出为 `Ubuntu20.04` 系统

**1.2 换源**

- 按以下步骤进行

```bash
cd /etc/apt
sudo mv sources.list sources.list.back  # 备份 sources.list 文件
sudo touch sources.list                 # 新建一个 sources.list 文件
sudo vi sources.list                    # 编辑 sources.list 文件
```

- 将如下阿里源内容写入  `sources.list` 文件，之后 :wq 保存退出（非Ubuntu20.04，则在网上搜索其他的源，步骤无区别）

```bash
deb https://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
```

- 更新

```bash
sudo apt update
```

**1.3 参考链接**

- https://blog.csdn.net/abilix_tony/article/details/148005158

## 2 安装Docker

**2.1 安装必要的软件包**

```bash
sudo apt install vim curl wget gnupg dpkg apt-transport-https lsb-release ca-certificates software-properties-common
```

**2.2 添加Docker官方版本库的GPG密钥**

```bash
sudo mkdir keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

**2.3 使用以下命令设置存储库**

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**2.4 安装 Docker 引擎**

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**常见问题**

- ##### 注意：如果在 2.4 步骤中，安装缓慢或出错，可以切换阿里云镜像源安装Docker，具体按照下方步骤执行

**2.4.1 卸载可能存在的或者为安装成功的Docker版本**

```bash
sudo apt remove docker docker-engine docker-ce docker.io
```

**2.4.2 添加阿里云的GPG密钥**

```bash
curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
```

**2.4.3 使用以下命令设置存储库**

```bash
sudo add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
```

**之后重新执行上面的 2.4 步骤**

**2.5 验证Docker**

```bash
sudo docker version
```

- 得到如下结果，安装成功：

```bash
Client: Docker Engine - Community
 Version:           28.1.1
 API version:       1.49
 Go version:        go1.23.8
 Git commit:        4eba377
 Built:             Fri Apr 18 09:52:18 2025
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          28.1.1
  API version:      1.49 (minimum version 1.24)
  Go version:       go1.23.8
  Git commit:       01f442b
  Built:            Fri Apr 18 09:52:18 2025
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.7.27
  GitCommit:        05044ec0a9a75232cad458027ca83437aae3f4da
 runc:
  Version:          1.2.5
  GitCommit:        v1.2.5-0-g59923ef
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
```

**2.6 验证Docker是否在运行**

```bash
sudo systemctl status docker
```

- 出现以下输出，则docker处于运行状态

```bash
● docker.service - Docker Application Container Engine
     Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2025-05-21 10:44:40 CST; 11min ago
TriggeredBy: ● docker.socket
       Docs: https://docs.docker.com
   Main PID: 7691 (dockerd)
      Tasks: 17
     Memory: 46.4M
     CGroup: /system.slice/docker.service
             └─7691 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
```

**2.7 启动Docker**

- 如果未运行，则运行以下命令启动Docker服务

```bash
sudo systemctl start docker
```

**2.8 设置开机自启动**

```bash
sudo systemctl enable docker
```

**2.9 参考链接**

- https://blog.csdn.net/s_daqing/article/details/128982516
- https://cloud.tencent.com/developer/article/2503527?policyId=1003
- https://zhuanlan.zhihu.com/p/31251918552

## 3 测试Docker镜像

**3.1 拉取Docker镜像**

```bash
sudo docker pull ubuntu:22.04
```

- 大概率会出现超时的报错

```bash
Error response from daemon: Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

**3.2 配置 Docker 镜像加速器**

```bash
cd /etc/docker
sudo touch daemon.json  # 没有这个文件时创建一个，有的话在原来的基础上修改
sudo vim daemon.json
```

- 添加以下内容：

```bash
{
	"registry-mirrors": [
	    "https://docker.1ms.run/", 
	    "https://hub.rat.dev/", 
	    "https://docker.1panel.live/", 
	    "https://docker.m.daocloud.io/"
	]
}
```

**3.3 重启Docker**

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl status docker  # 查看docker是否已重新启动
```

之后再拉取镜像应该就没问题了

**3.4 参考链接**

- https://blog.csdn.net/qq_44402184/article/details/144826592?spm=1001.2014.3001.5502

## 4 安装 NVIDIA Container Toolkit

为了让 `Docker` 容器可以访问宿主机上的 `NVIDIA GPU`，推荐安装 `NVIDIA Container Toolkit`

**4.1 检查 NVIDIA 容器工具包是否安装**

- 执行

```bash
dpkg -l | grep nvidia-container-toolkit
```

如果没有任何信息出现，则开始安装

**4.2 安装 NVIDIA Container Toolkit**

```bash
# 添加包仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装nvidia-container-toolkit
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 重启docker
sudo systemctl restart docker
```

**4.3 Docker运行时使用 NVIDIA配置**

```bash
sudo vim /etc/docker/daemon.json
```

添加以下内容（如果已有其他配置，保留其他配置）：

```bash
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

重启docker

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**4.4 验证安装**

```bash
sudo docker run -it --gpus device=0 nvcr.io/nvidia/tensorrt:22.04-py3 bash
```

正常的话会进入到创建的容器内，运行 `nvidia-smi` 可以看到显卡信息

**4.5 参考链接**

- https://blog.csdn.net/ZhouDevin/article/details/145335593
- https://blog.csdn.net/weixin_47880303/article/details/146017297

## 5 docker-compose

- **安装 docker-compose**

**5.1 下载并安装 docker-compose**

```bash
# 下载最新稳定版（替换版本号为你需要的版本）
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

**5.2 赋予可执行权限**

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

**5.3 验证安装**

```bash
docker-compose --version
```

输出应类似：`Docker Compose version v2.24.5`

- **docker-compose 管理服务**

**5.4 启动服务**

```bash
docker-compose up -d
```

**5.5 清除之前的所有状态并重新构建所有容器**

在使用 Docker Compose 时，如果需要清除之前的所有状态并重新构建所有容器，可以通过以下步骤实现。这包括删除旧的容器、网络、卷以及重新构建镜像。

**5.5.1 停止并删除当前的容器、网络和卷**

首先，确保所有服务都已停止并删除相关的容器、网络和卷。可以使用以下命令：

```bash
docker-compose down --volumes --rmi all
```

- `docker-compose down`：停止并删除由 `docker-compose` 管理的容器、网络和卷。
- `--volumes`：删除与服务关联的卷。
- `--rmi all`：删除所有由 `docker-compose` 创建的镜像。

**5.5.2 清理旧的构建缓存**

为了确保重新构建时没有旧的缓存影响，可以清理 Docker 的构建缓存：

```bash
docker builder prune -f
```

**5.5.3 重新构建并启动服务**

接下来，重新构建并启动服务。可以使用以下命令：

```bash
docker-compose up --build -d
```

- `--build`：强制重新构建服务的镜像。
- `-d`：在后台运行服务。

**完整命令**

将上述步骤合并为一个完整的命令序列，可以这样操作：

```bash
sudo docker-compose down --volumes --rmi all
sudo docker builder prune -f
sudo docker-compose up --build -d
```

**注意事项**

1. **数据丢失**：使用 `--volumes` 参数会删除所有与服务关联的卷，这意味着存储在这些卷中的数据将丢失。如果需要保留某些数据，请提前备份。
2. **镜像删除**：使用 `--rmi all` 会删除所有由 `docker-compose` 创建的镜像。如果这些镜像在其他地方还需要使用，请谨慎操作。
3. **构建缓存清理**：清理构建缓存可能会使构建过程变慢，因为 Docker 需要重新构建所有镜像，而不是利用缓存。

通过以上步骤，你可以清除之前的所有状态并重新构建所有容器，确保服务以全新的状态运行。

## 6 卸载Docker

- 参考链接：https://blog.csdn.net/qq_29709589/article/details/146551391