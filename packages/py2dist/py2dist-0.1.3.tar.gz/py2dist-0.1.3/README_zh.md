# py2dist

[English Documentation](README.md)

py2dist 是一个使用 Cython 将 Python 源代码编译为二进制扩展模块（.so/.pyd）的工具，用于简单地保护源代码不被更改，适用于发布 Python 项目、Docker 服务镜像的构建等场景。

## 功能

- 将单个 `.py` 文件或整个目录编译为二进制文件
- 保持目录结构，自动复制其他文件到输出目录
- 支持排除指定文件或目录
- 自动检测并使用 ccache 加速编译
- 获得 Cython 编译带来的一点性能提升
- 提供 CLI 和 Python API

## 安装

```bash
pip install py2dist
```

## 重要提示：Python 版本一致性

编译生成的二进制扩展模块（.so/.pyd）与特定的 Python 版本绑定。**您必须确保编译时使用的 Python 版本与运行时使用的 Python 版本完全一致**（包括次要版本号，例如 3.10 和 3.11 是不兼容的）。

如果版本不匹配，导入模块时可能会遇到如下错误：
`ImportError: ... undefined symbol: _PyThreadState_UncheckedGet`
或者
`ModuleNotFoundError: No module named ...`

## 使用方法

### 命令行界面 (CLI)

默认输出目录为 `dist` / `{-d 参数指定的目录名}`，也可以通过 `-o` 参数指定输出目录。

编译单个文件：
```bash
py2dist -f myscript.py
```

输出文件位置为 `dist/myscript.so`

编译整个目录：
```bash
py2dist -d myproject
```

输出文件位置为 `dist/myproject`，并且会自动复制非 `.py` 文件到输出目录。

## 示例用法

比如我有一个 Python FastAPI 项目，我想将其打包为一个 Docker 镜像的同时保护源代码不被修改，我可以使用 py2dist 将项目核心代码目录编译为二进制扩展模块，然后将其复制到 Docker 镜像中，直接发布也是可以的，原理类似。

> 我平时在实际项目中更习惯通过 `uv`、`pyproject.toml`、`.python-version` 等文件控制项目依赖和 Python 版本，Docker 镜像的构建也可以安装 `ccache`、`uv` 来等工具来优化工作流程，本演示为简化流程，不在此展开，可以自行研究改进。


### 示例项目环境

- `ccache` 推荐安装，用于加速后续改动项目时的编译速度，`py2dist` 会自动识别使用。
- `python3.12` 项目编译时使用的 Python 版本，因此Docker 镜像中也必须使用该 Python 版本，否则会报错


### 项目示例结构：

```
myproject/
├── Makefile (项目构建文件)
├── run.py (服务器启动文件，不能被编译)
├── requirements.txt
├── Dockerfile
├── server/ (项目代码目录，被编译的目标)
│   ├── __init__.py (每个模块必须存在的文件，内容可以为空)
│   ├── main.py（FastAPI 主入口文件）
│   ├── utils.py
│   ├── router/（模块路由目录）
│   │   ├── __init__.py (每个模块必须存在的文件，内容可以为空)
│   │   └── user.py
│   ├── static/（其他文件，会原样复制）
│   │   └── image.png
│   └── templates/ (其他文件，会原样复制)
│       ├── index.html
│       └── about.html
├── tests/
│   └── test_main.py
├── models/
└   └── ...
```

`run.py` 样例：
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("server.main:app", host="0.0.0.0", port=3000)
```

> 1. `__init__.py` 文件必须存在，内容可以为空。以便被编译后能被识别为一个模块。
> 
> 2. 需要一个未编译的 `run.py` 文件来启动服务器。
> 
> 3. 按通用规范不建议在源码目录中放置资源文件，一般放在单独的目录中去引用使用，但是为了演示，这里还是放了一些资源文件演示自动复制功能。
>

那么可以这样编写 `Makefile`:

```makefile
.PHONY: install compile build

install:
    pip3 install py2dist

compile:
    python3 -m py2dist -d server

build: compile
    docker build -t myproject .
```

这样编写 `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY models /app/models

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt
    pip3 install -r requirements.txt

COPY dist/server /app/server
COPY run.py /app/run.py

EXPOSE 3000
CMD ["python3", "/app/run.py"]
```

然后通过命令
```bash
cd myproject
make build
```

即可构建出发布版的镜像。
此时我们查看镜像内文件结构，类似如下：

```
/app/
├── run.py
├── server/
│   ├── __init__.py
│   ├── main.so
│   ├── utils.so
│   ├── router/
│   │   ├── __init__.py
│   │   └── user.so
│   ├── static/
│   │   └── image.png
│   └── templates/
│       ├── index.html
│       └── about.html
├── models/
└   └── ...
```

达到简单保护源代码不被修改的目的。

如果不想使用 Docker 镜像，可以直接打包发布项目，也可以使用类似流程，原理相同。

首先修改 `run.py` 文件，在文件开头添加如下代码：
```python
import sys
import os

# ================= Import lib =================

current_dir = os.path.dirname(os.path.abspath(__file__))

lib_path = os.path.join(current_dir, "lib")

if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# ================= End of Import lib =================
```

并且修改 `server/main.py` 文件，在文件开头添加如下代码：
```python
import sys
import os

# ================= Import lib =================

current_dir = os.path.dirname(os.path.abspath(__file__))

lib_path = os.path.join(current_dir, "../lib")

if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# ================= End of Import lib =================
```
目的是让 Python 解释器能够识别到第三方库文件，接下来通过类似下面的命令打包发布：

```bash
cd myproject
make compile
mkdir -p build/lib
cp -r dist/server build/server
cp run.py build/run.py
pip install -r requirements.txt --target "./build/lib" --python-version "3.12" --only-binary=:all:
tar -czvf myproject.tar.gz build
```

即可发布项目到任意服务器，当然这种方式也需要运行时环境有同版本号的 Python 3.12 环境，也可以自行放置便携版 Python 3.12 环境，或者使用 `uv` 等工具来控制项目依赖和 Python 版本，不在此展开了。

### 高级

参数说明：
- `-f, --file`: 指定要编译的单个 .py 文件
- `-d, --directory`: 指定要编译的目录
- `-o, --output`: 输出目录 (默认为 `dist`)
- `-m, --maintain`: 排除的文件或目录 (逗号分隔)
- `-x, --nthread`: 编译线程数 (默认为 1)
- `-q, --quiet`: 安静模式
- `-r, --release`: 发布模式 (清理临时构建文件)
- `-c, --ccache`: 使用 ccache (默认自动检测，也可指定路径)

### Python API

```python
from py2dist import compile_file, compile_dir

# 编译单个文件
compile_file("myscript.py", output_dir="dist")

# 编译目录
compile_dir(
    "myproject",
    output_dir="dist",
    exclude=["tests", "setup.py"],
    nthread=4
)
```
