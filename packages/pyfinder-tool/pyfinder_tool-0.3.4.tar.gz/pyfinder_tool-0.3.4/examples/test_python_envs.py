#!/usr/bin/env python3
"""
Python环境测试脚本

这个脚本用于测试和验证系统中的Python环境
"""

import sys
import os

# 添加pyfinder模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyfinder import find_python_environments


def main():
    """主函数"""
    print("Python环境测试脚本")
    print("=" * 50)
    
    # 查找所有Python环境
    print("\n查找系统中的Python环境...")
    environments = find_python_environments()
    
    if not environments:
        print("未找到任何Python环境")
        return
    
    # 显示所有找到的环境
    print(f"\n找到 {len(environments)} 个Python环境:")
    for i, env in enumerate(environments):
        print(f"{i+1}. {env['name']} ({env['type']}) - {env['version']} - {env['path']}")
    
    # 测试每个环境
    print("\n测试Python环境:")
    for env in environments:
        print(f"\n测试 {env['name']} ({env['type']})...")
        try:
            import subprocess
            result = subprocess.run(
                [env['path'], "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_output = result.stdout.strip()
                print(f"  版本: {version_output}")
                print(f"  路径: {env['path']}")
            else:
                print(f"  错误: {result.stderr.strip()}")
        except Exception as e:
            print(f"  异常: {e}")
    
    print("\n测试完成!")


if __name__ == "__main__":
    main()