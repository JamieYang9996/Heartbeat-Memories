# 帮我安装 Heartbeat-Memories

请帮我安装 Heartbeat-Memories (HBM) 记忆系统：

```bash
# 一行命令自动安装
curl -s https://raw.githubusercontent.com/JamieYang9996/hbm-skill/main/scripts/install_hbm.py | python3
```

或者手动执行：

```bash
# 下载安装脚本
wget https://raw.githubusercontent.com/JamieYang9996/hbm-skill/main/scripts/install_hbm.py

# 运行安装
python3 install_hbm.py
```

## 安装过程包括：

1. **下载代码**：从 GitHub 获取最新版本
2. **安装依赖**：自动安装 Python 包（chromadb, sentence-transformers, faiss-cpu）
3. **配置系统**：创建记忆库目录和配置文件
4. **初始化**：设置向量数据库和记忆库模板
5. **验证**：检查安装是否成功

## 前置要求：

- ✅ OpenClaw v1.0+ 已安装
- ✅ OpenClaw exec 权限已开启（`tools.profile: "coding"`）
- ✅ Python 3.8+ 环境
- ✅ 约 100MB 磁盘空间

## 安装后步骤：

1. **重启 OpenClaw Gateway**：
   ```bash
   openclaw gateway restart
   ```

2. **测试功能**：
   - 在 OpenClaw 对话中使用触发词："记忆系统"、"帮我回忆"
   - 运行诊断：`python3 ~/.openclaw/skills/hbm/scripts/hbm_doctor.py`

## 遇到问题？

- **权限问题**：确认 OpenClaw exec 权限已开启
- **网络问题**：国内用户可使用镜像源
- **依赖问题**：手动安装 `pip install chromadb sentence-transformers faiss-cpu`

## 更新 Heartbeat-Memories

已经安装过了？更新命令：

```bash
curl -s https://raw.githubusercontent.com/JamieYang9996/hbm-skill/main/scripts/update_hbm.py | python3
```

---

复制上面的命令给你的 AI 助手，它会自动完成安装。 🚀