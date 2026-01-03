#!/usr/bin/env python3
"""
生产级别分割运行示例

这个示例展示了如何使用PyFinder的交互式分割运行功能，
让Python 3.7环境运行到split_run_with_py37_and_py312这一行，
然后由Python 3.12环境接管并执行剩余代码，支持完整的交互式输入输出。
"""

import sys
import os

# 添加pyfinder模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyfinder import split_run_with_py37_and_py312


def main():
    """主函数 - 这部分代码由Python 3.7环境执行"""
    print("PyFinder 交互式分割运行示例")
    print("=" * 50)
    
    # 这部分代码由Python 3.7环境执行
    print(f"[Python 3.7环境] 当前Python版本: {sys.version}")
    print(f"[Python 3.7环境] 当前Python可执行文件: {sys.executable}")
    print("[Python 3.7环境] 这部分代码由Python 3.7环境执行...")
    print("[Python 3.7环境] 即将切换到Python 3.12环境执行剩余代码...")
    
    # 以下代码将由Python 3.12环境执行，并支持交互式输入输出
    split_run_with_py37_and_py312(interactive=True)


# 这部分代码由Python 3.12环境执行
def py312_interactive_code():
    """这部分代码由Python 3.12环境执行，支持交互式输入输出"""
    print("\n" + "=" * 50)
    print("[Python 3.12环境] 现在切换到Python 3.12环境...")
    print(f"[Python 3.12环境] 新Python版本: {sys.version}")
    print(f"[Python 3.12环境] 新Python可执行文件: {sys.executable}")
    
    # 尝试导入一些可能只在Python 3.12中安装的模块
    try:
        import torch
        print(f"[Python 3.12环境] 成功导入torch，版本: {torch.__version__}")
    except ImportError:
        print("[Python 3.12环境] 警告: torch模块未安装")
    
    try:
        import numpy as np
        print(f"[Python 3.12环境] 成功导入numpy，版本: {np.__version__}")
    except ImportError:
        print("[Python 3.12环境] 警告: numpy模块未安装")
    
    # 交互式输入示例
    print("\n[Python 3.12环境] 交互式输入示例:")
    name = input("[Python 3.12环境] 请输入您的名字: ")
    print(f"[Python 3.12环境] 您好, {name}!")
    
    # 执行一些计算
    print("\n[Python 3.12环境] 执行一些计算...")
    result = sum(range(100))
    print(f"[Python 3.12环境] 计算结果: {result}")
    
    # 更多交互式示例
    print("\n[Python 3.12环境] 更多交互式示例:")
    while True:
        command = input("[Python 3.12环境] 输入命令 (math/exit): ").strip().lower()
        
        if command == "exit":
            print("[Python 3.12环境] 退出交互模式")
            break
        elif command == "math":
            try:
                expr = input("[Python 3.12环境] 输入数学表达式: ")
                result = eval(expr)
                print(f"[Python 3.12环境] 结果: {result}")
            except Exception as e:
                print(f"[Python 3.12环境] 错误: {e}")
        else:
            print("[Python 3.12环境] 未知命令，请重试")
    
    print("\n[Python 3.12环境] 交互式分割运行完成!")


if __name__ == "__main__":
    main()