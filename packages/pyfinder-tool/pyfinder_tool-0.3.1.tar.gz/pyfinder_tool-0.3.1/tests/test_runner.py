import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open

from pyfinder.runner import CodeRunner, MultiFileRunner, SingleFileRunner, CodeParser


class TestCodeParser(unittest.TestCase):
    """测试代码解析器"""
    
    def test_extract_code_from_file(self):
        """测试从文件提取代码"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write("print('Hello, world!')\n")
            temp_file_path = temp_file.name
        
        try:
            # 提取代码
            code = CodeParser.extract_code_from_file(temp_file_path)
            
            # 验证代码内容
            self.assertEqual(code, "print('Hello, world!')\n")
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
    
    def test_extract_code_from_file_error(self):
        """测试从不存在的文件提取代码"""
        with self.assertRaises(ValueError):
            CodeParser.extract_code_from_file("/nonexistent/file.py")


class TestMultiFileRunner(unittest.TestCase):
    """测试多文件运行器"""
    
    def setUp(self):
        """测试前准备"""
        self.python_path = "/usr/bin/python3"
        self.runner = MultiFileRunner(self.python_path)
    
    @patch('pyfinder.runner.subprocess.run')
    def test_run_script_success(self, mock_subprocess):
        """测试成功运行脚本"""
        # 模拟subprocess.run返回成功结果
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, world!\n"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # 运行脚本
        result = self.runner.run("/path/to/script.py", ["--arg1", "value1"])
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["stdout"], "Hello, world!\n")
        self.assertEqual(result["stderr"], "")
        
        # 验证subprocess.run被正确调用
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        self.assertEqual(args[0][0], self.python_path)
        self.assertEqual(args[0][1], "/path/to/script.py")
        self.assertEqual(args[0][2], "--arg1")
        self.assertEqual(args[0][3], "value1")
    
    @patch('pyfinder.runner.subprocess.run')
    def test_run_script_failure(self, mock_subprocess):
        """测试运行脚本失败"""
        # 模拟subprocess.run返回失败结果
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: Something went wrong\n"
        mock_subprocess.return_value = mock_result
        
        # 运行脚本
        result = self.runner.run("/path/to/script.py")
        
        # 验证结果
        self.assertFalse(result["success"])
        self.assertEqual(result["returncode"], 1)
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "Error: Something went wrong\n")
    
    def test_run_script_not_found(self):
        """测试运行不存在的脚本"""
        # 运行不存在的脚本
        result = self.runner.run("/nonexistent/script.py")
        
        # 验证结果
        self.assertFalse(result["success"])
        self.assertEqual(result["returncode"], -1)
        self.assertIn("脚本文件不存在", result["stderr"])


class TestSingleFileRunner(unittest.TestCase):
    """测试单文件运行器"""
    
    def setUp(self):
        """测试前准备"""
        self.python_path = "/usr/bin/python3"
        self.runner = SingleFileRunner(self.python_path)
    
    @patch('pyfinder.runner.subprocess.run')
    @patch('pyfinder.runner.tempfile.NamedTemporaryFile')
    def test_run_code_success(self, mock_temp_file, mock_subprocess):
        """测试成功运行代码"""
        # 模拟临时文件
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/temp_script.py"
        mock_temp.__enter__.return_value = mock_temp
        mock_temp_file.return_value = mock_temp
        
        # 模拟subprocess.run返回成功结果
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, world!\n"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # 运行代码
        result = self.runner.run(code="print('Hello, world!')")
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["stdout"], "Hello, world!\n")
        self.assertEqual(result["stderr"], "")
        
        # 验证临时文件被创建和写入
        mock_temp_file.assert_called_once()
        mock_temp.write.assert_called_once_with("print('Hello, world!')")
        
        # 验证subprocess.run被正确调用
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        self.assertEqual(args[0][0], self.python_path)
        self.assertEqual(args[0][1], "/tmp/temp_script.py")


class TestCodeRunner(unittest.TestCase):
    """测试代码运行器"""
    
    @patch('pyfinder.runner.PythonEnvironmentFinder')
    def test_init_with_python_path(self, mock_finder):
        """测试使用Python路径初始化"""
        # 创建代码运行器
        runner = CodeRunner(python_path="/usr/bin/python3")
        
        # 验证Python路径被设置
        self.assertEqual(runner.python_path, "/usr/bin/python3")
        
        # 验证PythonEnvironmentFinder没有被调用
        mock_finder.assert_not_called()
    
    @patch('pyfinder.runner.PythonEnvironmentFinder')
    @patch('pyfinder.runner.shutil.which')
    def test_init_without_python_path(self, mock_which, mock_finder):
        """测试不使用Python路径初始化"""
        # 模拟shutil.which返回Python路径
        mock_which.return_value = "/usr/bin/python3"
        
        # 创建代码运行器
        runner = CodeRunner()
        
        # 验证Python路径被设置
        self.assertEqual(runner.python_path, "/usr/bin/python3")
        
        # 验证shutil.which被调用
        mock_which.assert_called_once_with("python")
        
        # 验证PythonEnvironmentFinder没有被调用
        mock_finder.assert_not_called()
    
    @patch('pyfinder.runner.MultiFileRunner')
    def test_run_script(self, mock_runner_class):
        """测试运行脚本"""
        # 模拟MultiFileRunner
        mock_runner = MagicMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.run.return_value = {"success": True, "returncode": 0}
        
        # 创建代码运行器
        runner = CodeRunner(python_path="/usr/bin/python3")
        
        # 运行脚本
        result = runner.run_script("/path/to/script.py", ["--arg1", "value1"])
        
        # 验证MultiFileRunner被创建和调用
        mock_runner_class.assert_called_once_with("/usr/bin/python3")
        mock_runner.run.assert_called_once_with(
            "/path/to/script.py", ["--arg1", "value1"], None, None, True
        )
        
        # 验证返回结果
        self.assertEqual(result, {"success": True, "returncode": 0})
    
    @patch('pyfinder.runner.SingleFileRunner')
    def test_run_code(self, mock_runner_class):
        """测试运行代码"""
        # 模拟SingleFileRunner
        mock_runner = MagicMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.run.return_value = {"success": True, "returncode": 0}
        
        # 创建代码运行器
        runner = CodeRunner(python_path="/usr/bin/python3")
        
        # 运行代码
        result = runner.run_code(code="print('Hello, world!')")
        
        # 验证SingleFileRunner被创建和调用
        mock_runner_class.assert_called_once_with("/usr/bin/python3")
        mock_runner.run.assert_called_once_with(
            code="print('Hello, world!')", frame=None, args=None, env=None
        )
        
        # 验证返回结果
        self.assertEqual(result, {"success": True, "returncode": 0})


if __name__ == '__main__':
    unittest.main()