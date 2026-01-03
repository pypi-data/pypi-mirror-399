# PyFinder - Python环境搜索与运行工具包

[![PyPI version](https://badge.fury.io/py/pyfinder.svg)](https://badge.fury.io/py/pyfinder)
[![Python versions](https://img.shields.io/pypi/pyversions/pyfinder.svg)](https://pypi.org/project/pyfinder/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PyFinder是一个强大的Python包，用于搜索系统中的Python环境（系统Python、UV、venv、Conda），并支持多种方式运行Python文件。

## 主要功能

- 🔍 **搜索Python环境**: 自动检测系统中的所有Python环境，包括系统Python、UV、venv和Conda
- 🚀 **多种运行模式**: 支持多文件模式和单文件模式运行Python代码
- 💾 **缓存机制**: 缓存Python环境信息，提高搜索效率
- 🌐 **跨平台支持**: 支持Windows、macOS和Linux
- 📦 **易于使用**: 简单直观的API，轻松集成到项目中

## 安装

```bash
pip install pyfinder
```

## 快速开始

### 搜索Python环境

```python
from pyfinder import find_python_environments

# 查找所有Python环境
environments = find_python_environments()

# 显示找到的环境
for env in environments:
    print(f"{env['name']} ({env['type']}) - {env['version']} - {env['path']}")
```

### 多文件模式运行

```python
from pyfinder import run_with_python

# 使用指定Python运行脚本文件
result = run_with_python("python3.9", "script.py", args=["--arg1", "value1"])

if result["success"]:
    print("运行成功!")
    print(f"输出: {result['stdout']}")
else:
    print("运行失败!")
    print(f"错误: {result['stderr']}")
```

### 单文件模式运行

```python
from pyfinder import auto_run_with_python

# 自动解析当前代码并使用指定Python运行
auto_run_with_python("python3.9")
```

## 高级用法

### 按类型查找Python环境

```python
from pyfinder import find_python_by_type

# 查找所有venv环境
venv_envs = find_python_by_type("venv")

# 查找所有Conda环境
conda_envs = find_python_by_type("conda")
```

### 按版本查找Python环境

```python
from pyfinder import find_python_by_version

# 查找Python 3.9环境
python39_envs = find_python_by_version("3.9")
```

### 运行代码字符串

```python
from pyfinder import run_code_with_python

code = """
import sys
print(f"Hello from Python {sys.version}!")
"""

# 使用指定Python运行代码字符串
result = run_code_with_python("python3.9", code)
print(result["stdout"])
```

### 缓存管理

```python
from pyfinder import clear_cache, refresh_cache

# 清空缓存
clear_cache()

# 刷新缓存
refresh_cache()
```

## 命令行界面

PyFinder也提供了命令行界面：

```bash
# 列出所有Python环境
pyfinder list

# 使用指定Python运行脚本
pyfinder run python3.9 script.py --args

# 查看帮助
pyfinder --help
```

## 示例

### 多文件模式示例

参见 `examples/multi_file_example/` 目录，其中包含：

- `main.py`: 主入口文件，展示如何使用PyFinder运行其他脚本
- `script.py`: 被运行的脚本文件

运行示例：

```bash
cd examples/multi_file_example
python main.py
```

### 单文件模式示例

参见 `examples/single_file_example.py`，展示如何使用PyFinder自动解析并运行当前代码。

运行示例：

```bash
python examples/single_file_example.py
```

## API参考

### 核心函数

- `find_python_environments(refresh_cache=False)`: 查找所有Python环境
- `find_python_by_type(env_type, refresh_cache=False)`: 按类型查找Python环境
- `find_python_by_version(version, refresh_cache=False)`: 按版本查找Python环境
- `find_python_by_name(name, refresh_cache=False)`: 按名称查找Python环境
- `run_with_python(python_identifier, script_path, ...)`: 使用指定Python运行脚本文件
- `auto_run_with_python(python_identifier, ...)`: 自动解析当前代码并运行
- `run_code_with_python(python_identifier, code, ...)`: 使用指定Python运行代码字符串

### 环境信息字典

每个Python环境信息包含以下字段：

- `path`: Python可执行文件路径
- `type`: 环境类型 (system, uv, venv, conda)
- `name`: 环境名称
- `version`: Python版本
- `executable`: 是否可执行

### 运行结果字典

运行结果包含以下字段：

- `success`: 是否成功
- `returncode`: 返回码
- `stdout`: 标准输出
- `stderr`: 标准错误
- `exception`: 异常名称（如果有）

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black pyfinder tests
```

### 类型检查

```bash
mypy pyfinder
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 更新日志

### 0.1.0 (2024-01-01)

- 初始版本发布
- 支持搜索系统Python、UV、venv和Conda环境
- 实现多文件和单文件运行模式
- 添加缓存机制
- 提供完整的测试套件

## 支持

如果您遇到问题或有建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索 [已有问题](https://github.com/pyfinder/pyfinder/issues)
3. 创建 [新问题](https://github.com/pyfinder/pyfinder/issues/new)

## 致谢

感谢所有贡献者和用户的支持！