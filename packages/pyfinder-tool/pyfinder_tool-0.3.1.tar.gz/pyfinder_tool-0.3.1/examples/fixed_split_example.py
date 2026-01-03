#!/usr/bin/env python3
"""
生产级别分割运行示例 - 修复版

这个示例展示了如何使用PyFinder的交互式分割运行功能，
并确保真正切换到不同的Python环境。
"""

import sys
import os

# 添加pyfinder模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyfinder import find_python_environments, split_and_run_with_python


def main():
    """主函数 - 这部分代码由Python 3.7环境执行"""
    print("PyFinder 交互式分割运行示例")
    print("=" * 50)
    
    # 这部分代码由Python 3.7环境执行
    print(f"[Python 3.7环境] 当前Python版本: {sys.version}")
    print(f"[Python 3.7环境] 当前Python可执行文件: {sys.executable}")
    
    # 查找所有Python环境
    print("\n[Python 3.7环境] 查找系统中的Python环境...")
    environments = find_python_environments()
    
    # 找到Python 3.12环境
    py312_env = None
    for env in environments:
        if env.get("version", "").startswith("3.12"):
            py312_env = env
            break
    
    if not py312_env:
        print("[Python 3.7环境] 警告: 未找到Python 3.12环境")
        return
    
    print(f"[Python 3.7环境] 找到Python 3.12环境: {py312_env['path']}")
    print(f"[Python 3.7环境] 这部分代码由Python 3.7环境执行...")
    print("[Python 3.7环境] 即将切换到Python 3.12环境执行剩余代码...")
    
    # 使用找到的Python 3.12环境路径进行分割运行
    result = split_and_run_with_python(
        current_python="python3.7", 
        target_python=py312_env['path'],  # 使用完整路径而不是名称
        interactive=True
    )
    
    print(f"\n[Python 3.7环境] 分割运行完成，返回码: {result['returncode']}")


if __name__ == "__main__":
    main()