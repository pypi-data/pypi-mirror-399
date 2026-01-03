import os
import sys
import inspect
import tempfile
from typing import List, Dict, Optional, Union, Any

from .utils import run_command, normalize_path
from .detectors import PythonEnvironmentFinder
from .runner import CodeRunner


def split_and_run_with_python(
    current_python: str, 
    target_python: str, 
    args: List[str] = None, 
    env: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    分割运行：当前Python运行到auto_run_with_python，然后由目标Python运行剩余代码
    
    Args:
        current_python: 当前运行的Python标识符
        target_python: 目标Python标识符，用于运行剩余代码
        args: 命令行参数列表
        env: 环境变量字典
        
    Returns:
        运行结果字典
    """
    # 获取调用栈信息
    stack = inspect.stack()
    frame = stack[1] if len(stack) > 1 else stack[0]
    
    # 获取当前文件路径和行号
    file_path = frame.filename
    call_line = frame.lineno
    
    # 读取整个文件
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 提取从调用行开始的代码
    remaining_code = "".join(lines[call_line:])
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(remaining_code)
        temp_file_path = temp_file.name
    
    try:
        # 获取目标Python环境信息
        from .core import get_python_info
        env_info = get_python_info(target_python)
        if not env_info:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"无法找到Python环境: {target_python}",
                "exception": "PythonNotFoundError"
            }
        
        # 创建代码运行器
        runner = CodeRunner(python_path=env_info["path"])
        
        # 运行剩余代码
        result = runner.run_code(code=remaining_code, args=args, env=env)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "exception": type(e).__name__
        }
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except Exception:
            pass


def auto_run_with_python(python_identifier: Union[str, Dict], 
                        args: List[str] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
    """
    自动解析当前代码并使用指定Python运行（单文件模式）
    
    Args:
        python_identifier: Python标识符，可以是路径、名称、版本或环境信息字典
        args: 命令行参数列表
        env: 环境变量字典
        
    Returns:
        运行结果字典
    """
    # 处理python_identifier参数
    python_path = None
    python_name = None
    python_version = None
    env_type = None
    
    if isinstance(python_identifier, dict):
        python_path = python_identifier.get("path")
        python_name = python_identifier.get("name")
        python_version = python_identifier.get("version")
        env_type = python_identifier.get("type")
    else:
        # 尝试获取Python环境信息
        from .core import get_python_info
        env_info = get_python_info(python_identifier)
        if env_info:
            python_path = env_info["path"]
            python_name = env_info["name"]
            python_version = env_info["version"]
            env_type = env_info["type"]
    
    # 创建代码运行器
    runner = CodeRunner(
        python_path=python_path,
        python_name=python_name,
        python_version=python_version,
        env_type=env_type
    )
    
    # 获取调用栈信息
    stack = inspect.stack()
    frame = stack[1] if len(stack) > 1 else stack[0]
    
    # 运行代码
    return runner.run_code(frame=frame, args=args, env=env)


def split_run_with_py37_and_py312(
    args: List[str] = None, 
    env: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    专门用于Python 3.7和Python 3.12的分割运行
    
    Args:
        args: 命令行参数列表
        env: 环境变量字典
        
    Returns:
        运行结果字典
    """
    return split_and_run_with_python("python3.7", "python3.12", args, env)