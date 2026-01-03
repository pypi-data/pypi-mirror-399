#!/usr/bin/env python3
"""
分割运行示例

这个示例展示了如何使用PyFinder的分割运行功能，
让Python 3.7环境运行到auto_run_with_python这一行，
然后由Python 3.12环境接管并执行剩余代码。
"""

import sys
import os

# 添加pyfinder模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyfinder import split_run_with_py37_and_py312


def main():
    """主函数"""
    print("PyFinder 分割运行示例")
    print("=" * 40)
    
    # 这部分代码由Python 3.7环境执行
    print(f"当前Python版本: {sys.version}")
    print(f"当前Python可执行文件: {sys.executable}")
    print("这部分代码由Python 3.7环境执行...")
    
    # 以下代码将由Python 3.12环境执行
    split_run_with_py37_and_py312()


# 这部分代码由Python 3.12环境执行
def py312_code():
    """这部分代码由Python 3.12环境执行"""
    print("\n现在切换到Python 3.12环境...")
    print(f"新Python版本: {sys.version}")
    print(f"新Python可执行文件: {sys.executable}")
    
    # 尝试导入一些可能只在Python 3.12中安装的模块
    try:
        import torch
        print(f"成功导入torch，版本: {torch.__version__}")
    except ImportError:
        print("警告: torch模块未安装")
    
    try:
        import numpy as np
        print(f"成功导入numpy，版本: {np.__version__}")
    except ImportError:
        print("警告: numpy模块未安装")
    
    # 执行一些计算
    print("\n执行一些计算...")
    result = sum(range(100))
    print(f"计算结果: {result}")
    
    print("\n分割运行完成!")


if __name__ == "__main__":
    main()