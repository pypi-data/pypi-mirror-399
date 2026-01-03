import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from pyfinder.cache import CacheManager


class TestCacheManager(unittest.TestCase):
    """测试缓存管理器"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录作为缓存目录
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")
        
        # 创建缓存管理器实例
        with patch('pyfinder.cache.get_cache_dir', return_value=self.temp_dir):
            self.cache_manager = CacheManager(expiry_seconds=3600)  # 1小时过期
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件和目录
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.temp_dir)
    
    def test_init_creates_cache_file(self):
        """测试初始化是否创建缓存文件"""
        self.assertTrue(os.path.exists(self.cache_file))
    
    def test_add_and_get_environment(self):
        """测试添加和获取环境"""
        env_info = {
            "path": "/usr/bin/python3",
            "type": "system",
            "name": "python3",
            "version": "3.9.7"
        }
        
        # 添加环境
        self.cache_manager.add_environment("test_env", env_info)
        
        # 获取环境
        retrieved_env = self.cache_manager.get_environment("test_env")
        self.assertEqual(retrieved_env, env_info)
    
    def test_get_environments(self):
        """测试获取所有环境"""
        env1 = {
            "path": "/usr/bin/python3",
            "type": "system",
            "name": "python3",
            "version": "3.9.7"
        }
        
        env2 = {
            "path": "/home/user/.venv/bin/python",
            "type": "venv",
            "name": "venv",
            "version": "3.8.10"
        }
        
        # 添加环境
        self.cache_manager.add_environment("env1", env1)
        self.cache_manager.add_environment("env2", env2)
        
        # 获取所有环境
        all_envs = self.cache_manager.get_environments()
        self.assertEqual(len(all_envs), 2)
        self.assertEqual(all_envs["env1"], env1)
        self.assertEqual(all_envs["env2"], env2)
    
    def test_remove_environment(self):
        """测试移除环境"""
        env_info = {
            "path": "/usr/bin/python3",
            "type": "system",
            "name": "python3",
            "version": "3.9.7"
        }
        
        # 添加环境
        self.cache_manager.add_environment("test_env", env_info)
        self.assertIsNotNone(self.cache_manager.get_environment("test_env"))
        
        # 移除环境
        result = self.cache_manager.remove_environment("test_env")
        self.assertTrue(result)
        self.assertIsNone(self.cache_manager.get_environment("test_env"))
    
    def test_clear_cache(self):
        """测试清空缓存"""
        env_info = {
            "path": "/usr/bin/python3",
            "type": "system",
            "name": "python3",
            "version": "3.9.7"
        }
        
        # 添加环境
        self.cache_manager.add_environment("test_env", env_info)
        
        # 清空缓存
        result = self.cache_manager.clear_cache()
        self.assertTrue(result)
        self.assertEqual(len(self.cache_manager.get_environments()), 0)
    
    def test_cache_expiry(self):
        """测试缓存过期"""
        # 创建一个已过期的缓存
        expired_cache = {
            "environments": {
                "test_env": {
                    "path": "/usr/bin/python3",
                    "type": "system",
                    "name": "python3",
                    "version": "3.9.7"
                }
            },
            "last_updated": 0  # 很久以前的时间戳
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(expired_cache, f)
        
        # 重新加载缓存管理器
        with patch('pyfinder.cache.get_cache_dir', return_value=self.temp_dir):
            cache_manager = CacheManager(expiry_seconds=3600)
        
        # 缓存应该为空，因为已过期
        self.assertEqual(len(cache_manager.get_environments()), 0)
    
    def test_refresh_cache(self):
        """测试刷新缓存"""
        env_info = {
            "path": "/usr/bin/python3",
            "type": "system",
            "name": "python3",
            "version": "3.9.7"
        }
        
        # 添加环境
        self.cache_manager.add_environment("test_env", env_info)
        
        # 刷新缓存
        self.cache_manager.refresh_cache()
        
        # 缓存应该为空，但last_updated应该是最新的
        self.assertEqual(len(self.cache_manager.get_environments()), 0)
        self.assertGreater(self.cache_manager._cache_data["last_updated"], 0)


if __name__ == '__main__':
    unittest.main()