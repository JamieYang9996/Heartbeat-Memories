#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBM Retriever - 混合检索器
向量搜索（ChromaDB）+ 关键词搜索（文件 grep）
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# 导入配置和向量库
from config_manager import load_config
from memory_connector import get_chroma_client, get_embedding_fn

WORKSPACE = Path(os.environ.get("HBM_ROOT", os.path.expanduser("~/.openclaw/skills/hbm")))

# 五个记忆库的文件路径映射
MEMORY_FILES = {
    "目标记忆库": WORKSPACE / "memory/目标记忆库/GOALS.md",
    "会话记忆库": WORKSPACE / "memory/会话记忆库",
    "版本记忆库": WORKSPACE / "memory/版本记忆库/CHANGELOG.md",
    "经验记忆库": WORKSPACE / "memory/经验记忆库/TIPS.md",
    "情感记忆库": WORKSPACE / "memory/情感记忆库/DAILY_EMOTIONS.md"
}

CHROMA_COLLECTION_NAMES = {
    "目标记忆库": "goals_local",
    "会话记忆库": "conversations_local",
    "版本记忆库": "system_changelog_local",
    "经验记忆库": "experiences_local",
    "情感记忆库": "ideas_local"  # 复用 ideas 集合
}

# Chroma collections 对应的中文名
CHROMA_TO_CHINESE = {v: k for k, v in CHROMA_COLLECTION_NAMES.items()}


class HBMRetriever:
    """混合检索器 - 向量 + 关键词"""
    
    def __init__(self):
        self.config = load_config()
        self.rag_config = self.config.get("rag_config", {})
        self.search_params = self.rag_config.get("检索参数", {})
        
        # 初始化 ChromaDB
        self.client = get_chroma_client()
        self.embedding_fn = get_embedding_fn()
        
        # 缓存集合引用
        self._collections = {}
    
    def _get_collection(self, name: str):
        """获取 Chroma 集合（带缓存）"""
        if name not in self._collections:
            try:
                self._collections[name] = self.client.get_collection(name)
            except Exception:
                self._collections[name] = None
        return self._collections[name]
    
    def retrieve(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """主检索接口：混合检索所有记忆库"""
        if limit is None:
            limit = self.search_params.get("max_results", 5)
        
        results = []
        
        # 1. 向量搜索
        if self.search_params.get("vector_search_enabled", True):
            vector_results = self._vector_search(query, limit * 2)
            results.extend(vector_results)
        
        # 2. 关键词搜索
        if self.search_params.get("keyword_search_enabled", True):
            keyword_results = self._keyword_search(query, limit)
            results.extend(keyword_results)
        
        # 3. 合并排序
        results = self._merge_and_rank(results, query)
        
        return results[:limit]
    
    def _vector_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """向量搜索：遍历所有 Chroma 集合"""
        results = []
        query_vector = self.embedding_fn([query])[0]
        
        for chinese_name, collection_name in CHROMA_COLLECTION_NAMES.items():
            collection = self._get_collection(collection_name)
            if collection is None or collection.count() == 0:
                continue
            
            try:
                result = collection.query(
                    query_embeddings=[query_vector],
                    n_results=min(limit, collection.count()),
                    include=["documents", "metadatas", "distances"]
                )
                
                for i, doc in enumerate(result["documents"][0]):
                    distance = result["distances"][0][i] if result["distances"] else 1.0
                    similarity = 1.0 - distance  # Chroma 返回的是 L2 距离
                    
                    # 应用相似度阈值
                    threshold = self.search_params.get("similarity_threshold", 0.75)
                    # Chroma L2 距离转相似度: 距离接近0 = 高度相似
                    # 对于 all-MiniLM-L6-v2，L2 距离通常 < 2.0
                    score = max(0, 1.0 - distance / 2.0)
                    
                    if score >= threshold * 0.5:  # 放宽阈值，关键词补充
                        results.append({
                            "source": chinese_name,
                            "source_type": "vector",
                            "content": doc,
                            "metadata": result["metadatas"][0][i] if result["metadatas"] else {},
                            "score": score,
                            "method": "vector"
                        })
            except Exception as e:
                pass  # 跳过空集合或错误
        
        return results
    
    def _keyword_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """关键词搜索：在 Markdown 文件中 grep"""
        results = []
        
        # 提取关键词（中文分词简化版：按空格/标点分隔）
        keywords = self._extract_keywords(query)
        if not keywords:
            return results
        
        # 对每个记忆库文件进行 grep
        for mem_type, file_path in MEMORY_FILES.items():
            if not file_path.exists():
                continue
            
            if file_path.is_dir():
                # 会话记忆库是目录，查所有 .md 文件
                md_files = list(file_path.glob("*.md"))
                for md_file in md_files[-10:]:  # 只查最近 10 个文件
                    hits = self._grep_file(md_file, keywords)
                    for hit in hits:
                        results.append({
                            "source": mem_type,
                            "source_type": "file",
                            "content": hit["content"],
                            "metadata": {"file": md_file.name, "source_line": hit["line"]},
                            "score": hit["score"] * 0.6,  # 关键词权重稍低
                            "method": "keyword"
                        })
            else:
                hits = self._grep_file(file_path, keywords)
                for hit in hits:
                    results.append({
                        "source": mem_type,
                        "source_type": "file",
                        "content": hit["content"],
                        "metadata": {"file": file_path.name},
                        "score": hit["score"] * 0.6,
                        "method": "keyword"
                    })
        
        return results
    
    def _grep_file(self, file_path: Path, keywords: List[str], context_lines: int = 3) -> List[Dict]:
        """在文件中搜索关键词，返回匹配行及其上下文"""
        results = []
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                matched_keywords = [kw for kw in keywords if kw.lower() in line_lower]
                
                if matched_keywords:
                    # 提取上下文（前后几行）
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    context = "\n".join(lines[start:end])
                    
                    score = len(matched_keywords) / len(keywords)
                    
                    results.append({
                        "line": i + 1,
                        "content": context,
                        "score": score,
                        "matched_keywords": matched_keywords
                    })
        except Exception:
            pass
        
        return results
    
    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词"""
        # 移除常见停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
                      "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
                      "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "什么",
                      "怎么", "如何", "为什么", "那个", "这个", "哪些", "现在"}
        
        # 简单分词：按空格、标点拆分
        tokens = re.split(r'[\s,，。！？、；：""''【】（）()\.\,\?\!\;\:\s]+', query)
        keywords = [t.strip() for t in tokens if t.strip() and len(t.strip()) >= 2 and t.strip() not in stop_words]
        
        return keywords
    
    def _merge_and_rank(self, results: List[Dict], query: str) -> List[Dict]:
        """合并向量和关键词结果，按相关性排序"""
        if not results:
            return results
        
        # 去重（基于内容相似度合并）
        merged = {}
        for r in results:
            # 使用内容前 50 个字作为去重 key
            content_key = r["content"][:100].strip()
            if content_key in merged:
                # 更新分数（取最大值）
                merged[content_key]["score"] = max(merged[content_key]["score"], r["score"])
                # 合并方法标记
                if r["method"] not in merged[content_key]["methods"]:
                    merged[content_key]["methods"].append(r["method"])
            else:
                r["methods"] = [r["method"]]
                merged[content_key] = r
        
        # 按分数降序排列
        ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        
        return ranked


def retrieve(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """便捷检索接口"""
    retriever = HBMRetriever()
    return retriever.retrieve(query, limit)
