import os
import sys
import subprocess
import tempfile
import inspect
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from .utils import run_command, normalize_path
from .detectors import PythonEnvironmentFinder


class CodeParser:
    """
    代码解析器，用于解析Python文件内容
    """
    
    @staticmethod
    def extract_code_from_file(file_path: str) -> str:
        """
        从文件中提取代码
        
        Args:
            file_path: Python文件路径
            
        Returns:
            文件中的代码内容
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"无法读取文件 {file_path}: {e}")
    
    @staticmethod
    def extract_code_from_frame(frame: Optional[inspect.FrameInfo] = None) -> str:
        """
        从调用栈中提取代码
        
        Args:
            frame: 调用栈帧信息，如果为None则使用调用者的帧
            
        Returns:
            提取的代码内容
        """
        if frame is None:
            # 获取调用者的帧
            stack = inspect.stack()
            # 跳过当前函数和调用者函数的帧
            if len(stack) > 2:
                frame = stack[2]
            else:
                frame = stack[1]
        
        try:
            # 获取源代码文件路径和行号
            file_path = frame.filename
            start_line = frame.lineno
            
            # 读取整个文件
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 提取从调用行开始的代码
            # 这里简单实现，实际可能需要更复杂的解析来获取完整的代码块
            code_lines = []
            for i in range(start_line - 1, len(lines)):
                line = lines[i]
                code_lines.append(line)
                # 简单的结束条件：遇到空行或缩进减少
                if i > start_line - 1 and line.strip() == "":
                    break
                if i > start_line and not line.startswith(" " * 4) and not line.startswith("\t"):
                    break
            
            return "".join(code_lines)
        except Exception as e:
            raise ValueError(f"无法从调用栈提取代码: {e}")


class BaseRunner(ABC):
    """
    代码运行器基类
    """
    
    def __init__(self, python_path: str):
        """
        初始化代码运行器
        
        Args:
            python_path: Python可执行文件路径
        """
        self.python_path = normalize_path(python_path)
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        运行代码
        
        Returns:
            运行结果字典，包含返回码、输出等信息
        """
        pass


class MultiFileRunner(BaseRunner):
    """
    多文件模式运行器
    """
    
    def run(self, script_path: str, args: List[str] = None, cwd: str = None, 
            env: Dict[str, str] = None, capture_output: bool = True) -> Dict[str, Any]:
        """
        使用指定Python运行脚本文件
        
        Args:
            script_path: 要运行的脚本文件路径
            args: 命令行参数列表
            cwd: 工作目录
            env: 环境变量字典
            capture_output: 是否捕获输出
            
        Returns:
            运行结果字典
        """
        script_path = normalize_path(script_path)
        
        if not os.path.isfile(script_path):
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"脚本文件不存在: {script_path}",
                "exception": None
            }
        
        # 构建命令
        cmd = [self.python_path, script_path]
        if args:
            cmd.extend(args)
        
        # 设置工作目录
        if cwd is None:
            cwd = os.path.dirname(script_path)
        
        # 运行命令
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                return {
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exception": None
                }
            else:
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    env=env,
                    timeout=300  # 5分钟超时
                )
                return {
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "stdout": "",
                    "stderr": "",
                    "exception": None
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "执行超时",
                "exception": "TimeoutExpired"
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "exception": type(e).__name__
            }


class SingleFileRunner(BaseRunner):
    """
    单文件模式运行器
    """
    
    def run(self, code: str = None, frame: inspect.FrameInfo = None, 
            args: List[str] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
        """
        运行代码（从字符串或调用栈中提取）
        
        Args:
            code: 要运行的代码字符串，如果为None则从frame中提取
            frame: 调用栈帧信息，用于提取代码
            args: 命令行参数列表
            env: 环境变量字典
            
        Returns:
            运行结果字典
        """
        # 如果没有提供代码，尝试从调用栈中提取
        if code is None:
            if frame is None:
                # 获取调用者的帧
                stack = inspect.stack()
                if len(stack) > 2:
                    frame = stack[2]
                else:
                    frame = stack[1]
            
            try:
                code = CodeParser.extract_code_from_frame(frame)
            except Exception as e:
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"无法提取代码: {e}",
                    "exception": "CodeExtractionError"
                }
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # 构建命令
            cmd = [self.python_path, temp_file_path]
            if args:
                cmd.extend(args)
            
            # 运行命令
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                timeout=300  # 5分钟超时
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exception": None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "执行超时",
                "exception": "TimeoutExpired"
            }
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


class CodeRunner:
    """
    代码运行器，提供统一的接口运行Python代码
    """
    
    def __init__(self, python_path: str = None, python_name: str = None, 
                 python_version: str = None, env_type: str = None):
        """
        初始化代码运行器
        
        Args:
            python_path: Python可执行文件路径
            python_name: Python环境名称
            python_version: Python版本
            env_type: 环境类型 (system, uv, venv, conda)
        """
        self.python_path = python_path
        self.python_name = python_name
        self.python_version = python_version
        self.env_type = env_type
        
        # 如果没有提供python_path，尝试查找
        if not self.python_path:
            self._find_python()
        
        if not self.python_path:
            raise ValueError("无法找到指定的Python环境")
    
    def _find_python(self) -> None:
        """
        查找Python环境
        """
        finder = PythonEnvironmentFinder()
        
        if self.python_name:
            # 按名称查找
            env = finder.find_by_name(self.python_name)
            if env:
                self.python_path = env["path"]
                return
        
        if self.python_version:
            # 按版本查找
            envs = finder.find_by_version(self.python_version)
            if envs:
                self.python_path = envs[0]["path"]
                return
        
        if self.env_type:
            # 按类型查找
            envs = finder.find_by_type(self.env_type)
            if envs:
                self.python_path = envs[0]["path"]
                return
        
        # 如果没有找到，尝试使用系统默认Python
        import shutil
        python_path = shutil.which("python")
        if python_path:
            self.python_path = python_path
    
    def run_script(self, script_path: str, args: List[str] = None, cwd: str = None, 
                   env: Dict[str, str] = None, capture_output: bool = True) -> Dict[str, Any]:
        """
        运行脚本文件（多文件模式）
        
        Args:
            script_path: 要运行的脚本文件路径
            args: 命令行参数列表
            cwd: 工作目录
            env: 环境变量字典
            capture_output: 是否捕获输出
            
        Returns:
            运行结果字典
        """
        runner = MultiFileRunner(self.python_path)
        return runner.run(script_path, args, cwd, env, capture_output)
    
    def run_code(self, code: str = None, frame: inspect.FrameInfo = None, 
                 args: List[str] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
        """
        运行代码（单文件模式）
        
        Args:
            code: 要运行的代码字符串，如果为None则从frame中提取
            frame: 调用栈帧信息，用于提取代码
            args: 命令行参数列表
            env: 环境变量字典
            
        Returns:
            运行结果字典
        """
        runner = SingleFileRunner(self.python_path)
        return runner.run(code, frame, args, env)
    
    def get_python_info(self) -> Dict[str, str]:
        """
        获取Python环境信息
        
        Returns:
            Python环境信息字典
        """
        from .utils import get_python_version
        
        return {
            "path": self.python_path,
            "version": get_python_version(self.python_path) or "Unknown",
            "name": self.python_name or "Unknown",
            "type": self.env_type or "Unknown"
        }


# 导入ABC模块
from abc import ABC