#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 系统主入口
==============
用法:
  python3 scripts/rag_system.py search <查询词>                  # 检索记忆
  python3 scripts/rag_system.py config                          # 查看当前配置
  python3 scripts/rag_system.py config toggle <开关名>           # 切换开关
  python3 scripts/rag_system.py cache stats                     # 查看缓存统计
  python3 scripts/rag_system.py cache clear                     # 清空缓存
"""

import sys
import json
from pathlib import Path

# 将 RAG 包加入路径
RAG_DIR = Path(__file__).parent.parent / "memory/RAG"
sys.path.insert(0, str(RAG_DIR))

from retriever import HBMRetriever
from context_assembler import assemble_context, format_for_bootstrap
from processor import process_results, deduplicate_by_similarity, limit_by_tokens, estimate_tokens
from cache import get_cache
from config_manager import load_config, save_config
from log_compressor import run_compression, run_full_compression


def cmd_search(args):
    """检索命令"""
    query = " ".join(args)
    if not query:
        print("❌ 请输入查询词")
        print("   用法: python3 scripts/rag_system.py search <关键词>")
        return
    
    limit = 5
    
    # 检查缓存
    cache = get_cache()
    cached = cache.get(query, limit)
    
    if cached:
        print("📦 [缓存命中]")
        results = cached
    else:
        print(f"🔍 正在检索: \"{query}\"")
        retriever = HBMRetriever()
        results = retriever.retrieve(query, limit)
        cache.set(query, limit, results)
    
    if not results:
        print("📭 未找到相关记忆片段")
        return
    
    # 输出完整上下文
    context = assemble_context(results, query)
    print(context)
    
    # 输出 JSON 格式详情（用于 debug）
    print("\n--- JSON 详情 ---")
    output = []
    for r in results:
        output.append({
            "source": r.get("source"),
            "score": round(r.get("score", 0), 3),
            "method": r.get("method", " / ".join(r.get("methods", ["unknown"]))),
            "preview": r.get("content", "")[:150]
        })
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_config(args):
    """配置管理命令"""
    if not args or args[0] == "show":
        config = load_config()
        print(json.dumps(config, ensure_ascii=False, indent=2))
    
    elif args[0] == "toggle":
        if len(args) < 2:
            print("❌ 请指定要切换的开关名")
            print("   可用开关: enable_limit_and_dedupe, enable_cache, enable_log_compression")
            return
        
        switch_map = {
            "dedupe": "enable_limit_and_dedupe",
            "cache": "enable_cache",
            "compress": "enable_log_compression"
        }
        switch_name = switch_map.get(args[1], args[1])
        
        config = load_config()
        switches = config.setdefault("rag_config", {}).setdefault("开关控制", {})
        
        if switch_name not in switches:
            print(f"❌ 未知开关: {switch_name}")
            return
        
        switches[switch_name] = not switches[switch_name]
        save_config(config)
        
        status = "✅ 开启" if switches[switch_name] else "⛔ 关闭"
        print(f"{status}: {switch_name}")
    
    else:
        print("❌ 未知配置命令")
        print("   用法: python3 scripts/rag_system.py config [show|toggle <开关名>]")


def cmd_compress(args):
    """日志压缩命令"""
    dry_run = "--dry-run" in args or "-n" in args
    full = "--full" in args or "-f" in args
    
    if full:
        result = run_full_compression(dry_run)
        print(f"\n处理: {result.get('processed', 0)} 个, 跳过: {result.get('skipped', 0)} 个")
    else:
        count = run_compression(dry_run)
        print(f"\n处理: {count} 个文件")


def cmd_cache(args):
    """缓存管理命令"""
    cache = get_cache()
    
    if not args or args[0] == "stats":
        stats = cache.stats()
        print(f"缓存条目: {stats['total_entries']}")
        print(f"有效条目: {stats['active_entries']}")
        print(f"累计命中: {stats['total_hits']}")
    
    elif args[0] == "clear":
        cache.clear()
        print("✅ 缓存已清空")
    
    else:
        print("❌ 未知缓存命令")
        print("   用法: python3 scripts/rag_system.py cache [stats|clear]")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "search": cmd_search,
        "config": cmd_config,
        "cache": cmd_cache,
        "compress": cmd_compress,
    }
    
    handler = commands.get(cmd)
    if handler:
        handler(args)
    else:
        print(f"❌ 未知命令: {cmd}")
        print(f"   可用命令: {', '.join(commands.keys())}")


if __name__ == "__main__":
    main()
