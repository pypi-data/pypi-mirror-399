import os
import re
import json
import platform
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set
from pathlib import Path

from .utils import (
    run_command, get_python_version, is_executable, 
    normalize_path, get_home_dir, find_executable_in_path
)
from .cache import CacheManager


class BaseDetector(ABC):
    """
    Python环境检测器基类
    """
    
    @abstractmethod
    def detect(self) -> List[Dict]:
        """
        检测Python环境
        
        Returns:
            检测到的Python环境列表
        """
        pass
    
    def _create_env_info(self, path: str, env_type: str, name: str = None) -> Dict:
        """
        创建环境信息字典
        
        Args:
            path: Python可执行文件路径
            env_type: 环境类型
            name: 环境名称
            
        Returns:
            环境信息字典
        """
        version = get_python_version(path)
        return {
            "path": normalize_path(path),
            "type": env_type,
            "name": name or f"{env_type}_{os.path.basename(path)}",
            "version": version,
            "executable": True
        }


class SystemPythonDetector(BaseDetector):
    """
    系统Python检测器
    """
    
    def detect(self) -> List[Dict]:
        """
        检测系统Python环境
        
        Returns:
            检测到的系统Python环境列表
        """
        environments = []
        
        # 常见的Python可执行文件名
        python_names = ["python", "python3", "python3.7", "python3.8", "python3.9", 
                        "python3.10", "python3.11", "python3.12"]
        
        # 在PATH中查找Python可执行文件
        for name in python_names:
            path = find_executable_in_path(name)
            if path:
                env_info = self._create_env_info(path, "system", name)
                environments.append(env_info)
        
        # 在常见安装路径中查找Python
        common_paths = self._get_common_install_paths()
        for install_path in common_paths:
            if os.path.isdir(install_path):
                for item in os.listdir(install_path):
                    item_path = os.path.join(install_path, item)
                    if os.path.isdir(item_path):
                        # 检查目录中的Python可执行文件
                        python_path = self._find_python_in_dir(item_path)
                        if python_path:
                            env_info = self._create_env_info(python_path, "system", item)
                            environments.append(env_info)
        
        return environments
    
    def _get_common_install_paths(self) -> List[str]:
        """
        获取常见的Python安装路径
        
        Returns:
            常见安装路径列表
        """
        system = platform.system()
        home_dir = get_home_dir()
        
        if system == "Windows":
            return [
                r"C:\Python*",
                r"C:\Program Files\Python*",
                r"C:\Program Files (x86)\Python*",
                os.path.join(home_dir, "AppData", "Local", "Programs", "Python"),
                os.path.join(home_dir, "AppData", "Roaming", "Python")
            ]
        elif system == "Darwin":  # macOS
            return [
                "/usr/bin",
                "/usr/local/bin",
                "/opt/homebrew/bin",
                os.path.join(home_dir, ".pyenv", "versions"),
                os.path.join(home_dir, ".local", "bin")
            ]
        else:  # Linux
            return [
                "/usr/bin",
                "/usr/local/bin",
                "/opt/python",
                os.path.join(home_dir, ".pyenv", "versions"),
                os.path.join(home_dir, ".local", "bin")
            ]
    
    def _find_python_in_dir(self, directory: str) -> Optional[str]:
        """
        在目录中查找Python可执行文件
        
        Args:
            directory: 目录路径
            
        Returns:
            Python可执行文件路径或None
        """
        system = platform.system()
        
        if system == "Windows":
            python_exe = "python.exe"
        else:
            python_exe = "python"
        
        for root, dirs, files in os.walk(directory):
            # 限制搜索深度，避免搜索过深
            level = root.replace(directory, "").count(os.sep)
            if level > 2:
                continue
                
            if python_exe in files:
                python_path = os.path.join(root, python_exe)
                if is_executable(python_path):
                    return python_path
        
        return None


class UVDetector(BaseDetector):
    """
    UV Python环境检测器
    """
    
    def detect(self) -> List[Dict]:
        """
        检测UV管理的Python环境
        
        Returns:
            检测到的UV Python环境列表
        """
        environments = []
        
        # 检查UV是否安装
        uv_path = find_executable_in_path("uv")
        if not uv_path:
            return environments
        
        # 获取UV管理的Python版本
        code, stdout, _ = run_command([uv_path, "python", "list"])
        if code != 0:
            return environments
        
        # 解析输出，提取Python版本和路径
        for line in stdout.splitlines():
            match = re.search(r"(\d+\.\d+\.\d+)\s+(.*)", line.strip())
            if match:
                version = match.group(1)
                path = match.group(2).strip()
                
                # 构建Python可执行文件路径
                if platform.system() == "Windows":
                    python_path = os.path.join(path, "python.exe")
                else:
                    python_path = os.path.join(path, "bin", "python")
                
                if os.path.isfile(python_path):
                    env_info = self._create_env_info(python_path, "uv", f"uv_{version}")
                    environments.append(env_info)
        
        return environments


