#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 配置管理器 - 加载和缓存 RAG 配置
"""

import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent / "config.json"

# 默认配置（与 config.json 同步）
DEFAULT_CONFIG = {
    "rag_config": {
        "开关控制": {
            "enable_limit_and_dedupe": False,
            "enable_cache": False,
            "enable_log_compression": True
        },
        "检索参数": {
            "vector_search_enabled": True,
            "keyword_search_enabled": True,
            "vector_search_weight": 0.7,
            "keyword_search_weight": 0.3,
            "max_results": 5,
            "max_tokens": 1000,
            "similarity_threshold": 0.75
        },
        "缓存参数": {
            "ttl_seconds": 3600,
            "max_cache_size": 100,
            "cleanup_interval_seconds": 300
        },
        "日志参数": {
            "log_dir": "/home/admin/.openclaw/workspace/memory/logs",
            "compression_day_of_month": 1,
            "months_to_keep_detailed": 1,
            "compress_months_ago": 2,
            "retain_detailed_days": 30,
            "simplification_ratio": 0.3
        }
    }
}


def load_config() -> Dict[str, Any]:
    """加载 RAG 配置"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> None:
    """保存 RAG 配置"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_switch_state(switch_name: str) -> bool:
    """快速获取某个开关的状态"""
    config = load_config()
    switches = config.get("rag_config", {}).get("开关控制", {})
    return switches.get(switch_name, False)


def is_dedupe_enabled() -> bool:
    return get_switch_state("enable_limit_and_dedupe")


def is_cache_enabled() -> bool:
    return get_switch_state("enable_cache")


def is_log_compression_enabled() -> bool:
    return get_switch_state("enable_log_compression")
