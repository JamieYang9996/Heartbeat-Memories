#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 上下文组装器 - 将检索结果格式化为 LLM 友好的 prompt 片段
"""

from typing import List, Dict, Any
from datetime import datetime
from processor import process_results, estimate_tokens


def assemble_context(results: List[Dict], query: str = "", max_tokens: int = 1000) -> str:
    """
    将检索结果组装成结构化的上下文片段
    
    Args:
        results: 检索结果列表
        query: 原始查询
        max_tokens: 最大 token 数
    
    Returns:
        格式化的上下文字符串
    """
    if not results:
        return ""
    
    # 处理结果（去重 + Token 限制）
    processed = process_results(results, max_tokens)
    
    if not processed:
        return ""
    
    parts = []
    parts.append("📚 —— 记忆库检索辅助 ——")
    parts.append(f"查询: \"{query}\"")
    parts.append(f"检索时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    parts.append("")
    
    for i, result in enumerate(processed, 1):
        source = result.get("source", "未知来源")
        score = result.get("score", 0)
        content = result.get("content", "")
        method = " / ".join(result.get("methods", [result.get("method", "unknown")]))
        file_meta = result.get("metadata", {}).get("file", "")
        
        # 截断过长的内容
        if len(content) > 500:
            content = content[:500] + "..."
        
        parts.append(f"--- 片段 {i} [来源: {source}] [相关度: {score:.2f}] [方法: {method}] ---")
        if file_meta:
            parts.append(f"文件: {file_meta}")
        parts.append(content)
        parts.append("")
    
    parts.append("—— 记忆库检索结束 ——")
    
    context_text = "\n".join(parts)
    
    # 整体 Token 限制
    if estimate_tokens(context_text) > max_tokens:
        # 如果整体超限，只保留相关性最高的片段
        parts = parts[:8]  # 保留头部 + 最多 3 个片段 (每个片段 3 行)
        parts.append("(因篇幅限制，部分检索结果已省略)")
        parts.append("—— 记忆库检索结束 ——")
        context_text = "\n".join(parts)
    
    return context_text


def format_for_bootstrap(results: List[Dict], query: str = "") -> str:
    """
    精简版上下文组装（用于 bootstrap 或简短提示）
    """
    if not results:
        return ""
    
    processed = process_results(results, max_tokens=300)
    
    lines = ["[记忆检索片段]"]
    for i, r in enumerate(processed[:3], 1):
        source = r.get("source", "?")
        content = r.get("content", "").replace("\n", " ")[:200]
        lines.append(f"  [{i}][{source}] {content}")
    
    return "\n".join(lines)
