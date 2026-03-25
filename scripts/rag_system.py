#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBM项目 - RAG检索增强生成系统
版本: 1.0 (HBM Skill 适配版)
创建时间: 2026-03-25
描述: 从五大记忆库检索信息，增强AI回答质量
适配说明: 支持 HBM Skill 环境变量配置
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import time

# ==================== 配置区域 ====================

# 从环境变量读取 HBM 根目录
def get_hbm_root():
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
HBM_ROOT = get_hbm_root()
WORKSPACE_PATH = HBM_ROOT
CONFIG_PATH = HBM_ROOT / "config" / "hbm_config.json"
MEMORY_DB_PATH = HBM_ROOT / "memory" / "语义搜索_db"
MODEL_PATH = HBM_ROOT / "models" / "all-MiniLM-L6-v2" / "sentence-transformers" / "all-MiniLM-L6-v2"

print(f"🔧 RAG 系统路径配置:")
print(f"  • HBM_ROOT: {HBM_ROOT}")
print(f"  • 配置文件: {CONFIG_PATH}")
print(f"  • 向量库: {MEMORY_DB_PATH}")

# 五大记忆库路径
MEMORY_PATHS = {
    "目标记忆库": HBM_ROOT / "memory" / "目标记忆库" / "GOALS.md",
    "会话记忆库": HBM_ROOT / "memory" / "会话记忆库",
    "版本记忆库": HBM_ROOT / "memory" / "版本记忆库" / "CHANGELOG.md",
    "经验记忆库": HBM_ROOT / "memory" / "经验记忆库" / "TIPS.md",
    "情感记忆库": HBM_ROOT / "memory" / "情感记忆库" / "DAILY_EMOTIONS.md"
}

# ==================== 配置管理 ====================

class ConfigManager:
    """RAG配置管理器"""
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            # 创建默认配置
            default_config = {
                "rag_config": {
                    "开关控制": {
                        "enable_limit_and_dedupe": False,
                        "enable_cache": False,
                        "enable_log_compression": True
                    },
                    "检索参数": {
                        "vector_search_enabled": True,
                        "keyword_search_enabled": True,
                        "max_results": 5,
                        "max_tokens": 1000
                    }
                }
            }
            self.save_config(default_config)
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config
            
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def get(self, key_path, default=None):
        """获取配置值，支持点路径"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def is_enabled(self, switch_name):
        """检查开关是否启用"""
        return self.get(f"rag_config.开关控制.{switch_name}", False)

# ==================== 向量检索器 ====================

class VectorRetriever:
    """基于ChromaDB的向量检索器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.client = None
        self.collections = {}
        self.embedding_fn = None
        self._init_vector_db()
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        try:
            # 创建ChromaDB客户端
            self.client = chromadb.PersistentClient(
                path=str(MEMORY_DB_PATH),
                settings=chromadb.config.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 获取5个记忆集合
            collection_names = {
                "对话记录": "conversations_local",
                "系统版本": "system_changelog_local", 
                "经验教训": "experiences_local",
                "待办目标": "goals_local",
                "想法灵感": "ideas_local"
            }
            
            for cn_name, coll_name in collection_names.items():
                try:
                    self.collections[cn_name] = self.client.get_collection(coll_name)
                except:
                    # 集合不存在
                    self.collections[cn_name] = None
            
            # 初始化向量化器
            self.embedding_fn = SentenceTransformer(MODEL_PATH, trust_remote_code=True)
            
            print(f"✅ 向量检索器初始化完成，已连接集合: {list(self.collections.keys())}")
            
        except Exception as e:
            print(f"⚠️ 向量检索器初始化失败: {e}")
            self.client = None
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict]:
        """语义搜索"""
        if not self.client or not self.config.get("rag_config.检索参数.vector_search_enabled", True):
            return []
        
        results = []
        
        for coll_name, collection in self.collections.items():
            if collection is None:
                continue
                
            try:
                # 获取查询向量
                query_vector = self.embedding_fn.encode([query]).tolist()
                
                # 执行搜索
                search_results = collection.query(
                    query_embeddings=query_vector,
                    n_results=min(limit, 10),
                    include=["documents", "metadatas", "distances"]
                )
                
                # 处理结果
                if search_results and search_results['documents']:
                    for i, doc in enumerate(search_results['documents'][0]):
                        metadata = search_results['metadatas'][0][i] if search_results['metadatas'] else {}
                        distance = search_results['distances'][0][i] if search_results['distances'] else 1.0
                        
                        # 距离转换为相似度分数 (0-1)
                        similarity = 1.0 - min(distance, 1.0)
                        
                        results.append({
                            'content': doc,
                            'metadata': metadata,
                            'similarity': similarity,
                            'source': coll_name,
                            'type': 'vector'
                        })
                        
            except Exception as e:
                print(f"⚠️ 集合 {coll_name} 搜索失败: {e}")
                continue
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:limit]

# ==================== 关键词检索器 ====================

