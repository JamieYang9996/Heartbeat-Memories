#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBM 系统初始化脚本
一键初始化 Humanized Brain Memory 系统
"""

import os
import sys
import json
import shutil
from pathlib import Path
import platform
import subprocess
import argparse

# ==================== 配置区域 ====================

class HBMInstaller:
    """HBM 系统安装器"""
    
    def __init__(self, hbm_root=None):
        """
        初始化安装器
        
        参数:
            hbm_root: HBM 根目录，如果为 None 则自动检测
        """
        self.system = platform.system()
        self.hbm_root = self.detect_hbm_root(hbm_root)
        self.config = {}
        
        print(f"🚀 HBM 初始化开始")
        print(f"📁 系统类型: {self.system}")
        print(f"📁 HBM 根目录: {self.hbm_root}")
    
    def detect_hbm_root(self, user_root):
        """检测 HBM 根目录"""
        if user_root:
            return Path(user_root).expanduser().resolve()
        
        # 自动检测 OpenClaw 技能目录
        possible_paths = [
            Path.home() / ".openclaw" / "skills" / "hbm",
            Path.home() / "AppData" / "Local" / "openclaw" / "skills" / "hbm",  # Windows
            Path.home() / "Library" / "Application Support" / "openclaw" / "skills" / "hbm",  # macOS
        ]
        
        for path in possible_paths:
            if path.exists():
                return path.resolve()
        
        # 如果都不存在，使用第一个路径
        return possible_paths[0].resolve()
    
    def create_directory_structure(self):
        """创建目录结构"""
        print(f"\n📂 创建目录结构...")
        
        directories = [
            self.hbm_root,
            self.hbm_root / "memory",
            self.hbm_root / "memory" / "目标记忆库",
            self.hbm_root / "memory" / "经验记忆库",
            self.hbm_root / "memory" / "情感记忆库",
            self.hbm_root / "memory" / "会话记忆库",
            self.hbm_root / "memory" / "版本记忆库",
            self.hbm_root / "memory" / "心跳回忆",
            self.hbm_root / "scripts",
            self.hbm_root / "config",
            self.hbm_root / "models",
            self.hbm_root / "logs",
            self.hbm_root / "docs",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory}")
        
        print(f"✅ 目录结构创建完成")
    
    def copy_template_files(self):
        """复制模板文件"""
        print(f"\n📄 复制模板文件...")
        
        # 获取当前脚本所在目录（模板文件应该在上一级的 memory 目录中）
        script_dir = Path(__file__).parent
        template_source = script_dir.parent / "memory"
        
        if not template_source.exists():
            print(f"⚠️  模板源目录不存在: {template_source}")
            print(f"⚠️  跳过模板复制，用户需要手动创建记忆库文件")
            return
        
        # 复制记忆库模板文件
        template_files = [
            ("目标记忆库/GOALS_template.md", "目标记忆库/GOALS.md"),
            ("经验记忆库/TIPS_template.md", "经验记忆库/TIPS.md"),
            ("情感记忆库/DAILY_EMOTIONS_template.md", "情感记忆库/DAILY_EMOTIONS.md"),
            ("版本记忆库/CHANGELOG_template.md", "版本记忆库/CHANGELOG.md"),
            ("心跳回忆/心跳回忆机制.md", "心跳回忆/心跳回忆机制.md"),
        ]
        
        for src_rel, dst_rel in template_files:
            src_path = template_source / src_rel
            dst_path = self.hbm_root / "memory" / dst_rel
            
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                print(f"  ✅ {dst_rel}")
            else:
                print(f"  ⚠️  模板文件不存在: {src_rel}")
        
        # 复制配置文件模板
        config_src = script_dir.parent / "config" / "hbm_config_template.json"
        config_dst = self.hbm_root / "config" / "hbm_config.json"
        
        if config_src.exists():
            # 读取模板并替换 ${HOME}
            with open(config_src, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换路径变量
            home_str = str(Path.home())
            content = content.replace("${HOME}", home_str)
            
            with open(config_dst, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ config/hbm_config.json (已替换路径变量)")
        else:
            print(f"  ⚠️  配置文件模板不存在")
        
        print(f"✅ 模板文件复制完成")
    
    def check_python_dependencies(self):
        """检查 Python 依赖"""
        print(f"\n🔧 检查 Python 依赖...")
        
        required_packages = [
            "chromadb>=0.4.22",
            "sentence-transformers>=2.2.2",
        ]
        
        # 根据系统选择 FAISS
        if self.system == "Darwin":  # macOS
            required_packages.append("faiss-cpu>=1.7.4")
        else:
            # Linux/Windows 通常也使用 CPU 版本
            required_packages.append("faiss-cpu>=1.7.4")
        
        print(f"📦 需要安装的包:")
        for pkg in required_packages:
            print(f"  • {pkg}")
        
        print(f"\n💡 安装建议:")
        print(f"  pip install {' '.join(required_packages)}")
        print(f"  或使用 conda: conda install -c conda-forge chromadb sentence-transformers")
        
        return required_packages
    
    def download_model_optional(self):
        """可选：下载向量模型"""
        print(f"\n🤖 向量模型设置...")
        
        model_name = "all-MiniLM-L6-v2"
        model_size_mb = 80
        
        print(f"📊 模型信息:")
        print(f"  • 名称: {model_name}")
        print(f"  • 大小: ~{model_size_mb}MB")
        print(f"  • 维度: 384")
        print(f"  • 用途: 文本向量化，支持语义搜索")
        
        print(f"\n💡 使用说明:")
        print(f"  1. 首次使用时会自动下载（需要网络）")
        print(f"  2. 下载后存储在: {self.hbm_root / 'models'}")
        print(f"  3. 国内用户建议使用 ModelScope 镜像:")
        print(f"     export HF_ENDPOINT=https://mirrors.tuna.tsinghua.edu.cn/hugging-face")
        
        return model_name
    
    def create_activation_script(self):
        """创建激活脚本（方便用户使用）"""
        print(f"\n⚡ 创建便捷脚本...")
        
        # 创建激活脚本（设置环境变量）
        activate_script = self.hbm_root / "activate_hbm.sh"
        
        script_content = f"""#!/bin/bash
