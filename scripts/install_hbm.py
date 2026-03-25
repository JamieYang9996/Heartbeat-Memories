#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBM Skill 在线安装脚本
用户只需运行：curl -s https://raw.githubusercontent.com/[用户名]/hbm-skill/main/scripts/install_hbm.py | python3
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
import platform
import argparse

# ==================== 配置 ====================

REPO_URL = "https://github.com/OpenClaw-CN/hbm-skill.git"
DEFAULT_BRANCH = "main"
INSTALL_PATH = Path.home() / ".openclaw" / "skills" / "hbm"
ACTIVATE_SCRIPT_URL = "https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/activate_hbm.sh"

# 依赖包
REQUIRED_PACKAGES = [
    "chromadb>=0.4.22",
    "sentence-transformers>=2.2.2",
]

# 根据系统选择FAISS
if platform.system() == "Darwin":  # macOS
    REQUIRED_PACKAGES.append("faiss-cpu>=1.7.4")
else:
    REQUIRED_PACKAGES.append("faiss-cpu>=1.7.4")

# ==================== 工具函数 ====================

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"🤖 {text}")
    print("="*60)

def print_step(step, description):
    """打印步骤"""
    print(f"\n[{step}] {description}")

def print_success(msg):
    """打印成功信息"""
    print(f"✅ {msg}")

def print_warning(msg):
    """打印警告信息"""
    print(f"⚠️  {msg}")

def print_error(msg):
    """打印错误信息"""
    print(f"❌ {msg}")