class KeywordRetriever:
    """基于关键词的Markdown文件检索器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """关键词搜索"""
        if not self.config.get("rag_config.检索参数.keyword_search_enabled", True):
            return []
        
        # 提取关键词
        keywords = self._extract_keywords(query)
        if not keywords:
            return []
        
        results = []
        
        # 搜索每个记忆库文件
        for mem_name, mem_path in MEMORY_PATHS.items():
            try:
                if mem_name == "会话记忆库":
                    # 会话记忆库是目录，需要搜索所有文件
                    file_results = self._search_session_files(mem_path, keywords, limit)
                    results.extend(file_results)
                else:
                    # 单个文件
                    file_results = self._search_single_file(mem_path, keywords, mem_name)
                    results.extend(file_results)
                    
            except Exception as e:
                print(f"⚠️ 记忆库 {mem_name} 搜索失败: {e}")
                continue
        
        # 按匹配度排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词"""
        # 简单实现：去除停用词，保留名词性词汇
        stop_words = {"的", "了", "和", "是", "在", "有", "我", "你", "他", "她", "它", "这", "那"}
        
        # 中文分词简单实现（按字符分割，实际应该用jieba等）
        words = re.findall(r'[\u4e00-\u9fff\w]+', query)
        
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        
        return keywords
    
    def _search_single_file(self, file_path: Path, keywords: List[str], source: str) -> List[Dict]:
        """搜索单个文件"""
        if not file_path.exists():
            return []
        
        results = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按行分割
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            if not line.strip():
                continue
            
            # 计算关键词匹配度
            score = 0
            matched_keywords = []
            
            for kw in keywords:
                if kw in line:
                    score += 1
                    matched_keywords.append(kw)
            
            if score > 0:
                # 获取上下文（前后各1行）
                start_line = max(0, line_num - 1)
                end_line = min(len(lines), line_num + 2)
                context = '\n'.join(lines[start_line:end_line])
                
                results.append({
                    'content': context,
                    'metadata': {
                        'line_number': line_num,
                        'matched_keywords': matched_keywords,
                        'file': file_path.name
                    },
                    'score': score / len(keywords),  # 归一化分数
                    'source': source,
                    'type': 'keyword'
                })
        
        return results
    
    def _search_session_files(self, dir_path: Path, keywords: List[str], limit: int) -> List[Dict]:
        """搜索会话记忆库目录"""
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        results = []
        
        # 获取最近7天的会话文件
        session_files = list(dir_path.glob("*.md"))
        session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        recent_files = session_files[:7]  # 最近7个文件
        
        for file_path in recent_files:
            file_results = self._search_single_file(file_path, keywords, f"会话记忆库/{file_path.name}")
            results.extend(file_results)
        
        return results

# ==================== 结果处理器 ====================

class ResultProcessor:
    """检索结果处理器（Token限制和去重）"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        
    def process(self, results: List[Dict], query: str = "") -> List[Dict]:
        """处理检索结果"""
        if not results:
            return []
        
        # 检查开关状态
        if not self.config.is_enabled("enable_limit_and_dedupe"):
            # 开关关闭，直接返回原始结果
            return results
        
        # 去重
        deduped = self._deduplicate(results)
        
        # Token限制
        limited = self._limit_by_tokens(deduped)
        
        return limited
    
    def _deduplicate(self, results: List[Dict], threshold: float = 0.8) -> List[Dict]:
        """基于内容相似度的去重（简化版）"""
        unique_results = []
        seen_contents = set()
        
        for result in results:
            content = result['content']
            
            # 简单去重：基于内容哈希
            content_hash = hash(content[:200])  # 取前200字符的哈希
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _limit_by_tokens(self, results: List[Dict], max_tokens: int = 1000) -> List[Dict]:
        """按Token数量限制结果"""
        max_tokens = self.config.get("rag_config.检索参数.max_tokens", 1000)
        
        total_tokens = 0
        final_results = []
        
        for result in results:
            # 简单Token估算：中文字符算1个token，英文字母算0.25个
            content = result['content']
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
            english_chars = len(re.findall(r'[a-zA-Z]', content))
            tokens = chinese_chars + english_chars * 0.25
            
            if total_tokens + tokens <= max_tokens:
                final_results.append(result)
                total_tokens += tokens
            else:
                # 尝试截断内容
                if total_tokens == 0:
                    # 如果第一个结果就超了，至少保留一部分
                    ratio = max_tokens / tokens
                    keep_chars = int(len(content) * ratio * 0.8)  # 保留80%的比例
                    if keep_chars > 50:
                        result['content'] = content[:keep_chars] + "..."
                        final_results.append(result)
                break
        
        return final_results

# ==================== 缓存管理器 ====================

class CacheManager:
    """内存缓存管理器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.cache = {}
        self.ttl = self.config.get("rag_config.缓存参数.ttl_seconds", 3600)
        self.max_size = self.config.get("rag_config.缓存参数.max_cache_size", 100)
    
    def get(self, key: str) -> Optional[Any]:
        """从缓存获取"""
        if not self.config.is_enabled("enable_cache"):
            return None
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                # 过期删除
                del self.cache[key]
        
        return None
    
    def set(self, key: str, data: Any):
        """设置缓存"""
        if not self.config.is_enabled("enable_cache"):
            return
        
        # 清理过期缓存
        self._cleanup()
        
        # 限制缓存大小
        if len(self.cache) >= self.max_size:
            # 删除最旧的缓存
            oldest_key = min(self.cache.items(), key=lambda x: x[1]['timestamp'])[0]
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _cleanup(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry['timestamp'] > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]

