#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBM 系统诊断工具
运行：python3 scripts/hbm_doctor.py
或：cd ~/.openclaw/skills/hbm && python3 scripts/hbm_doctor.py
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
import platform
import importlib.util
import shutil

# ==================== 配置 ====================

def get_hbm_root():
    """获取HBM根目录"""
    # 检查环境变量
    hbm_root = os.getenv("HBM_ROOT")
    if hbm_root:
        return Path(hbm_root).expanduser().resolve()
    
    # 检查默认安装位置
    possible_paths = [
        Path.home() / ".openclaw" / "skills" / "hbm",
        Path.home() / "AppData" / "Local" / "openclaw" / "skills" / "hbm",
        Path.home() / "Library" / "Application Support" / "openclaw" / "skills" / "hbm",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path.resolve()
    
    # 当前目录
    return Path(__file__).parent.parent.resolve()

HBM_ROOT = get_hbm_root()

# ==================== 诊断工具 ====================

class DiagnosticResult:
    """诊断结果"""
    
    def __init__(self, category, test_name, status, message, fix=None):
        self.category = category
        self.test_name = test_name
        self.status = status  # "PASS", "WARN", "FAIL", "SKIP"
        self.message = message
        self.fix = fix
    
    def __str__(self):
        status_icons = {
            "PASS": "✅",
            "WARN": "⚠️",
            "FAIL": "❌",
            "SKIP": "⏭️"
        }
        icon = status_icons.get(self.status, "❓")
        return f"{icon} [{self.category}] {self.test_name}: {self.message}"

class HBMDiagnostic:
    """HBM系统诊断"""
    
    def __init__(self):
        self.results = []
        self.system = platform.system()
        self.python_version = sys.version
        
        print(f"\n🔍 HBM 系统诊断报告")
        print(f"📁 HBM根目录: {HBM_ROOT}")
        print(f"💻 系统: {self.system} {platform.release()}")
        print(f"🐍 Python: {self.python_version}")
        print("-" * 60)
    
    def add_result(self, category, test_name, status, message, fix=None):
        """添加诊断结果"""
        result = DiagnosticResult(category, test_name, status, message, fix)
        self.results.append(result)
        print(result)
        return result.status != "FAIL"
    
    def run_all_tests(self):
        """运行所有诊断测试"""
        print("\n🧪 运行诊断测试...")
        
        # 1. 系统基础检查
        self.test_system_basics()
        
        # 2. HBM安装检查
        self.test_hbm_installation()
        
        # 3. Python依赖检查
        self.test_python_dependencies()
        
        # 4. 记忆库检查
        self.test_memory_libraries()
        
        # 5. 功能测试
        self.test_functionality()
        
        # 显示总结
        self.show_summary()
    
    def test_system_basics(self):
        """系统基础检查"""
        self.add_result("系统", "Python版本", 
                       "PASS" if sys.version_info >= (3, 8) else "FAIL",
                       f"Python {sys.version.split()[0]}",
                       "需要Python 3.8或更高版本")
        
        # 检查磁盘空间
        try:
            total, used, free = shutil.disk_usage(HBM_ROOT)
            free_gb = free // (2**30)
            status = "WARN" if free_gb < 1 else "PASS"
            self.add_result("系统", "磁盘空间", status,
                           f"可用空间: {free_gb}GB",
                           "建议保持至少1GB可用空间" if free_gb < 1 else None)
        except:
            self.add_result("系统", "磁盘空间", "SKIP", "无法检查磁盘空间")
    
    def test_hbm_installation(self):
        """HBM安装检查"""
        # 检查安装目录
        if not HBM_ROOT.exists():
            self.add_result("安装", "HBM根目录", "FAIL",
                           f"目录不存在: {HBM_ROOT}",
                           "请先安装HBM: curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py | python3")
            return False
        
        self.add_result("安装", "HBM根目录", "PASS", f"目录存在: {HBM_ROOT}")
        
        # 检查关键目录
        required_dirs = [
            ("memory", "记忆库目录"),
            ("scripts", "脚本目录"),
            ("config", "配置目录"),
        ]
        
        for dir_name, description in required_dirs:
            dir_path = HBM_ROOT / dir_name
            if dir_path.exists():
                self.add_result("安装", description, "PASS", f"目录存在: {dir_name}")
            else:
                self.add_result("安装", description, "FAIL", f"目录缺失: {dir_name}",
                               f"重新运行初始化: cd {HBM_ROOT} && python3 scripts/hbm_init.py")
        
        # 检查关键文件
        required_files = [
            ("SKILL.md", "技能描述文件"),
            ("scripts/hbm_init.py", "初始化脚本"),
            ("memory/目标记忆库/GOALS_template.md", "目标记忆库模板"),
            ("config/hbm_config_template.json", "配置文件模板"),
        ]
        
        for file_path, description in required_files:
            full_path = HBM_ROOT / file_path
            if full_path.exists():
                self.add_result("安装", description, "PASS", f"文件存在: {file_path}")
            else:
                self.add_result("安装", description, "WARN", f"文件缺失: {file_path}",
                               f"从GitHub重新下载或运行初始化")
        
        return True
    
    def test_python_dependencies(self):
        """Python依赖检查"""
        required_packages = [
            ("chromadb", "向量数据库"),
            ("sentence_transformers", "文本向量化"),
        ]
        
        for module_name, description in required_packages:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                self.add_result("依赖", description, "PASS", f"已安装: {module_name}")
            else:
                self.add_result("依赖", description, "FAIL", f"未安装: {module_name}",
                               f"安装: pip install {module_name.replace('_', '-')}")
        
        # 检查FAISS（可选）
        try:
            import faiss
            self.add_result("依赖", "FAISS向量库", "PASS", "已安装: faiss")
        except ImportError:
            self.add_result("依赖", "FAISS向量库", "WARN", "未安装: faiss",
                           "安装: pip install faiss-cpu (macOS/Windows: conda install -c conda-forge faiss-cpu)")
    
    def test_memory_libraries(self):
        """记忆库检查"""
        memory_dir = HBM_ROOT / "memory"
        
        if not memory_dir.exists():
            self.add_result("记忆库", "记忆库目录", "FAIL", "目录不存在", 
                           "重新运行初始化脚本")
            return
        
        # 检查五大记忆库
        libraries = [
            ("目标记忆库", "存储用户目标"),
            ("经验记忆库", "存储技术经验"),
            ("情感记忆库", "存储情绪记录"),
            ("会话记忆库", "存储对话摘要"),
            ("版本记忆库", "存储版本历史"),
            ("心跳回忆", "情感交互机制"),
        ]
        
        for lib_name, description in libraries:
            lib_path = memory_dir / lib_name
            if lib_path.exists():
                # 检查是否有实际文件（非模板）
                has_files = False
                try:
                    for item in lib_path.iterdir():
                        if item.is_file() and not item.name.endswith("_template.md"):
                            has_files = True
                            break
                    
                    if has_files:
                        self.add_result("记忆库", lib_name, "PASS", 
                                       f"已初始化，有用户数据")
                    else:
                        self.add_result("记忆库", lib_name, "INFO", 
                                       f"已创建，等待用户数据",
                                       f"在OpenClaw中使用触发词开始记录")
                except:
                    self.add_result("记忆库", lib_name, "WARN", 
                                   f"目录存在但无法读取")
            else:
                self.add_result("记忆库", lib_name, "WARN", 
                               f"目录不存在",
                               f"运行初始化脚本或手动创建")
    
    def test_functionality(self):
        """功能测试"""
        # 测试初始化脚本
        init_script = HBM_ROOT / "scripts" / "hbm_init.py"
        if init_script.exists():
            self.add_result("功能", "初始化脚本", "PASS", "脚本可用")
        else:
            self.add_result("功能", "初始化脚本", "FAIL", "脚本缺失")
        
        # 测试向量搜索脚本
        vector_script = HBM_ROOT / "scripts" / "local_memory_system_v2.py"
        if vector_script.exists():
            # 检查文件是否可读
            try:
                with open(vector_script, 'r', encoding='utf-8') as f:
                    content = f.read(100)
                self.add_result("功能", "向量搜索脚本", "PASS", "脚本可用")
            except:
                self.add_result("功能", "向量搜索脚本", "WARN", "脚本无法读取")
        else:
            self.add_result("功能", "向量搜索脚本", "FAIL", "脚本缺失")
        
        # 测试配置
        config_file = HBM_ROOT / "config" / "hbm_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.add_result("功能", "配置文件", "PASS", "配置文件有效")
            except json.JSONDecodeError:
                self.add_result("功能", "配置文件", "FAIL", "配置文件格式错误",
                               f"检查文件: {config_file}")
            except:
                self.add_result("功能", "配置文件", "WARN", "配置文件无法读取")
        else:
            # 检查模板文件
            template_file = HBM_ROOT / "config" / "hbm_config_template.json"
            if template_file.exists():
                self.add_result("功能", "配置文件", "INFO", 
                               "使用模板配置，建议创建自定义配置",
                               f"复制模板: cp {template_file} {config_file}")
            else:
                self.add_result("功能", "配置文件", "WARN", "配置文件缺失")
    
    def show_summary(self):
        """显示诊断摘要"""
        print("\n" + "="*60)
        print("📊 诊断摘要")
        print("="*60)
        
        # 统计结果
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0, "INFO": 0}
        for result in self.results:
            counts[result.status] = counts.get(result.status, 0) + 1
        
        total = len(self.results)
        print(f"总计: {total} 项检查")
        print(f"✅ 通过: {counts['PASS']}  ⚠️ 警告: {counts['WARN']}  ❌ 失败: {counts['FAIL']}")
        print(f"⏭️ 跳过: {counts['SKIP']}  ℹ️  信息: {counts.get('INFO', 0)}")
        
        # 显示失败的测试
        failures = [r for r in self.results if r.status == "FAIL"]
        if failures:
            print(f"\n❌ 需要立即修复的问题 ({len(failures)}项):")
            for failure in failures:
                print(f"  • {failure.test_name}: {failure.message}")
                if failure.fix:
                    print(f"    修复: {failure.fix}")
        
        # 显示警告
        warnings = [r for r in self.results if r.status == "WARN"]
        if warnings:
            print(f"\n⚠️  建议修复的警告 ({len(warnings)}项):")
            for warning in warnings:
                print(f"  • {warning.test_name}: {warning.message}")
        
        # 总体评估
        if counts['FAIL'] > 0:
            print(f"\n🔴 HBM 系统存在问题，需要修复")
            print("💡 建议按上述修复建议操作")
        elif counts['WARN'] > 0:
            print(f"\n🟡 HBM 系统基本可用，但有警告")
            print("💡 建议修复警告以优化使用体验")
        else:
            print(f"\n🟢 HBM 系统状态良好！")
        
        # 下一步建议
        print(f"\n📌 下一步:")
        if counts['FAIL'] > 0:
            print("  1. 修复上述失败项")
            print("  2. 重新运行诊断: python3 scripts/hbm_doctor.py")
        else:
            print("  1. 重启OpenClaw: openclaw gateway restart")
            print("  2. 在对话中使用触发词测试")
        
        print(f"  3. 查看详细文档: {HBM_ROOT}/README.md")
        print(f"  4. 获取帮助: GitHub Issues 或 OpenClaw Discord")

# ==================== 命令行接口 ====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="HBM 系统诊断工具")
    parser.add_argument("--quick", action="store_true", help="快速检查（跳过详细测试）")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复问题")
    parser.add_argument("--json", action="store_true", help="输出JSON格式结果")
    
    args = parser.parse_args()
    
    diagnostic = HBMDiagnostic()
    diagnostic.run_all_tests()
    
    if args.json:
        # 输出JSON格式（用于自动化）
        output = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "hbm_root": str(HBM_ROOT),
            "system": platform.system(),
            "python_version": sys.version,
            "results": [
                {
                    "category": r.category,
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "fix": r.fix
                }
                for r in diagnostic.results
            ]
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    
    # 如果有失败项，返回非零退出码
    failure_count = sum(1 for r in diagnostic.results if r.status == "FAIL")
    return failure_count

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)