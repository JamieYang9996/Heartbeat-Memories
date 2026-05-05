#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 日志压缩器 - 按自然月自动压缩日志
=====================================
规则:
  - 每月 1 号压缩上上个月的日志 (compress_months_ago=2)
  - 保留最近一个月的详细日志 (months_to_keep_detailed=1)
  - 精简版保留: 时间戳、重要事件、错误信息、关键指标
  - 精简版删除: 重复信息、调试信息、详细堆栈跟踪（除非是错误）
  - 精简比例目标: 原始体积的 30% (simplification_ratio=0.3)
"""

import re
import os
import gzip
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from config_manager import load_config


# 需要保留的关键行模式
KEEP_PATTERNS = [
    r'^\[?20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}',  # 时间戳开头: [2026-03-25 10:39] 或 2026-03-25 10:39
    r'(ERROR|WARN|WARNING|CRITICAL|FATAL|FATAL ERROR)',  # 错误/警告级别
    r'(错误|异常|失败|报错|故障|崩溃)',  # 中文错误
    r'(成功|完成|开始|结束)',  # 关键事件标记
    r'relevance.*[0-9]\.[0-9]',  # 相关性分数
    r'took\s+\d+\.?\d*\s*(ms|s|秒)',  # 执行耗时
    r'query.*retriev',  # 查询检索记录
    r'\d+\s*results?\s*(found|returned|检索)',  # 结果数
    r'hits?:\s*\d+',  # 缓存命中
    r'(cache|缓存).*(hit|miss|命中|未命中)',  # 缓存状态
    r'(token|Token|tokens).*(\d+)',  # Token 使用
    r'(model|模型).*(load|加载|init|初始化)',  # 模型加载
]

# 需要压缩的行模式（可移除的详细信息）
REMOVE_PATTERNS = [
    r'^\s+at\s+',  # Java/C# 堆栈的 "at ..."
    r'^\s+File\s+"',  # Python 堆栈文件引用
    r'Traceback \(most recent call last\)',  # Python 堆栈追踪头
    r'^The above exception',  # Python 链式异常
    r'^\s+\.{3}',  # 连续点号
    r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}\.\d{3}',  # 毫秒级时间戳（保留到秒即可）
    r'debug:\s',  # 调试信息
    r'DEBUG\s',  # DEBUG 级别日志
]


def _should_keep_line(line: str) -> bool:
    """判断一行日志是否应保留"""
    for pattern in KEEP_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    # 如果包含任何 REMOVE 模式，移除
    for pattern in REMOVE_PATTERNS:
        if re.search(pattern, line):
            return False
    
    # 空行保留（作为段落分隔）
    if not line.strip():
        return True
    
    # 短行（无信息量）移除
    if len(line.strip()) < 5 and not line.strip().startswith('['):
        return False
    
    return True


def _extract_key_points(content: str) -> str:
    """从详细日志中提取关键点"""
    lines = content.split('\n')
    kept_lines = []
    error_context_lines = 3  # 错误行周围保留的上下文行数
    
    for i, line in enumerate(lines):
        if _should_keep_line(line):
            kept_lines.append((i, line))
        # 检查是否需要保留错误上下文
        elif i > 0 and i < len(lines) - 1:
            # 如果相邻行包含错误关键词，保留
            for offset in [-1, 1]:
                idx = i + offset
                if 0 <= idx < len(lines):
                    if re.search(r'(ERROR|WARN|错误|异常|失败)', lines[idx], re.IGNORECASE):
                        kept_lines.append((i, line))
                        break
    
    # 重建内容，合并相邻行
    if not kept_lines:
        return "[精简版] (无关键信息保留)"
    
    result_lines = []
    last_idx = -10
    
    for idx, line in kept_lines:
        if idx - last_idx > 5:  # 间隔超过5行，添加省略标记
            if result_lines:
                result_lines.append(f"... [省略 {idx - last_idx - 1} 行]")
        elif idx - last_idx > 1:
            result_lines.append(f"... 省略 {idx - last_idx - 1} 行 ...")
        result_lines.append(line)
        last_idx = idx
    
    return '\n'.join(result_lines)


def compress_log_file(log_path: Path, dry_run: bool = False) -> Optional[Path]:
    """压缩单个日志文件"""
    if not log_path.exists() or log_path.suffix == '.gz':
        return None
    
    try:
        content = log_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None
    
    if not content.strip():
        return None
    
    # 提取关键信息
    simplified = _extract_key_points(content)
    
    # 检查压缩比例
    original_size = len(content.encode('utf-8'))
    simplified_size = len(simplified.encode('utf-8'))
    
    config = load_config()
    target_ratio = config.get("rag_config", {}).get("日志参数", {}).get("simplification_ratio", 0.3)
    
    # 如果简化版体积小于原始体积的 target_ratio*2，视为有效压缩
    # 否则保留完整版本（可能已经是关键内容了）
    if simplified_size > original_size * target_ratio * 2:
        simplified = f"[日志精简]\n原始大小: {original_size} 字节\n[以下为完整关键内容]\n" + simplified
    
    # 构建精简版文件名
    simplified_path = log_path.with_name(f"{log_path.stem}_simplified{log_path.suffix}")
    
    if dry_run:
        print(f"  [试运行] {log_path.name}")
        print(f"    原始: {original_size:,} bytes")
        print(f"    精简: {simplified_size:,} bytes")
        print(f"    压缩比: {simplified_size/original_size:.1%}" if original_size > 0 else "")
        return None
    
    # 写精简版
    simplified_path.write_text(simplified, encoding='utf-8')
    
    # 删除原始详细日志
    log_path.unlink()
    
    return simplified_path


def run_compression(dry_run: bool = False) -> int:
    """
    执行日志压缩 - 自动识别需要压缩的月份
    
    Returns:
        处理的文件数
    """
    config = load_config()
    log_config = config.get("rag_config", {}).get("日志参数", {})
    log_dir = Path(log_config.get("log_dir", os.path.join(os.environ.get("HBM_ROOT", os.path.expanduser("~/.openclaw/skills/hbm")), "memory/logs")))
    compress_months_ago = log_config.get("compress_months_ago", 2)
    
    if not log_dir.exists():
        if dry_run:
            print(f"  日志目录不存在: {log_dir}")
        return 0
    
    now = datetime.now()
    target_month = now.month - compress_months_ago
    target_year = now.year
    while target_month < 1:
        target_month += 12
        target_year -= 1
    
    # 查找目标月份的日志文件
    pattern = f"rag_{target_year:04d}-{target_month:02d}*.log"
    log_files = list(log_dir.glob(pattern))
    
    # 排除已经精简过的文件
    log_files = [f for f in log_files if '_simplified' not in f.name and f.suffix != '.gz']
    
    if not log_files:
        if dry_run:
            print(f"  未找到需要压缩的日志文件 (匹配: {pattern})")
        return 0
    
    count = 0
    for log_file in sorted(log_files):
        result = compress_log_file(log_file, dry_run)
        if result:
            count += 1
            original_size = log_file.stat().st_size if not dry_run else 0
            simplified_size = result.stat().st_size
            ratio = simplified_size / original_size if original_size > 0 else 0
            print(f"  ✓ {log_file.name} → {result.name} (压缩比: {ratio:.1%})")
    
    return count


def run_full_compression(dry_run: bool = False) -> dict:
    """
    完整日志压缩（考虑所有可压缩的月份）
    
    Returns:
        统计信息
    """
    config = load_config()
    log_config = config.get("rag_config", {}).get("日志参数", {})
    log_dir = Path(log_config.get("log_dir", os.path.join(os.environ.get("HBM_ROOT", os.path.expanduser("~/.openclaw/skills/hbm")), "memory/logs")))
    months_to_keep = log_config.get("months_to_keep_detailed", 1)
    
    if not log_dir.exists():
        return {"error": f"日志目录不存在: {log_dir}"}
    
    now = datetime.now()
    processed = 0
    skipped = 0
    
    # 查找所有 rag_YYYY-MM*.log 文件（非精简版、非 gz）
    all_logs = sorted([
        f for f in log_dir.glob("rag_*.log")
        if '_simplified' not in f.name
    ])
    
    summary = []
    
    for log_file in all_logs:
        # 从文件名提取月份
        match = re.search(r'rag_(\d{4})-(\d{2})', log_file.name)
        if not match:
            continue
        
        file_year = int(match.group(1))
        file_month = int(match.group(2))
        
        # 计算月份差
        month_diff = (now.year - file_year) * 12 + (now.month - file_month)
        
        if not dry_run:
            print(f"  ⏹  {log_file.name} (保留中)", end="")
        
        if month_diff >= months_to_keep:
            # 超过保留期，需要压缩
            orig_size = log_file.stat().st_size if log_file.exists() else 0
            result = compress_log_file(log_file, dry_run)
            if result:
                processed += 1
                simp_size = result.stat().st_size
                ratio = simp_size / orig_size if orig_size > 0 else 0
                summary.append(f"  ✓ {log_file.name} → {result.name} ({ratio:.1%})")
            else:
                skipped += 1
        else:
            skipped += 1
    
    if not dry_run and summary:
        print("\n压缩结果:")
        for line in summary:
            print(line)
    
    return {
        "processed": processed,
        "skipped": skipped,
        "log_dir": str(log_dir),
        "months_to_keep": months_to_keep
    }


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    full = "--full" in sys.argv or "-f" in sys.argv
    
    print(f"{'[试运行] ' if dry_run else ''}RAG 日志压缩 {'(完整模式)' if full else ''}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    if full:
        result = run_full_compression(dry_run)
        print(f"\n处理: {result['processed']} 个, 跳过: {result['skipped']} 个")
    else:
        count = run_compression(dry_run)
        print(f"\n处理: {count} 个文件")