def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"    $ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print_error(f"命令执行失败: {result.stderr}")
            return False
        return True
    except Exception as e:
        print_error(f"命令执行异常: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    import sys
    if sys.version_info < (3, 8):
        print_error("需要 Python 3.8 或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_openclaw_installed():
    """检查OpenClaw是否已安装"""
    try:
        result = subprocess.run(["openclaw", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"OpenClaw 已安装: {result.stdout.strip()}")
            return True
        else:
            print_warning("OpenClaw 未安装或不在PATH中")
            return False
    except FileNotFoundError:
        print_warning("OpenClaw 未安装或不在PATH中")
        return False

def check_exec_permission():
    """检查OpenClaw的exec权限"""
    print_warning("请确认OpenClaw的exec权限已开启:")
    print("  1. 编辑 ~/.openclaw/openclaw.json")
    print("  2. 设置 \"tools\": { \"profile\": \"coding\" }")
    print("  3. 重启Gateway: openclaw gateway restart")
    return True

def install_dependencies():
    """安装Python依赖"""
    print_step("3", "安装Python依赖包")
    
    # 检查pip是否可用
    if not run_command("python3 -m pip --version"):
        print_error("pip 不可用，请先安装pip")
        return False
    
    # 安装依赖包
    packages_str = " ".join(REQUIRED_PACKAGES)
    print(f"    需要安装: {packages_str}")
    
    # 询问用户确认
    print("\n💡 建议使用虚拟环境（venv）")
    print("   是否继续安装到系统环境？(y/N): ", end="")
    
    # 如果是自动化安装（非交互模式），默认安装
    if not sys.stdin.isatty():
        print("y (非交互模式)")
        user_input = "y"
    else:
        user_input = input().strip().lower()
    
    if user_input not in ['y', 'yes']:
        print_warning("跳过依赖安装，请手动安装:")
        print(f"    pip install {packages_str}")
        return True  # 跳过但不视为失败
    
    # 安装依赖
    cmd = f"python3 -m pip install --upgrade {packages_str}"
    if run_command(cmd):
        print_success("依赖安装完成")
        return True
    else:
        print_error("依赖安装失败")
        return False

def clone_repository():
    """克隆仓库到临时目录"""
    print_step("1", "下载HBM Skill代码")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="hbm_install_")
    print(f"    临时目录: {temp_dir}")
    
    # 克隆仓库
    cmd = f"git clone --depth 1 {REPO_URL} {temp_dir}/hbm-skill"
    if run_command(cmd):
        print_success("代码下载完成")
        return temp_dir
    else:
        print_error("代码下载失败")
        return None

def copy_files(temp_dir):
    """复制文件到安装目录"""
    print_step("2", "安装到OpenClaw技能目录")
    
    source_dir = Path(temp_dir) / "hbm-skill"
    target_dir = INSTALL_PATH
    
    # 备份现有安装（如果存在）
    if target_dir.exists():
        backup_dir = target_dir.with_suffix(f".backup.{int(os.getpid())}")
        print_warning(f"备份现有安装: {target_dir} -> {backup_dir}")
        try:
            shutil.move(target_dir, backup_dir)
            print_success("备份完成")
        except Exception as e:
            print_error(f"备份失败: {e}")
            # 尝试删除
            try:
                shutil.rmtree(target_dir)
                print_success("删除现有目录")
            except Exception as e2:
                print_error(f"删除失败: {e2}")
                return False
    
    # 复制文件
    try:
        shutil.copytree(source_dir, target_dir)
        print_success(f"文件复制完成: {target_dir}")
        return True
    except Exception as e:
        print_error(f"复制失败: {e}")
        return False

def run_initialization():
    """运行初始化脚本"""
    print_step("4", "初始化HBM系统")
    
    init_script = INSTALL_PATH / "scripts" / "hbm_init.py"
    if not init_script.exists():
        print_error(f"初始化脚本不存在: {init_script}")
        return False
    
    # 运行初始化脚本
    cmd = f"cd {INSTALL_PATH} && python3 scripts/hbm_init.py --skip-deps"
    if run_command(cmd, cwd=INSTALL_PATH):
        print_success("HBM系统初始化完成")
        return True
    else:
        print_error("初始化失败")
        return False

def create_activation_script():
    """创建激活脚本（简化版）"""
    print_step("5", "创建便捷使用脚本")
    
    # 创建简单的激活脚本
    activate_content = f"""#!/bin/bash
# HBM 快速激活脚本
export HBM_ROOT="{INSTALL_PATH}"
echo "✅ HBM 环境已设置"
echo "📁 HBM_ROOT: $HBM_ROOT"
echo ""
echo "使用示例:"
echo "  python3 $HBM_ROOT/scripts/hbm_init.py --check"
echo "  在OpenClaw中使用触发词开始记忆"
"""
    
    activate_path = INSTALL_PATH / "activate.sh"
    try:
        with open(activate_path, 'w', encoding='utf-8') as f:
            f.write(activate_content)
        os.chmod(activate_path, 0o755)
        print_success(f"激活脚本: {activate_path}")
        return True
    except Exception as e:
        print_error(f"创建激活脚本失败: {e}")
        return False

def verify_installation():
    """验证安装"""
    print_step("6", "验证安装结果")
    
    checks = []
    
    # 检查目录
    required_dirs = [
        INSTALL_PATH,
        INSTALL_PATH / "memory",
        INSTALL_PATH / "scripts",
    ]
    
    for directory in required_dirs:
        if directory.exists():
            checks.append(("✅", f"目录存在: {directory.name}"))
        else:
            checks.append(("❌", f"目录缺失: {directory.name}"))
    
    # 检查关键文件
    required_files = [
        INSTALL_PATH / "SKILL.md",
        INSTALL_PATH / "scripts" / "hbm_init.py",
        INSTALL_PATH / "memory" / "目标记忆库" / "GOALS_template.md",
    ]
    
    for file in required_files:
        if file.exists():
            checks.append(("✅", f"文件存在: {file.relative_to(INSTALL_PATH)}"))
        else:
            checks.append(("❌", f"文件缺失: {file.relative_to(INSTALL_PATH)}"))
    
    # 显示结果
    print("\n📋 安装验证:")
    for status, message in checks:
        print(f"  {status} {message}")
    
    # 统计
    error_count = sum(1 for status, _ in checks if status == "❌")
    return error_count == 0

def show_next_steps():
    """显示后续步骤"""
    print_header("安装完成！")
    
    print("\n🎉 HBM Skill 已成功安装！")
    print(f"📁 安装位置: {INSTALL_PATH}")
    
    print("\n📌 下一步:")
    print("  1. 重启OpenClaw Gateway:")
    print("     openclaw gateway restart")
    print("  2. 在OpenClaw对话中使用触发词:")
    print("     • '记忆系统'、'帮我回忆'")
    print("     • '记下来'、'查看目标'")
    print("     • '上次怎么解决的'")
    
    print("\n🔧 管理命令:")
    print(f"  # 检查状态")
    print(f"  cd {INSTALL_PATH} && python3 scripts/hbm_init.py --check")
    print(f"  # 更新HBM")
    print(f"  cd {INSTALL_PATH} && git pull origin main")
    print(f"  # 卸载HBM")
    print(f"  rm -rf {INSTALL_PATH}")
    
    print("\n📚 文档:")
    print(f"  查看 {INSTALL_PATH}/README.md 获取完整文档")
    print("  问题反馈: GitHub Issues")

def update_existing():
    """更新现有安装"""
    print_header("更新 HBM Skill")
    
    if not INSTALL_PATH.exists():
        print_error("HBM 未安装，请先安装")
        return False
    
    print_step("1", "更新代码")
    cmd = f"cd {INSTALL_PATH} && git pull origin {DEFAULT_BRANCH}"
    if not run_command(cmd, cwd=INSTALL_PATH):
        print_error("更新失败")
        return False
    
    print_step("2", "运行升级脚本")
    init_script = INSTALL_PATH / "scripts" / "hbm_init.py"
    if init_script.exists():
        cmd = f"cd {INSTALL_PATH} && python3 scripts/hbm_init.py --skip-deps"
        run_command(cmd, cwd=INSTALL_PATH)
    
    print_success("HBM Skill 更新完成")
    return True

def run_diagnostic():
    """运行诊断"""
    print_header("HBM 系统诊断")
    
    if not INSTALL_PATH.exists():
        print_error("HBM 未安装")
        return False
    
    print("\n📋 系统检查:")
    print(f"  • 系统: {platform.system()} {platform.release()}")
    print(f"  • Python: {sys.version}")
    print(f"  • HBM路径: {INSTALL_PATH}")
    
    # 运行内置诊断
    init_script = INSTALL_PATH / "scripts" / "hbm_init.py"
    if init_script.exists():
        print("\n🔍 运行HBM自检:")
        cmd = f"cd {INSTALL_PATH} && python3 scripts/hbm_init.py --check"
        run_command(cmd, cwd=INSTALL_PATH)
    
    return True

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description="HBM Skill 安装工具")
    parser.add_argument("--root", help="指定安装目录（默认：~/.openclaw/skills/hbm）")
    parser.add_argument("--update", action="store_true", help="更新现有安装")
    parser.add_argument("--diagnostic", action="store_true", help="运行诊断")
    parser.add_argument("--skip-deps", action="store_true", help="跳过依赖安装")
    parser.add_argument("--force", action="store_true", help="强制安装（覆盖现有）")
    
    args = parser.parse_args()
    
    # 如果指定了安装目录，修改全局路径
    if args.root:
        global INSTALL_PATH
        INSTALL_PATH = Path(args.root).expanduser().resolve()
        print(f"📁 使用自定义安装目录: {INSTALL_PATH}")
    
    # 打印欢迎信息
    print_header("HBM (Humanized Brain Memory) 安装工具")
    print("🎯 完全本地化的AI长期记忆系统")
    print("📚 五大记忆库 + 语义搜索 + 心跳回忆")
    print("🔒 零API Key、零Token消耗、完全离线")
    
    # 检查前提条件
    if not check_python_version():
        sys.exit(1)
    
    check_openclaw_installed()
    check_exec_permission()
    
    # 根据参数执行不同操作
    if args.diagnostic:
        return run_diagnostic()
    elif args.update:
        return update_existing()
    else:
        # 全新安装
        temp_dir = None
        try:
            # 1. 下载代码
            temp_dir = clone_repository()
            if not temp_dir:
                return False
            
            # 2. 复制文件
            if not copy_files(temp_dir):
                return False
            
            # 3. 安装依赖（可选）
            if not args.skip_deps:
                if not install_dependencies():
                    print_warning("依赖安装失败或跳过，可能需要手动安装")
            
            # 4. 初始化
            if not run_initialization():
                print_warning("初始化可能有警告，但安装继续")
            
            # 5. 创建激活脚本
            create_activation_script()
            
            # 6. 验证
            if not verify_installation():
                print_warning("安装验证有警告，但安装继续")
            
            # 7. 显示后续步骤
            show_next_steps()
            
            return True
            
        except Exception as e:
            print_error(f"安装过程异常: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    print(f"🧹 清理临时目录: {temp_dir}")
                except Exception as e:
                    print_warning(f"清理临时目录失败: {e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)