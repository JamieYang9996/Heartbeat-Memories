#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统连接器 - ChromaDB 客户端和 Embedding 模型共享实例
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
import chromadb.config

WORKSPACE = Path(os.environ.get("HBM_ROOT", os.path.expanduser("~/.openclaw/skills/hbm")))
MEMORY_DB_PATH = WORKSPACE / "memory/语义搜索_db"
MODEL_PATH = str(Path.home() / ".openclaw/workspace/models/all-MiniLM-L6-v2/sentence-transformers/all-MiniLM-L6-v2")

# 备用模型路径（兼容不同安装方式）
ALT_MODEL_PATHS = [
    MODEL_PATH,
    str(WORKSPACE / "models/all-MiniLM-L6-v2/sentence-transformers/all-MiniLM-L6-v2"),
    str(Path.home() / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/*"),
]


class EmbeddingFunction:
    """自定义 Embedding 函数 - 使用本地已下载模型"""
    
    def __init__(self):
        self.model = self._load_model()
    
    def _load_model(self):
        for path in [MODEL_PATH, str(WORKSPACE / "models/all-MiniLM-L6-v2/sentence-transformers/all-MiniLM-L6-v2")]:
            p = Path(path)
            if p.exists():
                return SentenceTransformer(str(p), trust_remote_code=True)
        # fallback: let sentence-transformers download
        return SentenceTransformer("all-MiniLM-L6-v2", trust_remote_code=True)
    
    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input, show_progress_bar=False)
        return embeddings.tolist()


# 全局单例
_client = None
_embedding_fn = None


def get_chroma_client():
    """获取 ChromaDB 客户端（单例）"""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=str(MEMORY_DB_PATH),
            settings=chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    return _client


def get_embedding_fn():
    """获取 Embedding 函数（单例）"""
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = EmbeddingFunction()
    return _embedding_fn
