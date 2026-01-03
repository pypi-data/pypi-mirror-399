import os
import sys
import subprocess
import json
import platform
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """
    运行系统命令并返回结果
    
    Args:
        cmd: 要执行的命令列表
        capture_output: 是否捕获输出
        
    Returns:
        返回码、标准输出、标准错误
    """
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, timeout=10)
            return result.returncode, "", ""
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        return 1, "", str(e)


def get_python_version(python_path: str) -> Optional[str]:
    """
    获取Python版本信息
    
    Args:
        python_path: Python可执行文件路径
        
    Returns:
        Python版本字符串或None
    """
    try:
        code, stdout, _ = run_command([python_path, "--version"])
        if code == 0:
            version = stdout.strip()
            # 处理不同格式的版本输出
            if version.startswith("Python "):
                version = version[7:]
            return version
    except Exception:
        pass
    return None


def is_executable(file_path: str) -> bool:
    """
    检查文件是否可执行
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否可执行
    """
    if not os.path.isfile(file_path):
        return False
    
    if platform.system() == "Windows":
        return file_path.lower().endswith((".exe", ".bat", ".cmd"))
    else:
        return os.access(file_path, os.X_OK)


def normalize_path(path: str) -> str:
    """
    标准化路径
    
    Args:
        path: 原始路径
        
    Returns:
        标准化后的路径
    """
    return os.path.normpath(os.path.expanduser(path))


def get_home_dir() -> str:
    """
    获取用户主目录
    
    Returns:
        用户主目录路径
    """
    return os.path.expanduser("~")


def get_cache_dir() -> str:
    """
    获取缓存目录
    
    Returns:
        缓存目录路径
    """
    if platform.system() == "Windows":
        cache_dir = os.environ.get("LOCALAPPDATA", os.path.join(get_home_dir(), "AppData", "Local"))
    elif platform.system() == "Darwin":  # macOS
        cache_dir = os.path.join(get_home_dir(), "Library", "Caches")
    else:  # Linux
        cache_dir = os.environ.get("XDG_CACHE_HOME", os.path.join(get_home_dir(), ".cache"))
    
    pyfinder_cache = os.path.join(cache_dir, "pyfinder")
    os.makedirs(pyfinder_cache, exist_ok=True)
    return pyfinder_cache


def find_executable_in_path(name: str) -> Optional[str]:
    """
    在PATH中查找可执行文件
    
    Args:
        name: 可执行文件名
        
    Returns:
        可执行文件路径或None
    """
    if platform.system() == "Windows":
        extensions = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(";")
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            for ext in extensions:
                full_path = os.path.join(path_dir, name + ext)
                if is_executable(full_path):
                    return full_path
    else:
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            full_path = os.path.join(path_dir, name)
            if is_executable(full_path):
                return full_path
    return None


def read_json_file(file_path: str) -> Dict:
    """
    读取JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的字典，出错时返回空字典
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json_file(file_path: str, data: Dict) -> bool:
    """
    写入JSON文件
    
    Args:
        file_path: JSON文件路径
        data: 要写入的数据
        
    Returns:
        是否成功写入
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False