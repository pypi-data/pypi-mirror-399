import os
import sys
import inspect
from typing import List, Dict, Optional, Union, Any

from .detectors import PythonEnvironmentFinder
from .runner import CodeRunner
from .cache import CacheManager


def find_python_environments(refresh_cache: bool = False) -> List[Dict]:
    """
    查找系统中的所有Python环境
    
    Args:
        refresh_cache: 是否刷新缓存
        
    Returns:
        Python环境列表，每个环境包含path、type、name、version等信息
    """
    finder = PythonEnvironmentFinder()
    return finder.find_all(refresh_cache)


def find_python_by_type(env_type: str, refresh_cache: bool = False) -> List[Dict]:
    """
    按类型查找Python环境
    
    Args:
        env_type: 环境类型 (system, uv, venv, conda)
        refresh_cache: 是否刷新缓存
        
    Returns:
        指定类型的Python环境列表
    """
    finder = PythonEnvironmentFinder()
    return finder.find_by_type(env_type, refresh_cache)


def find_python_by_version(version: str, refresh_cache: bool = False) -> List[Dict]:
    """
    按版本查找Python环境
    
    Args:
        version: Python版本 (如 "3.9", "3.9.7")
        refresh_cache: 是否刷新缓存
        
    Returns:
        指定版本的Python环境列表
    """
    finder = PythonEnvironmentFinder()
    return finder.find_by_version(version, refresh_cache)


def find_python_by_name(name: str, refresh_cache: bool = False) -> Optional[Dict]:
    """
    按名称查找Python环境
    
    Args:
        name: 环境名称
        refresh_cache: 是否刷新缓存
        
    Returns:
        指定名称的Python环境或None
    """
    finder = PythonEnvironmentFinder()
    return finder.find_by_name(name, refresh_cache)


def get_python_info(python_identifier: str) -> Optional[Dict]:
    """
    获取特定Python环境的信息
    
    Args:
        python_identifier: Python标识符，可以是路径、名称或版本
        
    Returns:
        Python环境信息或None
    """
    # 首先尝试作为路径
    if os.path.isfile(python_identifier):
        from .utils import get_python_version
        version = get_python_version(python_identifier)
        return {
            "path": python_identifier,
            "type": "custom",
            "name": os.path.basename(python_identifier),
            "version": version,
            "executable": True
        }
    
    # 尝试按名称查找
    env = find_python_by_name(python_identifier)
    if env:
        return env
    
    # 尝试按版本查找
    envs = find_python_by_version(python_identifier)
    if envs:
        return envs[0]
    
    return None


def run_with_python(python_identifier: Union[str, Dict], script_path: str, 
                   args: List[str] = None, cwd: str = None, 
                   env: Dict[str, str] = None, capture_output: bool = True) -> Dict[str, Any]:
    """
    使用指定Python运行脚本文件（多文件模式）
    
    Args:
        python_identifier: Python标识符，可以是路径、名称、版本或环境信息字典
        script_path: 要运行的脚本文件路径
        args: 命令行参数列表
        cwd: 工作目录
        env: 环境变量字典
        capture_output: 是否捕获输出
        
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
    
    # 运行脚本
    return runner.run_script(script_path, args, cwd, env, capture_output)


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


def run_code_with_python(python_identifier: Union[str, Dict], code: str,
                        args: List[str] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
    """
    使用指定Python运行代码字符串（单文件模式）
    
    Args:
        python_identifier: Python标识符，可以是路径、名称、版本或环境信息字典
        code: 要运行的代码字符串
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
    
    # 运行代码
    return runner.run_code(code=code, args=args, env=env)


def clear_cache() -> bool:
    """
    清空Python环境缓存
    
    Returns:
        是否成功清空
    """
    cache_manager = CacheManager()
    return cache_manager.clear_cache()


def refresh_cache() -> None:
    """
    刷新Python环境缓存
    """
    cache_manager = CacheManager()
    cache_manager.refresh_cache()


def list_available_pythons(refresh_cache: bool = False) -> Dict[str, List[Dict]]:
    """
    列出所有可用的Python环境，按类型分组
    
    Args:
        refresh_cache: 是否刷新缓存
        
    Returns:
        按类型分组的Python环境字典
    """
    all_envs = find_python_environments(refresh_cache)
    grouped_envs = {
        "system": [],
        "uv": [],
        "venv": [],
        "conda": [],
        "other": []
    }
    
    for env in all_envs:
        env_type = env.get("type", "other")
        if env_type in grouped_envs:
            grouped_envs[env_type].append(env)
        else:
            grouped_envs["other"].append(env)
    
    return grouped_envs


def get_best_python(version: str = None, env_type: str = None, refresh_cache: bool = False) -> Optional[Dict]:
    """
    获取最佳的Python环境
    
    Args:
        version: 首选的Python版本
        env_type: 首选的环境类型
        refresh_cache: 是否刷新缓存
        
    Returns:
        最佳的Python环境或None
    """
    all_envs = find_python_environments(refresh_cache)
    
    if not all_envs:
        return None
    
    # 如果指定了版本和类型，先尝试精确匹配
    if version and env_type:
        for env in all_envs:
            if (env.get("type") == env_type and 
                env.get("version") and 
                env.get("version").startswith(version)):
                return env
    
    # 如果只指定了版本，查找匹配版本的环境
    if version:
        for env in all_envs:
            if env.get("version") and env.get("version").startswith(version):
                return env
    
    # 如果只指定了类型，查找该类型的环境
    if env_type:
        for env in all_envs:
            if env.get("type") == env_type:
                return env
    
    # 默认返回系统Python
    for env in all_envs:
        if env.get("type") == "system":
            return env
    
    # 如果没有系统Python，返回第一个环境
    return all_envs[0]