#!/usr/bin/env python3
"""
单文件模式示例

这个示例展示了如何使用PyFinder的单文件模式自动解析并运行当前代码
"""

import sys
import os

# 添加pyfinder模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyfinder import find_python_environments, auto_run_with_python


def calculate_fibonacci(n):
    """计算斐波那契数列的第n项"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)


def main():
    """主函数"""
    print("PyFinder 单文件模式示例")
    print("=" * 40)
    
    # 查找所有Python环境
    print("1. 查找系统中的Python环境:")
    environments = find_python_environments()
    
    if not environments:
        print("  未找到任何Python环境")
        return
    
    # 显示找到的环境
    for i, env in enumerate(environments[:3]):  # 只显示前3个
        print(f"  {i+1}. {env['name']} ({env['type']}) - {env['version']}")
    
    # 选择一个Python环境
    if len(environments) > 0:
        selected_env = environments[0]
        print(f"\n2. 使用第一个环境运行代码: {selected_env['name']}")
        
        # 计算斐波那契数列
        n = 10
        print(f"\n3. 计算斐波那契数列的第{n}项:")
        result = calculate_fibonacci(n)
        print(f"   结果: {result}")
        
        # 如果这是被PyFinder运行的，显示额外信息
        if len(sys.argv) > 1 and sys.argv[1] == "--pyfinder-run":
            print("\n4. 这个代码是由PyFinder自动解析并运行的!")
            print(f"   使用的Python: {sys.executable}")
    
    print("\n示例完成!")


# 这个条件检查是为了避免在直接运行时执行auto_run_with_python
# 当使用PyFinder运行时，这个条件会为False，代码会被PyFinder执行
if __name__ == "__main__" and "--pyfinder-run" not in sys.argv:
    # 直接运行时，使用PyFinder自动解析并运行当前代码
    print("直接运行此脚本，将使用PyFinder自动解析并运行...")
    auto_run_with_python("python3.9")  # 尝试使用Python 3.9运行
else:
    # 被PyFinder运行时，执行主函数
    main()