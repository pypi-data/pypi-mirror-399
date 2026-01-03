#!/usr/bin/env python3
"""
多文件模式示例 - 脚本文件

这个文件被main.py调用，演示多文件模式的运行
"""

import sys
import argparse


def greet(name):
    """问候函数"""
    return f"你好, {name}! 这是一个由PyFinder运行的脚本。"


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="PyFinder多文件模式示例脚本")
    parser.add_argument("--name", default="World", help="要问候的名字")
    args = parser.parse_args()
    
    # 打印问候语
    message = greet(args.name)
    print(message)
    
    # 打印Python信息
    print(f"当前Python版本: {sys.version}")
    print(f"Python可执行文件: {sys.executable}")
    
    # 模拟一些工作
    print("正在执行一些计算...")
    result = sum(range(100))
    print(f"计算结果: {result}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())