import os
import json
import time
from typing import Dict, List, Optional, Any
from .utils import get_cache_dir, read_json_file, write_json_file


class CacheManager:
    """
    缓存管理器，用于存储和管理Python环境信息
    """
    
    CACHE_FILE = os.path.join(get_cache_dir(), "python_environments.json")
    DEFAULT_EXPIRY = 24 * 60 * 60  # 24小时（秒）
    
    def __init__(self, expiry_seconds: int = DEFAULT_EXPIRY):
        """
        初始化缓存管理器
        
        Args:
            expiry_seconds: 缓存过期时间（秒）
        """
        self.expiry_seconds = expiry_seconds
        self._cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """
        加载缓存数据
        
        Returns:
            缓存数据字典
        """
        cache_data = read_json_file(self.CACHE_FILE)
        
        # 检查缓存是否过期
        if self._is_cache_expired(cache_data):
            return {"environments": {}, "last_updated": 0}
        
        return cache_data
    
    def _is_cache_expired(self, cache_data: Dict[str, Any]) -> bool:
        """
        检查缓存是否过期
        
        Args:
            cache_data: 缓存数据
            
        Returns:
            是否过期
        """
        last_updated = cache_data.get("last_updated", 0)
        current_time = int(time.time())
        return (current_time - last_updated) > self.expiry_seconds
    
    def _save_cache(self) -> bool:
        """
        保存缓存数据
        
        Returns:
            是否成功保存
        """
        self._cache_data["last_updated"] = int(time.time())
        return write_json_file(self.CACHE_FILE, self._cache_data)
    
    def get_environments(self) -> Dict[str, Dict]:
        """
        获取所有缓存的Python环境
        
        Returns:
            Python环境字典
        """
        return self._cache_data.get("environments", {})
    
    def get_environment(self, env_id: str) -> Optional[Dict]:
        """
        获取特定的Python环境
        
        Args:
            env_id: 环境ID
            
        Returns:
            环境信息字典或None
        """
        return self.get_environments().get(env_id)
    
    def add_environment(self, env_id: str, env_info: Dict) -> None:
        """
        添加Python环境到缓存
        
        Args:
            env_id: 环境ID
            env_info: 环境信息
        """
        if "environments" not in self._cache_data:
            self._cache_data["environments"] = {}
        
        self._cache_data["environments"][env_id] = env_info
        self._save_cache()
    
    def remove_environment(self, env_id: str) -> bool:
        """
        从缓存中移除Python环境
        
        Args:
            env_id: 环境ID
            
        Returns:
            是否成功移除
        """
        if env_id in self._cache_data.get("environments", {}):
            del self._cache_data["environments"][env_id]
            return self._save_cache()
        return False
    
    def clear_cache(self) -> bool:
        """
        清空缓存
        
        Returns:
            是否成功清空
        """
        self._cache_data = {"environments": {}, "last_updated": 0}
        return self._save_cache()
    
    def is_cache_valid(self) -> bool:
        """
        检查缓存是否有效
        
        Returns:
            缓存是否有效
        """
        return not self._is_cache_expired(self._cache_data)
    
    def refresh_cache(self) -> None:
        """
        刷新缓存（清空并重新标记更新时间）
        """
        self._cache_data = {"environments": {}, "last_updated": int(time.time())}
        self._save_cache()