#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG日志压缩器 (HBM Skill 适配版)
按自然月压缩日志：进入新月份后，自动将上上个月的详细日志压缩为精简版
规则：每月1号压缩上上个月日志，保留最近一个月详细版
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime, timedelta
import shutil

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
LOG_DIR = HBM_ROOT / "logs"
CONFIG_PATH = HBM_ROOT / "config" / "hbm_config.json"

print(f"🔧 日志压缩器路径配置:")
print(f"  • HBM_ROOT: {HBM_ROOT}")
print(f"  • 日志目录: {LOG_DIR}")
print(f"  • 配置文件: {CONFIG_PATH}")

# ==================== 日志压缩器 ====================

class LogCompressor:
    """RAG日志按月压缩器"""
    
    def __init__(self, log_dir, config_path):
        self.log_dir = Path(log_dir)
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            return {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    
    def compress_previous_month(self, force_month=None):
        """
        压缩上上个月的RAG系统日志（保留最近一个月的详细版）
        例如：8月1日压缩6月份日志，保留7月份详细版
        
        参数:
            force_month: 强制压缩指定月份（格式: YYYY-MM），为None时自动检测
        """
        if force_month:
            target_month = force_month
        else:
            # 自动检测：当前月份的前两个月（压缩上上个月，保留最近一个月详细版）
            current_date = datetime.now()
            
            # 计算上上个月的最后一天
            first_day_of_current_month = current_date.replace(day=1)
            
            # 上个月的最后一天
            last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
            
            # 上上个月的最后一天
            first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
            last_day_of_previous_previous_month = first_day_of_previous_month - timedelta(days=1)
            
            target_month = last_day_of_previous_previous_month.strftime("%Y-%m")
        
        print(f"📊 开始压缩 {target_month} 的RAG日志（保留最近一个月详细版）...")
        
        # 查找目标月份的所有日志文件
        log_files = list(self.log_dir.glob(f"*{target_month}*.log"))
        detailed_files = [f for f in log_files if not f.name.endswith("_simplified.log")]
        
        if not detailed_files:
            print(f"📭 未找到 {target_month} 的详细日志文件")
            return
        
        compressed_count = 0
        
        for log_file in detailed_files:
            try:
                # 检查是否已有精简版
                simplified_path = log_file.with_name(f"{log_file.stem}_simplified.log")
                if simplified_path.exists():
                    print(f"⏭️  跳过 {log_file.name}，已存在精简版")
                    continue
                
                # 读取日志内容
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 压缩日志（提取关键信息）
                simplified_content = self.simplify_log(content, log_file.name)
                
                # 保存精简版
                with open(simplified_path, 'w', encoding='utf-8') as f:
                    f.write(simplified_content)
                
                # 删除详细版（根据配置决定）
                retain_detailed = self.config.get("rag_config", {}).get("日志参数", {}).get("retain_detailed_days", 30)
                
                if retain_detailed <= 0:
                    # 立即删除详细版
                    log_file.unlink()
                    print(f"✅ 已压缩并删除: {log_file.name} → {simplified_path.name}")
                else:
                    # 保留详细版（用户要求全部留存备份）
                    print(f"✅ 已创建精简版: {log_file.name} → {simplified_path.name}（保留详细版）")
                
                compressed_count += 1
                
            except Exception as e:
                print(f"❌ 压缩文件 {log_file.name} 失败: {e}")
                continue
        
        print(f"📦 压缩完成: 共处理 {compressed_count}/{len(detailed_files)} 个文件")
    
    def simplify_log(self, content: str, filename: str) -> str:
        """
        简化日志内容，提取关键信息
        
        参数:
            content: 原始日志内容
            filename: 日志文件名
            
        返回:
            简化后的日志内容
        """
        lines = content.split('\n')
        simplified_lines = []
        
        # 添加文件头信息
        simplified_lines.append(f"# 📦 精简版日志: {filename}")
        simplified_lines.append(f"# 压缩时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        simplified_lines.append(f"# 原始大小: {len(content)} 字符")
        simplified_lines.append("")
        
        # 提取关键信息
        key_sections = []
        current_section = []
        
        for line in lines:
            # 识别关键行（时间戳、错误、重要事件）
            if self.is_key_line(line):
                if current_section:
                    key_sections.append('\n'.join(current_section))
                    current_section = []
                key_sections.append(line)
            elif line.strip() and (line.startswith('✅') or line.startswith('❌') or line.startswith('⚠️')):
                # 重要标志
                key_sections.append(line)
            elif re.search(r'(error|fail|exception|warning|critical)', line.lower()):
                # 错误信息
                key_sections.append(line)
            elif re.match(r'^\d{4}-\d{2}-\d{2}', line[:10]):
                # 时间戳行
                key_sections.append(line)
        
        # 添加最后一个部分
        if current_section:
            key_sections.append('\n'.join(current_section))
        
        # 限制提取的行数（避免过大）
        max_lines = 100
        if len(key_sections) > max_lines:
            # 保留开始和结束的部分
            keep_start = int(max_lines * 0.6)
            keep_end = max_lines - keep_start
            
            key_sections = (
                key_sections[:keep_start] + 
                ["\n[... 中间部分已省略 ...]\n"] + 
                key_sections[-keep_end:]
            )
        
        simplified_lines.extend(key_sections)
        
        # 添加统计信息
        simplified_lines.append("")
        simplified_lines.append("---")
        simplified_lines.append(f"**统计信息**: 原始{len(lines)}行 → 精简{len(key_sections)}行 (压缩率: {len(key_sections)/max(len(lines),1):.1%})")
        simplified_lines.append(f"**关键事件**: 提取了重要时间戳、错误信息和状态变更")
        
        return '\n'.join(simplified_lines)
    
    def is_key_line(self, line: str) -> bool:
        """判断是否为关键行"""
        line = line.strip()
        
        # 空行
        if not line:
            return False
        
        # 章节标题
        if line.startswith('# ') or line.startswith('## ') or line.startswith('### '):
            return True
        
        # 重要分隔符
        if line.startswith('---') or line.startswith('===') or line.startswith('***'):
            return True
        
        # JSON格式的行（可能包含重要数据）
        if line.strip().startswith('{') and line.strip().endswith('}'):
            return True
        
        # 包含重要关键词
        keywords = ['检索', '查询', '结果', '错误', '失败', '异常', '警告', '完成', '开始', '结束']
        for kw in keywords:
            if kw in line:
                return True
        
        return False
    
    def check_and_compress(self):
        """检查并执行压缩（如果到了压缩时间）"""
        # 检查配置是否启用
        if not self.config.get("rag_config", {}).get("开关控制", {}).get("enable_log_compression", True):
            print("📭 日志压缩功能已禁用")
            return
        
        # 获取压缩日期配置
        compression_day = self.config.get("rag_config", {}).get("日志参数", {}).get("compression_day_of_month", 1)
        
        current_date = datetime.now()
        
        # 检查是否到了压缩日
        if current_date.day != compression_day:
            print(f"📅 未到压缩日（配置: 每月{compression_day}号，今天: {current_date.day}号）")
            return
        
        # 检查是否已经压缩过本月
        marker_file = self.log_dir / f"compression_marker_{current_date.strftime('%Y-%m')}.txt"
        if marker_file.exists():
            print(f"⏭️  本月日志已压缩过（标记文件: {marker_file.name}）")
            return
        
        # 执行压缩
        print(f"🚀 开始执行月度日志压缩...")
        self.compress_previous_month()
        
        # 创建标记文件
        marker_file.write_text(f"压缩时间: {current_date.isoformat()}\n")
        print(f"📝 已创建压缩标记文件: {marker_file.name}")

# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("🧪 测试日志压缩器...")
    
    compressor = LogCompressor(LOG_DIR, CONFIG_PATH)
    
    # 检查并执行压缩
    compressor.check_and_compress()
    
    # 也可以手动指定月份进行压缩
    # compressor.compress_previous_month("2026-02")
    
    print("✅ 日志压缩器测试完成")