import unittest
from unittest.mock import patch, MagicMock

from pyfinder.detectors import (
    SystemPythonDetector, UVDetector, VenvDetector, 
    CondaDetector, PythonEnvironmentFinder
)


class TestSystemPythonDetector(unittest.TestCase):
    """测试系统Python检测器"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = SystemPythonDetector()
    
    @patch('pyfinder.detectors.find_executable_in_path')
    @patch('pyfinder.detectors.is_executable')
    @patch('pyfinder.detectors.get_python_version')
    def test_find_python_in_path(self, mock_version, mock_executable, mock_find):
        """测试在PATH中查找Python"""
        # 模拟找到python3
        mock_find.return_value = "/usr/bin/python3"
        mock_executable.return_value = True
        mock_version.return_value = "3.9.7"
        
        environments = self.detector.detect()
        
        # 应该找到至少一个环境
        self.assertGreater(len(environments), 0)
        
        # 检查找到的环境信息
        python_env = next((env for env in environments if env["name"] == "python3"), None)
        self.assertIsNotNone(python_env)
        self.assertEqual(python_env["path"], "/usr/bin/python3")
        self.assertEqual(python_env["type"], "system")
        self.assertEqual(python_env["version"], "3.9.7")


class TestUVDetector(unittest.TestCase):
    """测试UV Python检测器"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = UVDetector()
    
    @patch('pyfinder.detectors.find_executable_in_path')
    @patch('pyfinder.detectors.run_command')
    @patch('pyfinder.detectors.os.path.isfile')
    def test_detect_uv_environments(self, mock_isfile, mock_run, mock_find):
        """测试检测UV环境"""
        # 模拟找到uv命令
        mock_find.return_value = "/usr/local/bin/uv"
        
        # 模拟uv python list的输出
        mock_run.return_value = (0, "3.9.7 /path/to/python3.9\n3.10.0 /path/to/python3.10", "")
        
        # 模拟Python文件存在
        mock_isfile.return_value = True
        
        environments = self.detector.detect()
        
        # 应该找到两个环境
        self.assertEqual(len(environments), 2)
        
        # 检查第一个环境
        env1 = environments[0]
        self.assertEqual(env1["type"], "uv")
        self.assertTrue(env1["name"].startswith("uv_"))
        self.assertIn("3.9.7", env1["name"])


class TestVenvDetector(unittest.TestCase):
    """测试Venv检测器"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = VenvDetector()
    
    @patch('pyfinder.detectors.os.path.isdir')
    @patch('pyfinder.detectors.os.getcwd')
    @patch('pyfinder.detectors.get_home_dir')
    def test_detect_venv_environments(self, mock_home, mock_cwd, mock_isdir):
        """测试检测venv环境"""
        # 模拟当前目录和主目录
        mock_cwd.return_value = "/home/user/project"
        mock_home.return_value = "/home/user"
        
        # 模拟目录存在
        mock_isdir.return_value = True
        
        with patch.object(self.detector, '_find_python_in_venv') as mock_find_python:
            # 模拟找到Python可执行文件
            mock_find_python.return_value = "/home/user/project/venv/bin/python"
            
            environments = self.detector.detect()
            
            # 应该找到至少一个环境
            self.assertGreater(len(environments), 0)
            
            # 检查环境信息
            venv_env = environments[0]
            self.assertEqual(venv_env["type"], "venv")
            self.assertEqual(venv_env["path"], "/home/user/project/venv/bin/python")


class TestCondaDetector(unittest.TestCase):
    """测试Conda检测器"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = CondaDetector()
    
    @patch('pyfinder.detectors.find_executable_in_path')
    @patch('pyfinder.detectors.run_command')
    def test_detect_conda_environments(self, mock_run, mock_find):
        """测试检测Conda环境"""
        # 模拟找到conda命令
        mock_find.return_value = "/opt/conda/bin/conda"
        
        # 模拟conda env list的输出
        mock_run.return_value = (0, "# conda environments:\n#\nbase                  *  /opt/conda\npy39                     /opt/conda/envs/py39", "")
        
        with patch.object(self.detector, '_find_python_in_conda_env') as mock_find_python:
            # 模拟找到Python可执行文件
            mock_find_python.return_value = "/opt/conda/envs/py39/bin/python"
            
            environments = self.detector.detect()
            
            # 应该找到至少一个环境
            self.assertGreater(len(environments), 0)
            
            # 检查环境信息
            conda_env = environments[0]
            self.assertEqual(conda_env["type"], "conda")
            self.assertEqual(conda_env["name"], "py39")
            self.assertEqual(conda_env["path"], "/opt/conda/envs/py39/bin/python")


class TestPythonEnvironmentFinder(unittest.TestCase):
    """测试Python环境查找器"""
    
    def setUp(self):
        """测试前准备"""
        self.finder = PythonEnvironmentFinder(use_cache=False)
    
    @patch('pyfinder.detectors.SystemPythonDetector.detect')
    @patch('pyfinder.detectors.UVDetector.detect')
    @patch('pyfinder.detectors.VenvDetector.detect')
    @patch('pyfinder.detectors.CondaDetector.detect')
    def test_find_all_environments(self, mock_conda, mock_venv, mock_uv, mock_system):
        """测试查找所有环境"""
        # 模拟各检测器返回的环境
        mock_system.return_value = [
            {"path": "/usr/bin/python3", "type": "system", "name": "python3", "version": "3.9.7"}
        ]
        
        mock_uv.return_value = [
            {"path": "/path/to/uv/python", "type": "uv", "name": "uv_3.9.7", "version": "3.9.7"}
        ]
        
        mock_venv.return_value = [
            {"path": "/home/user/venv/bin/python", "type": "venv", "name": "venv", "version": "3.8.10"}
        ]
        
        mock_conda.return_value = [
            {"path": "/opt/conda/envs/py39/bin/python", "type": "conda", "name": "py39", "version": "3.9.7"}
        ]
        
        environments = self.finder.find_all()
        
        # 应该找到4个环境
        self.assertEqual(len(environments), 4)
        
        # 检查各类型环境
        types = [env["type"] for env in environments]
        self.assertIn("system", types)
        self.assertIn("uv", types)
        self.assertIn("venv", types)
        self.assertIn("conda", types)
    
    def test_deduplicate_environments(self):
        """测试去重功能"""
        # 创建重复的环境（相同路径）
        env1 = {"path": "/usr/bin/python3", "type": "system", "name": "python3", "version": "3.9.7"}
        env2 = {"path": "/usr/bin/python3", "type": "system", "name": "python3.9", "version": "3.9.7"}
        env3 = {"path": "/usr/bin/python3.9", "type": "system", "name": "python3.9", "version": "3.9.7"}
        
        unique_envs = self.finder._deduplicate_environments([env1, env2, env3])
        
        # 应该只有两个环境（去重）
        self.assertEqual(len(unique_envs), 2)
        
        paths = [env["path"] for env in unique_envs]
        self.assertIn("/usr/bin/python3", paths)
        self.assertIn("/usr/bin/python3.9", paths)


if __name__ == '__main__':
    unittest.main()