# 帮我更新 HBM

HBM 已安装，请帮我更新到最新版本：

```bash
# 一行命令自动更新
curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/update_hbm.py | python3
```

或者手动执行：

```bash
# 下载更新脚本
wget https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/update_hbm.py

# 运行更新
python3 update_hbm.py
```

## 更新过程包括：

1. **检查当前安装**：确认 HBM 已安装且为 git 仓库
2. **拉取最新代码**：从 GitHub 获取最新版本
3. **更新依赖**：如有新依赖会提示安装
4. **运行配置更新**：应用最新的配置变更
5. **验证更新**：检查更新是否成功

## 更新选项：

```bash
# 检查更新（不实际执行）
python3 update_hbm.py --check

# 强制更新（覆盖本地修改）
python3 update_hbm.py --force

# 手动更新（不使用 git）
python3 update_hbm.py --manual
```

## 更新后建议：

1. **重启 OpenClaw Gateway**：
   ```bash
   openclaw gateway restart
   ```

2. **检查更新内容**：
   ```bash
   cd ~/.openclaw/skills/hbm && git log --oneline -5
   ```

3. **运行诊断**：
   ```bash
   cd ~/.openclaw/skills/hbm && python3 scripts/hbm_doctor.py
   ```

## 回滚更新

如果更新后出现问题：

```bash
# 回滚到上一个版本
cd ~/.openclaw/skills/hbm && git reset --hard HEAD~1

# 从备份恢复（更新前会自动创建备份）
ls -la ~/.openclaw/skills/hbm.backup.*
```

## 遇到问题？

- **git 仓库问题**：如果安装时不是通过 git，使用 `--manual` 参数
- **冲突问题**：使用 `--force` 参数强制更新
- **权限问题**：确保有写入权限

---

复制上面的命令给你的 AI 助手，它会自动完成更新。 🔄