class VenvDetector(BaseDetector):
    """
    Venv虚拟环境检测器
    """
    
    def detect(self) -> List[Dict]:
        """
        检测venv虚拟环境
        
        Returns:
            检测到的venv环境列表
        """
        environments = []
        
        # 常见的虚拟环境目录
        venv_dirs = self._get_venv_directories()
        
        for venv_dir in venv_dirs:
            if os.path.isdir(venv_dir):
                # 查找虚拟环境中的Python可执行文件
                python_path = self._find_python_in_venv(venv_dir)
                if python_path:
                    env_name = os.path.basename(venv_dir)
                    env_info = self._create_env_info(python_path, "venv", env_name)
                    environments.append(env_info)
        
        return environments
    
    def _get_venv_directories(self) -> List[str]:
        """
        获取可能的虚拟环境目录列表
        
        Returns:
            虚拟环境目录列表
        """
        venv_dirs = []
        current_dir = os.getcwd()
        home_dir = get_home_dir()
        
        # 当前目录及其父目录中的常见虚拟环境目录
        search_dirs = [current_dir]
        parent_dir = os.path.dirname(current_dir)
        while parent_dir and parent_dir != os.path.dirname(parent_dir):
            search_dirs.append(parent_dir)
            parent_dir = os.path.dirname(parent_dir)
        
        # 添加用户主目录
        search_dirs.append(home_dir)
        
        # 在每个目录中查找常见的虚拟环境目录名
        for directory in search_dirs:
            for venv_name in ["venv", ".venv", "env", ".env", "virtualenv"]:
                venv_path = os.path.join(directory, venv_name)
                if os.path.isdir(venv_path):
                    venv_dirs.append(venv_path)
        
        return venv_dirs
    
    def _find_python_in_venv(self, venv_dir: str) -> Optional[str]:
        """
        在虚拟环境目录中查找Python可执行文件
        
        Args:
            venv_dir: 虚拟环境目录
            
        Returns:
            Python可执行文件路径或None
        """
        if platform.system() == "Windows":
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")
        
        if os.path.isfile(python_path) and is_executable(python_path):
            return python_path
        
        return None


class CondaDetector(BaseDetector):
    """
    Conda环境检测器
    """
    
    def detect(self) -> List[Dict]:
        """
        检测Conda环境
        
        Returns:
            检测到的Conda环境列表
        """
        environments = []
        
        # 检查conda是否安装
        conda_path = find_executable_in_path("conda")
        if not conda_path:
            return environments
        
        # 获取conda环境列表
        code, stdout, _ = run_command([conda_path, "env", "list"])
        if code != 0:
            return environments
        
        # 解析输出，提取环境路径
        for line in stdout.splitlines():
            line = line.strip()
            # 跳过注释和空行
            if line.startswith("#") or not line:
                continue
            
            # 提取环境名称和路径
            parts = line.split()
            if len(parts) >= 1:
                env_name = parts[0]
                
                # 获取环境路径
                if len(parts) >= 2:
                    env_path = parts[1]
                else:
                    # 使用默认路径
                    env_path = self._get_default_conda_env_path(env_name)
                
                # 查找Python可执行文件
                python_path = self._find_python_in_conda_env(env_path)
                if python_path:
                    env_info = self._create_env_info(python_path, "conda", env_name)
                    environments.append(env_info)
        
        return environments
    
    def _get_default_conda_env_path(self, env_name: str) -> str:
        """
        获取conda环境的默认路径
        
        Args:
            env_name: 环境名称
            
        Returns:
            环境路径
        """
        # 尝试从conda配置中获取envs_dirs
        conda_path = find_executable_in_path("conda")
        if conda_path:
            code, stdout, _ = run_command([conda_path, "config", "--show", "envs_dirs"])
            if code == 0:
                for line in stdout.splitlines():
                    if line.strip().startswith("envs_dirs"):
                        # 提取路径列表
                        paths_str = line.split(":", 1)[1].strip()
                        paths = [p.strip().strip('"\'') for p in paths_str.split(",")]
                        if paths:
                            return os.path.join(paths[0], env_name)
        
        # 默认路径
        home_dir = get_home_dir()
        if platform.system() == "Windows":
            return os.path.join(home_dir, "Anaconda3", "envs", env_name)
        else:
            return os.path.join(home_dir, "anaconda3", "envs", env_name)
    
    def _find_python_in_conda_env(self, env_path: str) -> Optional[str]:
        """
        在conda环境中查找Python可执行文件
        
        Args:
            env_path: conda环境路径
            
        Returns:
            Python可执行文件路径或None
        """
        if not os.path.isdir(env_path):
            return None
        
        if platform.system() == "Windows":
            python_path = os.path.join(env_path, "python.exe")
        else:
            python_path = os.path.join(env_path, "bin", "python")
        
        if os.path.isfile(python_path) and is_executable(python_path):
            return python_path
        
        return None


