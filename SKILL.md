---
name: hbm
description: >
  Humanized Brain Memory - 完全本地化的长期记忆系统，五大记忆库 + 语义搜索 + 情感交互
  适用于：需要长期记忆对话、追踪目标、记录经验的OpenClaw用户
  特点：零API Key、零Token消耗、跨平台支持、完全离线运行
triggers:
  - "记忆系统"、"长期记忆"、"帮我回忆"
  - "记下来"、"查看目标"、"上次怎么解决的"
  - "心情记录"、"习惯观察"
  - "memory system"、"recall"、"save this"
  - "check goals"、"how did we solve this"
---

# HBM (Humanized Brain Memory) - 使用指南

**完全本地化的AI长期记忆系统**，让你的OpenClaw记住一切重要对话、目标、经验和情感。

> **📝 发布前注意**: 本文档中的 GitHub 链接包含占位符 `OpenClaw-CN`。  
> 请替换为自己的 GitHub 用户名，或修改脚本中的仓库地址。

## 🚀 一键安装（一句话命令，AI自动执行）

### 方案A：复制给AI自动安装（推荐）
```bash
# 复制这句话给你的AI助手（OpenClaw/Claude Code等）：
帮我安装 HBM：https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py

# AI会自动执行安装，你只需确认权限即可
```

### 方案B：手动执行安装命令
```bash
# 一行命令自动安装
curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py | python3

# 或下载后安装
wget https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py
python3 install_hbm.py
```

### 方案C：通过GitHub手动安装
```bash
# 1. 克隆仓库到本地
git clone https://github.com/OpenClaw-CN/hbm-skill.git

# 2. 复制到OpenClaw技能目录
cp -r hbm-skill ~/.openclaw/skills/hbm

# 3. 初始化记忆系统
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_init.py
```

### 方案D：通过clawhub（如果已上架）
```bash
openclaw skill install hbm
```

## 🔄 一键更新

已经装过了？更新也是一句话：

```bash
# 复制给AI自动更新：
帮我更新 HBM：https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/update_hbm.py

# 或手动更新：
curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/update_hbm.py | python3
```

## 🩺 系统诊断

```bash
# 运行诊断检查
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_doctor.py

# 或直接复制给AI：
帮我检查 HBM：运行 hbm_doctor.py
```

## 📁 系统架构

```
hbm/
├── SKILL.md                    # 本文件
├── memory/                     # 记忆库模板
│   ├── 目标记忆库/GOALS_template.md
│   ├── 经验记忆库/TIPS_template.md  
│   ├── 情感记忆库/DAILY_EMOTIONS_template.md
│   ├── 会话记忆库/YYYY-MM-DD_template.md
│   ├── 版本记忆库/CHANGELOG_template.md
│   └── 心跳回忆/心跳回忆机制.md
├── scripts/                    # 核心脚本
│   ├── hbm_init.py            # 初始化脚本
│   ├── local_memory_system_v2.py
│   └── rag_system.py
├── config/                     # 配置文件
│   └── hbm_config_template.json
└── README.md                   # GitHub说明文档
```

## 🎯 核心功能

### 1. 五大记忆库自动记录
- **目标记忆库**：自动追踪用户目标（P0/P1/P2优先级）
- **经验记忆库**：记录技术问题和解决方案
- **情感记忆库**：分析用户情绪和习惯偏好  
- **会话记忆库**：每日对话摘要（10:1压缩比）
- **版本记忆库**：系统变更历史记录

### 2. 语义搜索（向量检索）
- 基于ChromaDB向量数据库
- 自然语言查询记忆内容
- 本地模型：all-MiniLM-L6-v2（80MB，自动下载）

### 3. 心跳回忆情感交互
- 智能触发回忆对话
- 增强AI情感连接
- 规避敏感节日（如清明节）

### 4. RAG检索增强
- 提升回答准确性和相关性
- 从记忆库检索上下文
- 可配置的开关控制（默认关闭）

## 🔧 使用方法

### 基础使用（开箱即用）
安装后无需额外配置，HBM会自动：
1. 记录重要对话到记忆库
2. 响应触发词进行检索
3. 维护记忆库完整性

### 常用触发词示例
```
用户："记下来，我要学习Python"
AI：✅ 已记录到目标记忆库

用户："上次那个服务器问题怎么解决的？"
AI：🔍 从经验记忆库检索到解决方案...

用户："查看我今天的目标"
AI：📄 从目标记忆库读取...

用户："帮我回忆上周聊过的事情"
AI：❤️ 想起来上周提到的"海边咖啡厅"...
```

### 高级配置（可选）
```bash
# 1. 修改配置
vim ~/.openclaw/skills/hbm/config/hbm_config.json

# 2. 自定义记忆库位置
export HBM_MEMORY_PATH="~/my-memories"

# 3. 启用RAG高级功能
# 编辑配置文件中 enable_limit_and_dedupe: true
```

## ⚙️ 技术规格

| 组件 | 规格 | 说明 |
|------|------|------|
| **向量数据库** | ChromaDB + SQLite | 完全本地存储 |
| **文本向量化** | all-MiniLM-L6-v2 | 384维度，80MB |
| **模型下载源** | ModelScope（国内镜像） | 快速稳定 |
| **存储格式** | Markdown (.md) | 人类可读 |
| **跨平台支持** | Windows/Linux/macOS | 自动适配路径 |
| **依赖项** | Python 3.8+ | chromadb, sentence-transformers |

## 🐛 故障排除

### 常见问题

**Q：安装后没有反应？**
A：确保目录正确：`~/.openclaw/skills/hbm/`，重启OpenClaw。

**Q：模型下载失败？**
A：手动下载：`python3 scripts/download_model.py`，或使用镜像源。

**Q：存储空间不足？**
A：记忆库文件很小，向量模型80MB，RAG日志按月自动压缩。

**Q：跨平台兼容性？**
A：已适配Windows(WSL/Git Bash)、Linux、macOS，自动检测系统。

### 诊断命令
```bash
# 检查HBM状态
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_init.py --check

# 查看记忆库
ls -la ~/.openclaw/skills/hbm/memory/

# 测试语义搜索
python3 scripts/local_memory_system_v2.py --test
```

## 📈 高级功能

### RAG系统优化（可选）
- **Token限制和去重**：防止回答过长（默认关闭）
- **内存缓存**：提升检索速度（默认关闭）
- **日志压缩**：按月自动压缩日志文件

### 自定义扩展
```python
# 扩展新的记忆库类型
# 在 scripts/local_memory_system_v2.py 中添加新集合

# 自定义触发逻辑
# 修改 心跳回忆/心跳回忆机制.md 中的触发条件
```

## 🤝 贡献与反馈

### GitHub仓库
- 项目地址：https://github.com/[你的用户名]/hbm-skill
- Issues：报告问题或建议功能
- Pull Requests：欢迎贡献代码

### 社区支持
- OpenClaw Discord：https://discord.com/invite/clawd
- 中文讨论：Telegram/微信群（如有）

### 版本更新
```bash
# 更新到最新版本
cd ~/.openclaw/skills/hbm
git pull origin main
python3 scripts/hbm_init.py --upgrade
```

## 📝 许可证

MIT License - 详见 LICENSE 文件

---

**HBM让你的OpenClaw真正拥有长期记忆，成为更懂你的智能助手！**

*最后更新：2026年3月25日*