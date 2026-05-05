#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 处理器 - 结果去重、Token 限制、排序
"""

from typing import List, Dict, Any
from config_manager import is_dedupe_enabled


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数（~1.3 字符/token 的粗略估算）"""
    return int(len(text) / 1.3)


def content_similarity(text_a: str, text_b: str) -> float:
    """基于公共子串比例的简单内容相似度计算"""
    # 使用较简单的方式：计算公共词的比例
    words_a = set(text_a.lower().split()[:50])
    words_b = set(text_b.lower().split()[:50])
    
    if not words_a or not words_b:
        return 0.0
    
    intersection = words_a & words_b
    union = words_a | words_b
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def deduplicate_by_similarity(results: List[Dict], threshold: float = 0.8) -> List[Dict]:
    """基于内容相似度的去重"""
    if not results:
        return results
    
    deduped = []
    
    for result in results:
        is_duplicate = False
        
        for existing in deduped:
            sim = content_similarity(result.get("content", ""), existing.get("content", ""))
            if sim >= threshold:
                # 保留分数更高的那个
                if result.get("score", 0) > existing.get("score", 0):
                    deduped.remove(existing)
                    deduped.append(result)
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduped.append(result)
    
    return deduped


def limit_by_tokens(results: List[Dict], max_tokens: int = 1000) -> List[Dict]:
    """按 Token 数量限制结果"""
    total_tokens = 0
    limited = []
    
    for result in results:
        tokens = estimate_tokens(result.get("content", ""))
        if total_tokens + tokens <= max_tokens:
            limited.append(result)
            total_tokens += tokens
        else:
            if limited:
                break  # 已经超出限制，停止
            else:
                # 至少保留一个结果
                limited.append(result)
                break
    
    return limited


def process_results(results: List[Dict], max_tokens: int = 1000) -> List[Dict]:
    """处理检索结果：去重 + Token 限制（按开关控制）"""
    if not results:
        return results
    
    # 去重（仅开关开启时）
    if is_dedupe_enabled():
        results = deduplicate_by_similarity(results)
        results = limit_by_tokens(results, max_tokens)
    
    # 重新排序（按分数降序）
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return results
