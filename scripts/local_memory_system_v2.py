#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地记忆系统 - 使用外部指定 ONNX 模型
==========================================
避免 ChromaDB 自动下载 onnx.tar.gz 的问题

适配 HBM Skill 版本：从环境变量读取配置
"""

import chromadb
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import sys
import os

# ==================== 配置区域 ====================

# 从环境变量读取路径，支持 HBM Skill 安装
def get_hbm_path():
    """获取 HBM 根目录"""
    # 1. 检查环境变量
    hbm_root = os.getenv("HBM_ROOT")
    if hbm_root:
        return Path(hbm_root).expanduser().resolve()
    
    # 2. 检查默认 OpenClaw 技能目录
    possible_paths = [
        Path.home() / ".openclaw" / "skills" / "hbm",
        Path.home() / "AppData" / "Local" / "openclaw" / "skills" / "hbm",  # Windows
        Path.home() / "Library" / "Application Support" / "openclaw" / "skills" / "hbm",  # macOS
    ]
    
    for path in possible_paths:
        if path.exists():
            return path.resolve()
    
    # 3. 如果都不存在，使用当前脚本所在目录的上两级
    return Path(__file__).parent.parent.resolve()

# 计算路径
HBM_ROOT = get_hbm_path()
WORKSPACE_PATH = HBM_ROOT
MEMORY_DB_PATH = HBM_ROOT / "memory" / "语义搜索_db"
MODEL_PATH = HBM_ROOT / "models" / "all-MiniLM-L6-v2" / "sentence-transformers" / "all-MiniLM-L6-v2"

print(f"🔧 HBM 路径配置:")
print(f"  • HBM_ROOT: {HBM_ROOT}")
print(f"  • 记忆库: {MEMORY_DB_PATH}")
print(f"  • 模型: {MODEL_PATH}")

# ==================== 向量化器 (使用本地已下载的模型) ====================

class LocalSentenceTransformerEF:
    """自定义 Embedding Function，使用已下载的 all-MiniLM-L6-v2"""
    
    def __init__(self):
        print(f"\n加载本地模型：{MODEL_PATH}")
        self.model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)
        print(f"✓ 模型加载成功！向量维度：{self.model.get_sentence_embedding_dimension()}")
    
    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input, show_progress_bar=False)
        return embeddings.tolist()


# ==================== 核心类定义 ====================

class LocalMemorySystem:
    """本地语义记忆系统 - 使用指定的 ONNX 模型"""
    
    def __init__(self):
        """初始化 ChromaDB 客户端和集合"""
        # 创建 ChromaDB 实例但不启用自动向量化
        client = chromadb.PersistentClient(
            path=str(MEMORY_DB_PATH),
            settings=chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 创建 5 个记忆集合
        self.collections = {
            "对话记录": client.get_or_create_collection(name="conversations_local", metadata={"description": "每日会话梗概"}),
            "系统版本": client.get_or_create_collection(name="system_changelog_local", metadata={"description": "版本更新记录"}),
            "经验教训": client.get_or_create_collection(name="experiences_local", metadata={"description": "问题与解决方案"}),
            "待办目标": client.get_or_create_collection(name="goals_local", metadata={"description": "用户目标跟踪"}),
            "想法灵感": client.get_or_create_collection(name="ideas_local", metadata={"description": "创意想法收集"})
        }
        
        # 初始化向量化器
        self.embedding_fn = LocalSentenceTransformerEF()
        
        print("✅ 本地记忆系统初始化完成！")
        print(f"   数据库路径：{MEMORY_DB_PATH}")
        print(f"   ONNX 模型：{MODEL_PATH}")
        
    def add_experience(self, problem: str, solution: str, is_highlighted: bool = False):
        """添加经验教训"""
        collection = self.collections["经验教训"]
        
        record_text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}]\n问题：{problem}\n\n解决方案：{solution}"
        meta = {
            "highlighted": is_highlighted,
            "created_at": datetime.now().isoformat(),
            "type": "经验教训"
        }
        
        # 获取向量表示
        vectors = self.embedding_fn([record_text])
        
        collection.add(
            documents=[record_text],
            metadatas=[meta],
            ids=[f"exp_{len(record_text)}_{hash(record_text) % 10000}"],
            embeddings=vectors
        )
        print(f"✓ 已添加经验 [{'⭐高亮' if is_highlighted else '普通'}]")
        
    def add_goal(self, goal: str, background: str, reason: str, temporary_solution: str):
        """添加目标"""
        collection = self.collections["待办目标"]
        
        created_at = datetime.now().strftime("%Y-%m-%d")
        record_text = f"[{created_at}]\n目标：{goal}\n\n背景：{background}\n原因：{reason}\n暂时方案：{temporary_solution}"
        meta = {
            "goal_summary": goal[:50],
            "created_date": created_at,
            "status": "pending",
            "type": "待办目标"
        }
        
        # 获取向量表示
        vectors = self.embedding_fn([record_text])
        
        collection.add(
            documents=[record_text],
            metadatas=[meta],
            ids=[f"goal_{len(record_text)}_{hash(record_text) % 10000}"],
            embeddings=vectors
        )
        print(f"✓ 已添加目标：{goal[:30]}...")
        
    def add_idea(self, idea: str, context: str):
        """添加灵感想法"""
        collection = self.collections["想法灵感"]
        
        created_at = datetime.now().strftime("%Y-%m-%d")
        record_text = f"[{created_at}]\n灵感：{idea}\n\n背景：{context}"
        meta = {
            "idea_summary": idea[:50],
            "context": context[:50],
            "created_date": created_at,
            "type": "想法灵感"
        }
        
        # 获取向量表示
        vectors = self.embedding_fn([record_text])
        
        collection.add(
            documents=[record_text],
            metadatas=[meta],
            ids=[f"idea_{len(record_text)}_{hash(record_text) % 10000}"],
            embeddings=vectors
        )
        print(f"✓ 已添加灵感：{idea[:30]}...")
        
    def search_memories(self, query: str, top_k: int = 5, memory_type: Optional[str] = None) -> List[Dict]:
        """语义搜索所有记忆"""
        results = []
        
        target_types = [memory_type] if memory_type else list(self.collections.keys())
        
        # 将查询转换为向量
        query_vector = self.embedding_fn([query])[0]
        
        for mem_type in target_types:
            if mem_type not in self.collections:
                continue
                
            collection = self.collections[mem_type]
            
            if collection.count() > 0:
                result = collection.query(
                    query_embeddings=[query_vector],
                    n_results=min(top_k // len(self.collections), collection.count()),
                    include=["documents", "metadatas", "distances"]
                )
                
                for i, doc in enumerate(result["documents"][0]):
                    results.append({
                        "type": mem_type,
                        "content": doc,
                        "metadata": result["metadatas"][0][i] if result["metadatas"] else {},
                        "similarity": 1 - result["distances"][0][i] if result["distances"] else 0
                    })
        
        # 按相似度排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
        
    def list_all_memories(self, memory_type: Optional[str] = None):
        """列出所有记忆内容"""
        print("\n📋 记忆库列表:")
        target_types = [memory_type] if memory_type else list(self.collections.keys())
        
        for mem_type in target_types:
            if mem_type not in self.collections:
                continue
            
            collection = self.collections[mem_type]
            count = collection.count()
            print(f"\n  • {mem_type}: {count} 条记录")
            
            # 显示最新 3 条
            if count > 0:
                result = collection.get(limit=3, include=["documents", "metadatas"])
                for i, doc in enumerate(result["documents"]):
                    preview = doc.replace("\n", " ").replace(" ", "")[:80] + "..."
                    print(f"    [{i+1}] {preview}")


if __name__ == "__main__":
    print("=" * 70)
    print("OpenClaw 本地记忆系统 v2.0 - 使用本地已下载模型")
    print("=" * 70)
    
    # 初始化系统
    system = LocalMemorySystem()
    
    print("\n📋 可用命令:")
    print("  add_exp <问题> <解决方案> [--highlight]")
    print("  add_goal <目标> <背景> <原因> <暂时方案>")
    print("  add_idea <灵感> <背景>")
    print("  search <关键词> ([类型])")
    print("  list ([类型])")
    print("\n示例:")
    print("  add_exp \"网络慢\" \"改用 ModelScope\" --highlight")
    print("  add_goal \"学习 Python\" \"工作需要\" \"提升技能\" \"每天学 1 小时\"")
    print("  search ChromaDB")
    print("  list 经验教训")