# ==================== 上下文组装器 ====================

class ContextAssembler:
    """上下文组装器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def assemble(self, results: List[Dict], query: str) -> str:
        """组装检索结果为上下文"""
        if not results:
            return ""
        
        context_parts = []
        
        # 添加上下文头
        context_parts.append("# 📚 相关记忆检索结果")
        context_parts.append(f"**查询**: {query}")
        context_parts.append(f"**检索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        context_parts.append("---")
        
        # 添加每个检索结果
        for i, result in enumerate(results, 1):
            source = result.get('source', '未知')
            result_type = result.get('type', '未知')
            score = result.get('similarity', result.get('score', 0))
            
            context_parts.append(f"## 结果 {i}: [{source}] ({result_type})")
            context_parts.append(f"*相关度: {score:.2f}*")
            context_parts.append("")
            context_parts.append(result['content'])
            context_parts.append("")
        
        # 添加使用说明
        context_parts.append("---")
        context_parts.append("**使用说明**: 以上是从你的记忆库中检索到的相关信息。请参考这些信息来回答用户的问题，保持回答的准确性和相关性。")
        
        return '\n'.join(context_parts)

# ==================== 主RAG系统 ====================

class RAGSystem:
    """主RAG系统"""
    
    def __init__(self):
        self.config = ConfigManager(CONFIG_PATH)
        self.vector_retriever = VectorRetriever(self.config)
        self.keyword_retriever = KeywordRetriever(self.config)
        self.result_processor = ResultProcessor(self.config)
        self.cache_manager = CacheManager(self.config)
        self.context_assembler = ContextAssembler(self.config)
        
        print("✅ RAG系统初始化完成")
        print(f"   配置状态: 限制去重开关={self.config.is_enabled('enable_limit_and_dedupe')}, "
              f"缓存开关={self.config.is_enabled('enable_cache')}")
    
    def retrieve(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        检索相关记忆
        
        参数:
            query: 用户查询
            use_cache: 是否使用缓存
            
        返回:
            包含检索结果和上下文的字典
        """
        # 检查缓存
        cache_key = f"rag:{hash(query)}"
        if use_cache:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                print(f"📦 从缓存获取检索结果 (查询: {query[:30]}...)")
                return cached_result
        
        # 向量检索
        print(f"🔍 开始向量检索: {query[:50]}...")
        vector_results = self.vector_retriever.semantic_search(query)
        
        # 关键词检索
        print(f"🔍 开始关键词检索: {query[:50]}...")
        keyword_results = self.keyword_retriever.search(query)
        
        # 合并结果
        all_results = vector_results + keyword_results
        
        # 处理结果（应用限制和去重）
        processed_results = self.result_processor.process(all_results, query)
        
        # 组装上下文
        context = self.context_assembler.assemble(processed_results, query)
        
        # 构建返回结果
        result = {
            'query': query,
            'vector_results_count': len(vector_results),
            'keyword_results_count': len(keyword_results),
            'processed_results_count': len(processed_results),
            'context': context,
            'results': processed_results,
            'timestamp': datetime.now().isoformat()
        }
        
        # 存入缓存
        self.cache_manager.set(cache_key, result)
        
        return result
    
    def get_context_for_query(self, query: str) -> str:
        """
        获取查询的上下文（简化接口）
        
        参数:
            query: 用户查询
            
        返回:
            组装好的上下文字符串
        """
        result = self.retrieve(query)
        return result['context']

# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 测试RAG系统
    print("🧪 测试RAG系统...")
    
    rag = RAGSystem()
    
    # 测试查询
    test_queries = [
        "OpenClaw的记忆系统怎么用？",
        "我之前遇到过什么技术问题？",
        "最近有什么待办目标？"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"测试查询: {query}")
        print(f"{'='*60}")
        
        result = rag.retrieve(query, use_cache=False)
        
        print(f"✅ 检索完成")
        print(f"   向量结果: {result['vector_results_count']} 条")
        print(f"   关键词结果: {result['keyword_results_count']} 条")
        print(f"   处理后结果: {result['processed_results_count']} 条")
        
        # 显示部分上下文
        context_preview = result['context'][:500] + "..." if len(result['context']) > 500 else result['context']
        print(f"\n📄 上下文预览:\n{context_preview}")
    
    print(f"\n{'='*60}")
    print("✅ RAG系统测试完成")
    print(f"{'='*60}")