class PythonEnvironmentFinder:
    """
    Python环境查找器，整合所有检测器
    """
    
    def __init__(self, use_cache: bool = True, cache_expiry: int = 24 * 60 * 60):
        """
        初始化Python环境查找器
        
        Args:
            use_cache: 是否使用缓存
            cache_expiry: 缓存过期时间（秒）
        """
        self.use_cache = use_cache
        self.cache_manager = CacheManager(cache_expiry) if use_cache else None
        self.detectors = [
            SystemPythonDetector(),
            UVDetector(),
            VenvDetector(),
            CondaDetector()
        ]
    
    def find_all(self, refresh_cache: bool = False) -> List[Dict]:
        """
        查找所有Python环境
        
        Args:
            refresh_cache: 是否刷新缓存
            
        Returns:
            所有Python环境列表
        """
        # 如果使用缓存且缓存有效，直接返回缓存结果
        if self.use_cache and not refresh_cache and self.cache_manager.is_cache_valid():
            return list(self.cache_manager.get_environments().values())
        
        # 使用所有检测器查找Python环境
        all_environments = []
        for detector in self.detectors:
            try:
                environments = detector.detect()
                all_environments.extend(environments)
            except Exception as e:
                # 记录错误但继续使用其他检测器
                print(f"检测器 {detector.__class__.__name__} 出错: {e}")
        
        # 去重（基于路径）
        unique_environments = self._deduplicate_environments(all_environments)
        
        # 更新缓存
        if self.use_cache:
            self.cache_manager.clear_cache()
            for env in unique_environments:
                env_id = f"{env['type']}_{env['name']}"
                self.cache_manager.add_environment(env_id, env)
        
        return unique_environments
    
    def find_by_type(self, env_type: str, refresh_cache: bool = False) -> List[Dict]:
        """
        按类型查找Python环境
        
        Args:
            env_type: 环境类型 (system, uv, venv, conda)
            refresh_cache: 是否刷新缓存
            
        Returns:
            指定类型的Python环境列表
        """
        all_environments = self.find_all(refresh_cache)
        return [env for env in all_environments if env["type"] == env_type]
    
    def find_by_version(self, version: str, refresh_cache: bool = False) -> List[Dict]:
        """
        按版本查找Python环境
        
        Args:
            version: Python版本 (如 "3.9", "3.9.7")
            refresh_cache: 是否刷新缓存
            
        Returns:
            指定版本的Python环境列表
        """
        all_environments = self.find_all(refresh_cache)
        return [env for env in all_environments if env["version"] and env["version"].startswith(version)]
    
    def find_by_name(self, name: str, refresh_cache: bool = False) -> Optional[Dict]:
        """
        按名称查找Python环境
        
        Args:
            name: 环境名称
            refresh_cache: 是否刷新缓存
            
        Returns:
            指定名称的Python环境或None
        """
        all_environments = self.find_all(refresh_cache)
        for env in all_environments:
            if env["name"] == name:
                return env
        return None
    
    def _deduplicate_environments(self, environments: List[Dict]) -> List[Dict]:
        """
        去除重复的Python环境（基于路径）
        
        Args:
            environments: 原始环境列表
            
        Returns:
            去重后的环境列表
        """
        seen_paths = set()
        unique_environments = []
        
        for env in environments:
            path = env["path"]
            if path not in seen_paths:
                seen_paths.add(path)
                unique_environments.append(env)
        
        return unique_environments