# HBM 系统激活脚本
# 运行此脚本设置 HBM 环境变量

export HBM_ROOT="{self.hbm_root}"
export HBM_MEMORY_PATH="$HBM_ROOT/memory"
export HBM_CONFIG_PATH="$HBM_ROOT/config/hbm_config.json"
export PYTHONPATH="$HBM_ROOT/scripts:$PYTHONPATH"

echo "✅ HBM 环境变量已设置"
echo "📁 HBM_ROOT: $HBM_ROOT"
echo "📁 HBM_MEMORY_PATH: $HBM_MEMORY_PATH"
echo ""
echo "使用示例:"
echo "  python3 $HBM_ROOT/scripts/local_memory_system_v2.py --help"
echo "  python3 $HBM_ROOT/scripts/rag_system.py --test"
"""

        with open(activate_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置为可执行（Linux/macOS）
        if self.system != "Windows":
            os.chmod(activate_script, 0o755)
        
        print(f"  ✅ activate_hbm.sh (环境变量设置脚本)")
        
        # 创建 Windows 批处理文件
        if self.system == "Windows":
            bat_script = self.hbm_root / "activate_hbm.bat"
            bat_content = f"""@echo off
REM HBM 系统激活脚本 (Windows)
set HBM_ROOT={self.hbm_root}
set HBM_MEMORY_PATH=%HBM_ROOT%\\memory
set HBM_CONFIG_PATH=%HBM_ROOT%\\config\\hbm_config.json

echo ✅ HBM 环境变量已设置
echo 📁 HBM_ROOT: %HBM_ROOT%
echo 📁 HBM_MEMORY_PATH: %HBM_MEMORY_PATH%
echo.
echo 使用示例:
echo   python %HBM_ROOT%\\scripts\\local_memory_system_v2.py --help
"""
            with open(bat_script, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            print(f"  ✅ activate_hbm.bat (Windows 环境变量脚本)")
        
        print(f"✅ 便捷脚本创建完成")
    
    def generate_readme(self):
        """生成 README 文件"""
        print(f"\n📝 生成 README.md...")
        
        readme_path = self.hbm_root / "README.md"
        
        readme_content = f"""# HBM (Humanized Brain Memory)

**完全本地化的长期记忆系统**，让 OpenClaw 记住一切重要对话、目标、经验和情感。

## 🎯 功能特性

### 五大记忆库
- **目标记忆库**：追踪用户目标（P0/P1/P2优先级）
- **经验记忆库**：记录技术问题和解决方案
- **情感记忆库**：分析用户情绪和习惯偏好
- **会话记忆库**：每日对话摘要（10:1压缩比）
- **版本记忆库**：系统变更历史记录

### 高级功能
- **语义搜索**：基于向量数据库的自然语言检索
- **心跳回忆**：智能情感交互，增强AI连接感
- **RAG增强**：检索增强生成，提升回答质量
- **完全本地化**：零API Key、零Token消耗

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install chromadb sentence-transformers faiss-cpu
```

### 2. 激活HBM
```bash
# Linux/macOS
source {self.hbm_root}/activate_hbm.sh

