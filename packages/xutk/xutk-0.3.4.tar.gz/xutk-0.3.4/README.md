# Xulab Useful Toolkit in Python (xutk)

![Maintenance](https://img.shields.io/maintenance/Zelin2001/2025)
![PyPI - Python Version](https://img.shields.io/badge/python-3.11|3.12|3.13|3.14|3.14t-blue.svg)

## 导入项目

```bash
pip install \
  --trusted-host "gitea.xulab.ion.ac.cn" \
  --extra-index-url "http://gitea.xulab.ion.ac.cn/api/packages/zelin2001/pypi/simple/" \
  xutk
```

或者使用 uv:

```bash
uv add --index http://gitea.xulab.ion.ac.cn/api/packages/zelin2001/pypi/simple xutk
```

## 快速开始

```python
from xutk import verchk, log, mp_runner
from pathlib import Path

# 版本检查
verchk.check_version("0.2.0", "some_package")

# 日志记录
logger = log.CtxLogger("my_app")
logger.info({"module": "processor", "file": "data.csv"}, "Processing started")

# 多进程运行器
runner = mp_runner.mprunner_factory(2, log_file=Path("process.log")) # 进程队列，取 2 个运行
runner.batch_run(["echo", "-E", f"test{num}"] for num in range(1,25)) # 排队 25 个进程
```

**建议在项目 `__init__.py` 创建 CtxLogger("my_app")，避免实例化顺序问题。**

## 项目结构

```text
xutk/
├── xutk/
│   ├── __init__.py      # 包初始化
│   ├── log.py           # 日志记录功能
│   ├── mp_runner.py     # 多进程运行管理
│   ├── perf.py          # 快速资源检查
│   └── verchk.py        # 版本检查功能
├── test/
│   ├── integration/     # 集成测试
│   └── unit/            # 单元测试
├── gitea/
│   └── workflows/       # CI 工作流
├── pyproject.toml       # 项目配置
└── README.md            # 项目文档
```

## 开发

### 安装开发依赖

```bash
uv sync --all-extras
```

### 运行测试

```bash
uv run pytest
```

### 代码检查

```bash
uv run ruff check      # 代码风格检查
uv run ty check        # 类型检查
uv run pytest          # 样例测试
```
