#!/usr/bin/env python3
"""
多文件模式示例 - 主入口文件

这个示例展示了如何使用PyFinder的多文件模式运行Python脚本
"""

import sys
import os

# 添加pyfinder模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pyfinder import find_python_environments, run_with_python


def main():
    """主函数"""
    print("PyFinder 多文件模式示例")
    print("=" * 40)
    
    # 查找所有Python环境
    print("1. 查找系统中的Python环境:")
    environments = find_python_environments()
    
    if not environments:
        print("  未找到任何Python环境")
        return
    
    # 显示找到的环境
    for i, env in enumerate(environments[:5]):  # 只显示前5个
        print(f"  {i+1}. {env['name']} ({env['type']}) - {env['version']} - {env['path']}")
    
    if len(environments) > 5:
        print(f"  ... 还有 {len(environments)-5} 个环境")
    
    # 选择一个Python环境
    if len(environments) > 0:
        selected_env = environments[0]
        print(f"\n2. 使用第一个环境运行脚本: {selected_env['name']}")
        
        # 运行脚本文件
        script_path = os.path.join(os.path.dirname(__file__), "script.py")
        result = run_with_python(
            selected_env, 
            script_path, 
            args=["--name", "PyFinder"],
            capture_output=True
        )
        
        print("\n3. 运行结果:")
        print(f"  成功: {result['success']}")
        print(f"  返回码: {result['returncode']}")
        
        if result['stdout']:
            print(f"  输出:\n{result['stdout']}")
        
        if result['stderr']:
            print(f"  错误:\n{result['stderr']}")
    
    print("\n示例完成!")


if __name__ == "__main__":
    main()