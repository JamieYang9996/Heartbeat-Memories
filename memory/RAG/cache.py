#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 内存缓存 - 查询结果缓存（开关控制，默认关闭）
"""

import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from config_manager import is_cache_enabled


class MemoryCache:
    """LRU 风格的内存缓存，支持 TTL 过期"""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._last_cleanup: float = 0
        self._cleanup_interval: float = 300  # 5 分钟
    
    def _should_cleanup(self) -> bool:
        return (time.time() - self._last_cleanup) >= self._cleanup_interval
    
    def _cleanup(self):
        """清理过期缓存"""
        now = time.time()
        expired = [k for k, v in self._cache.items() if now - v["timestamp"] >= v["ttl"]]
        for k in expired:
            del self._cache[k]
        self._last_cleanup = now
    
    def _make_key(self, query: str, limit: int) -> str:
        """生成缓存键"""
        raw = f"{query}|{limit}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def get(self, query: str, limit: int = 5) -> Optional[List[Dict]]:
        """获取缓存结果"""
        if not is_cache_enabled():
            return None
        
        if self._should_cleanup():
            self._cleanup()
        
        key = self._make_key(query, limit)
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        # 检查是否过期
        if time.time() - entry["timestamp"] >= entry["ttl"]:
            del self._cache[key]
            return None
        
        entry["hits"] = entry.get("hits", 0) + 1
        return entry["data"]
    
    def set(self, query: str, limit: int, data: List[Dict], ttl: int = 3600):
        """设置缓存"""
        if not is_cache_enabled():
            return
        
        key = self._make_key(query, limit)
        self._cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl,
            "hits": 0
        }
        
        # 限制缓存大小
        max_size = 100
        if len(self._cache) > max_size:
            # 移除最旧的条目
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest]
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
    
    def stats(self) -> Dict:
        """缓存统计"""
        now = time.time()
        active = sum(1 for v in self._cache.values() if now - v["timestamp"] < v["ttl"])
        total_hits = sum(v.get("hits", 0) for v in self._cache.values())
        return {
            "total_entries": len(self._cache),
            "active_entries": active,
            "total_hits": total_hits
        }


# 全局单例
_global_cache = None


def get_cache() -> MemoryCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MemoryCache()
    return _global_cache