# Windows
{self.hbm_root}\\activate_hbm.bat
```

### 3. 开始使用
HBM会自动：
- 记录重要对话到记忆库
- 响应触发词进行检索
- 维护记忆库完整性

## 📁 目录结构
```
{self.hbm_root}/
├── memory/           # 五大记忆库
├── scripts/          # 核心脚本
├── config/           # 配置文件
├── models/           # 向量模型
├── logs/             # 系统日志
└── docs/             # 文档
```

## 🔧 配置说明

主要配置文件：`config/hbm_config.json`

可配置项：
- 记忆库启用/禁用
- 向量检索参数
- 心跳回忆频率
- RAG功能开关

## 🤝 社区支持

- GitHub: [你的仓库地址]
- OpenClaw Discord: https://discord.com/invite/clawd
- 问题反馈: 创建 GitHub Issue

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**让 OpenClaw 真正拥有长期记忆，成为更懂你的智能助手！**
"""

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ README.md 生成完成")
    
    def run_health_check(self):
        """运行健康检查"""
        print(f"\n🏥 运行健康检查...")
        
        checks = []
        
        # 检查目录
        required_dirs = [
            self.hbm_root / "memory",
            self.hbm_root / "scripts",
            self.hbm_root / "config",
        ]
        
        for directory in required_dirs:
            if directory.exists():
                checks.append(("✅", f"目录存在: {directory.name}"))
            else:
                checks.append(("❌", f"目录缺失: {directory.name}"))
        
        # 检查配置文件
        config_file = self.hbm_root / "config" / "hbm_config.json"
        if config_file.exists():
            checks.append(("✅", "配置文件存在"))
        else:
            checks.append(("⚠️", "配置文件缺失（可手动创建）"))
        
        # 检查记忆库模板
        memory_files = [
            self.hbm_root / "memory" / "目标记忆库" / "GOALS.md",
            self.hbm_root / "memory" / "经验记忆库" / "TIPS.md",
        ]
        
        for file in memory_files:
            if file.exists():
                checks.append(("✅", f"记忆库文件存在: {file.parent.name}/{file.name}"))
            else:
                checks.append(("⚠️", f"记忆库文件缺失: {file.parent.name}/{file.name}"))
        
        # 显示检查结果
        print(f"📋 检查结果:")
        for status, message in checks:
            print(f"  {status} {message}")
        
        # 总体评估
        error_count = sum(1 for status, _ in checks if status == "❌")
        warning_count = sum(1 for status, _ in checks if status == "⚠️")
        
        if error_count == 0:
            print(f"\n🎉 健康检查通过！HBM 系统已就绪。")
            return True
        else:
            print(f"\n⚠️  发现 {error_count} 个错误，{warning_count} 个警告。")
            print(f"💡 建议：请根据上述检查结果修复问题。")
            return False
    
    def install(self, skip_deps=False, skip_model=False):
        """执行完整安装流程"""
        print(f"=" * 60)
        print(f"🤖 HBM (Humanized Brain Memory) 安装向导")
        print(f"=" * 60)
        
        try:
            # 1. 创建目录结构
            self.create_directory_structure()
            
            # 2. 复制模板文件
            self.copy_template_files()
            
            # 3. 检查依赖
            if not skip_deps:
                self.check_python_dependencies()
            
            # 4. 模型设置
            if not skip_model:
                self.download_model_optional()
            
            # 5. 创建便捷脚本
            self.create_activation_script()
            
            # 6. 生成README
            self.generate_readme()
            
            # 7. 健康检查
            success = self.run_health_check()
            
            print(f"\n" + "=" * 60)
            if success:
                print(f"🎉 HBM 安装完成！")
                print(f"\n📌 下一步：")
                print(f"  1. 安装依赖: pip install chromadb sentence-transformers faiss-cpu")
                print(f"  2. 激活环境: source {self.hbm_root}/activate_hbm.sh")
                print(f"  3. 开始使用: 在 OpenClaw 对话中使用触发词")
                print(f"\n💡 常用触发词:")
                print(f"  • '记忆系统'、'帮我回忆'、'记下来'")
                print(f"  • '查看目标'、'上次怎么解决的'")
            else:
                print(f"⚠️  HBM 安装完成，但存在一些问题需要手动修复。")
            
            print(f"\n📁 HBM 根目录: {self.hbm_root}")
            print(f"=" * 60)
            
            return success
            
        except Exception as e:
            print(f"\n❌ 安装过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description="HBM 系统初始化工具")
    parser.add_argument("--root", help="指定 HBM 根目录")
    parser.add_argument("--skip-deps", action="store_true", help="跳过依赖检查")
    parser.add_argument("--skip-model", action="store_true", help="跳过模型下载提示")
    parser.add_argument("--check", action="store_true", help="只运行健康检查")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    
    args = parser.parse_args()
    
    if args.version:
        print("HBM 初始化脚本 v1.0.0")
        return
    
    installer = HBMInstaller(args.root)
    
    if args.check:
        installer.run_health_check()
    else:
        installer.install(skip_deps=args.skip_deps, skip_model=args.skip_model)


if __name__ == "__main__":
    main()