#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heartbeat-Memories Skill 更新脚本
运行：curl -s https://raw.githubusercontent.com/[用户名]/hbm-skill/main/scripts/update_hbm.py | python3
"""

import os
import sys
import subprocess
from pathlib import Path
import platform
import argparse

# ==================== 配置 ====================

INSTALL_PATH = Path.home() / ".openclaw" / "skills" / "hbm"
REPO_URL = "https://github.com/OpenClaw-CN/hbm-skill.git"
DEFAULT_BRANCH = "main"

# ==================== 工具函数 ====================

def print_header(text):
    print("\n" + "="*60)
    print(f"🔄 {text}")
    print("="*60)

def print_step(step, description):
    print(f"\n[{step}] {description}")

def print_success(msg):
    print(f"✅ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"    $ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    stderr: {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print_error(f"命令执行异常: {e}")
        return False

# ==================== 更新函数 ====================

def check_installation():
    """检查 Heartbeat-Memories 是否已安装"""
    if not INSTALL_PATH.exists():
        print_error(f"Heartbeat-Memories 未安装: {INSTALL_PATH}")
        print("💡 请先安装 Heartbeat-Memories:")
        print("   curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py | python3")
        return False
    
    # 检查git仓库
    git_dir = INSTALL_PATH / ".git"
    if not git_dir.exists():
        print_warning("当前安装不是git仓库，无法自动更新")
        print("💡 建议重新安装:")
        print(f"  1. 备份: mv {INSTALL_PATH} {INSTALL_PATH}.backup")
        print("  2. 重新安装: curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py | python3")
        return False
    
    return True

def update_via_git():
    """通过git更新"""
    print_step("1", "拉取最新代码")
    
    # 检查当前分支
    branch_cmd = "git branch --show-current"
    result = subprocess.run(branch_cmd, shell=True, cwd=INSTALL_PATH, capture_output=True, text=True)
    current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
    
    print(f"    当前分支: {current_branch}")
    
    # 拉取更新
    pull_cmd = f"git pull origin {DEFAULT_BRANCH}"
    if run_command(pull_cmd, cwd=INSTALL_PATH):
        print_success("代码更新完成")
        return True
    else:
        print_error("代码更新失败")
        return False

def update_via_manual():
    """手动更新（如果没有git）"""
    print_step("1", "下载最新版本")
    
    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="hbm_update_")
    print(f"    临时目录: {temp_dir}")
    
    # 克隆最新版本
    clone_cmd = f"git clone --depth 1 {REPO_URL} {temp_dir}/hbm-skill"
    if not run_command(clone_cmd):
        return False
    
    # 备份现有文件
    import shutil
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = INSTALL_PATH.with_suffix(f".backup.{timestamp}")
    
    print_step("2", "备份现有安装")
    try:
        shutil.copytree(INSTALL_PATH, backup_dir, dirs_exist_ok=True)
        print_success(f"备份完成: {backup_dir}")
    except Exception as e:
        print_error(f"备份失败: {e}")
        return False
    
    # 复制新文件
    print_step("3", "复制新版本")
    source_dir = Path(temp_dir) / "hbm-skill"
    
    # 先删除现有文件（保留备份）
    try:
        # 删除除.git外的所有文件
        for item in INSTALL_PATH.iterdir():
            if item.name != ".git":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    except Exception as e:
        print_warning(f"清理现有文件时警告: {e}")
    
    # 复制新文件
    try:
        for item in source_dir.iterdir():
            if item.name != ".git":
                dest = INSTALL_PATH / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        print_success("文件复制完成")
    except Exception as e:
        print_error(f"复制文件失败: {e}")
        return False
    
    # 清理临时目录
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
    
    return True

def run_post_update():
    """运行更新后脚本"""
    print_step("2", "运行更新后配置")
    
    # 检查初始化脚本
    init_script = INSTALL_PATH / "scripts" / "hbm_init.py"
    if init_script.exists():
        cmd = f"cd {INSTALL_PATH} && python3 scripts/hbm_init.py --skip-deps"
        if run_command(cmd, cwd=INSTALL_PATH):
            print_success("配置更新完成")
        else:
            print_warning("配置更新可能有警告")
    else:
        print_warning("初始化脚本不存在，跳过配置更新")
    
    return True

def check_changes():
    """检查更新内容"""
    print_step("3", "检查更新内容")
    
    # 获取最近的提交信息
    log_cmd = "git log --oneline -5"
    result = subprocess.run(log_cmd, shell=True, cwd=INSTALL_PATH, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        print("\n📝 最近更新:")
        print(result.stdout)
    else:
        print("   无最近更新信息")
    
    return True

def show_update_summary():
    """显示更新摘要"""
    print_header("更新完成！")
    
    print("\n🎉 Heartbeat-Memories Skill 已更新到最新版本")
    print(f"📁 安装位置: {INSTALL_PATH}")
    
    print("\n📌 下一步:")
    print("  1. 重启OpenClaw Gateway:")
    print("     openclaw gateway restart")
    print("  2. 检查系统状态:")
    print(f"     cd {INSTALL_PATH} && python3 scripts/hbm_init.py --check")
    
    print("\n🔧 如有问题:")
    print("  1. 查看更新日志:")
    print(f"     cd {INSTALL_PATH} && git log --oneline -10")
    print("  2. 回滚到上一个版本:")
    print(f"     cd {INSTALL_PATH} && git reset --hard HEAD~1")
    print("  3. 从备份恢复:")
    print("     查看备份目录: ls -la ~/.openclaw/skills/hbm.backup.*")
    
    return True

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description="Heartbeat-Memories Skill 更新工具")
    parser.add_argument("--root", help="指定 Heartbeat-Memories 安装目录（默认：~/.openclaw/skills/hbm）")
    parser.add_argument("--check", action="store_true", help="检查更新（不执行）")
    parser.add_argument("--force", action="store_true", help="强制更新（覆盖修改）")
    parser.add_argument("--manual", action="store_true", help="手动更新（不使用git）")
    
    args = parser.parse_args()
    
    # 如果指定了安装目录，修改全局路径
    if args.root:
        global INSTALL_PATH
        INSTALL_PATH = Path(args.root).expanduser().resolve()
        print(f"📁 使用自定义安装目录: {INSTALL_PATH}")
    
    print_header("Heartbeat-Memories Skill 更新工具")
    
    # 检查是否已安装
    if not check_installation():
        return False
    
    if args.check:
        # 检查更新
        print_step("检查", "检查可用更新")
        
        # 获取远程信息
        if run_command("git fetch origin", cwd=INSTALL_PATH):
            # 比较本地和远程
            status_cmd = "git status -uno"
            result = subprocess.run(status_cmd, shell=True, cwd=INSTALL_PATH, capture_output=True, text=True)
            
            if result.returncode == 0:
                if "Your branch is up to date" in result.stdout:
                    print_success("已是最新版本")
                else:
                    print("📢 有可用更新:")
                    print(result.stdout)
            else:
                print_warning("无法检查更新状态")
        
        return True
    
    # 执行更新
    success = False
    
    if args.manual or not (INSTALL_PATH / ".git").exists():
        # 手动更新
        success = update_via_manual()
    else:
        # git更新
        success = update_via_git()
    
    if success:
        # 运行更新后配置
        run_post_update()
        
        # 检查更新内容
        if not args.manual and (INSTALL_PATH / ".git").exists():
            check_changes()
        
        # 显示摘要
        show_update_summary()
    else:
        print_error("更新失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)