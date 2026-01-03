"""
PyFinder - Python环境搜索与运行工具包

一个强大的Python包，用于搜索系统中的Python环境（系统Python、UV、venv、Conda），
并支持多种方式运行Python文件。

主要功能：
- 搜索系统中的Python环境
- 支持多文件和单文件运行模式
- 缓存Python目录信息
- 跨平台支持（Windows、macOS、Linux）
"""

__version__ = "0.1.0"
__author__ = "PyFinder Team"

from .core import find_python_environments, run_with_python, auto_run_with_python
from .detectors import PythonEnvironmentFinder
from .runner import MultiFileRunner, SingleFileRunner
from .cache import CacheManager

__all__ = [
    "find_python_environments",
    "run_with_python", 
    "auto_run_with_python",
    "PythonEnvironmentFinder",
    "MultiFileRunner",
    "SingleFileRunner",
    "CacheManager"
]