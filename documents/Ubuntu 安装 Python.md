# Ubuntu 安装 Python

在 Ubuntu 20.04 上通过 tgz 包安装 Python 3.12.8，以下是详细步骤：

## 1. 安装编译依赖

```bash
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev \
libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev wget
```

## 2. 下载 Python 3.12.8 源码包

```bash
# 创建安装目录
mkdir -p ~/python-install
cd ~/python-install

# 下载 Python 3.12.8
wget https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tgz

# 解压
tar -xzf Python-3.12.8.tgz
cd Python-3.12.8
```

## 3. 配置编译选项

```bash
# 配置编译选项
./configure --enable-optimizations --prefix=/usr/local/python3.12.8

# 或者如果您想安装到系统目录（需要sudo权限）
# ./configure --enable-optimizations
```

`--enable-optimizations` 选项会进行优化编译，但会延长编译时间。

## 4. 编译和安装

```bash
# 确定CPU核心数（用于并行编译加速）
nproc

# 编译（将8替换为您的CPU核心数）
make -j 8

# 安装
sudo make altinstall  # 使用altinstall避免覆盖系统默认Python
```

## 5. 创建符号链接（可选）

```bash
# 创建python3.12和pip3.12的符号链接
sudo ln -sf /usr/local/python3.12.8/bin/python3.12 /usr/local/bin/python3.12
sudo ln -sf /usr/local/python3.12.8/bin/pip3.12 /usr/local/bin/pip3.12

# 如果您想将其设置为默认python3（谨慎操作）
# sudo ln -sf /usr/local/python3.12.8/bin/python3.12 /usr/local/bin/python3
```

## 6. 验证安装

```bash
# 检查Python版本
python3.12 --version

# 检查pip版本
pip3.12 --version

# 测试Python运行
python3.12 -c "print('Python 3.12.8 installed successfully!')"
```

## 7. 配置环境变量（可选）

如果您希望优先使用新安装的Python，可以编辑 `~/.bashrc`：

```bash
echo 'export PATH="/usr/local/python3.12.8/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 8. 安装常用工具

```bash
# 升级pip
pip3.12 install --upgrade pip

# 安装常用包
pip3.12 install setuptools wheel virtualenv
```

## 注意事项

1. **使用 altinstall**：`make altinstall` 防止覆盖系统默认的Python版本
2. **编译时间**：启用优化选项后编译时间较长（约10-30分钟）
3. **依赖问题**：如果遇到缺少依赖的错误，请安装相应的开发包
4. **磁盘空间**：确保有足够的磁盘空间（约1-2GB）
5. **系统Python**：Ubuntu 20.04 的系统工具依赖于Python 3.8，不要删除或替换它

## 替代方案

如果您只是想使用Python 3.12.8而不需要从源码编译，可以考虑：

```bash
# 使用DeadSnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

这种方法更简单且易于管理。