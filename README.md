# Heartbeat-Memories (HBM) - OpenClaw Skill

<div align="center">

![HBM Logo](https://img.shields.io/badge/HBM-Heartbeat%20Memories-blue)
![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![GitHub Stars](https://img.shields.io/github/stars/JamieYang9996/Heartbeat-Memories?style=social)
![GitHub Forks](https://img.shields.io/github/forks/JamieYang9996/Heartbeat-Memories?style=social)
![GitHub Issues](https://img.shields.io/github/issues/JamieYang9996/Heartbeat-Memories)
![GitHub Last Commit](https://img.shields.io/github/last-commit/JamieYang9996/Heartbeat-Memories)

**完全本地化的长期记忆系统**，让你的 OpenClaw 记住一切重要对话、目标、经验和情感。

</div>

> **📝 使用前注意**: 本项目中的 GitHub 链接包含占位符 `JamieYang9996`。  
> 发布前请替换为自己的 GitHub 用户名，或 Fork 后修改脚本中的仓库地址。

---

## 🚀 快速解答新用户疑问

| 常见疑问 | 简短回答 |
|----------|----------|
| **会与现有记忆系统冲突吗？** | ❌ **不会**，完美协作：原系统负责短期记忆，HBM负责长期结构化记忆 |
| **安装复杂吗？需要配置很多参数吗？** | 🚀 **一键安装**，开箱即用，90%用户无需额外配置 |
| **会占用很多磁盘空间吗？** | 📦 **轻量级**，约100MB空间（模型80MB + 代码20MB） |
| **心跳回忆会不会很烦人？** | ⚙️ **智能触发**，频率可调，支持静默模式，紧急时自动暂停 |
| **我的隐私数据安全吗？** | 🔒 **100%本地**，零数据上传，零API调用，所有数据留在你电脑 |
| **支持哪些平台？** | 💻 **跨平台**：Windows (WSL/Git Bash)、Linux、macOS |
| **需要额外的API Key吗？** | 🆓 **零成本**，完全免费开源，无需任何API Key |
| **如何卸载？** | 🗑️ **简单删除**目录即可完全卸载，不留痕迹 |

---

## 🎯 为什么需要 Heartbeat-Memories？

### 痛点一：传统 Memory 文件太原始，无法结合场景使用
你可能尝试过用 `.memory` 或 `.txt` 文件记录 AI 对话，但很快发现：
- **散乱无序**：所有内容堆在一个文件，找起来像大海捞针
- **缺乏结构**：目标、经验、情感混在一起，难以分类检索  
- **无法场景化**：无法针对不同使用场景（项目追踪、问题排查、情感记录）进行精细化处理

### 痛点二：AI 总是回复长文字，浪费资源还没有情感
你有没有发现 AI 助手有这些问题？
- **长篇大论**：每次回答都像写论文，浪费 Token 和注意力
- **机械重复**：同样的技术问题，每次都要从头解释
- **缺乏情感**：AI 像个冷漠的数据库，不懂你的情绪和习惯
- **没有专属感**：每次对话都是“从零开始”，无法建立长期关系

### ✨ 解决方案：精细化拆解 + 情感化交互
Heartbeat-Memories 通过 **五大记忆库精细化拆解** + **心跳回忆情感互动**，彻底解决上述问题：

📝 **"上周我们讨论的那个项目目标是什么？"** → 目标记忆库实时追踪，进度一目了然
🎯 **"我之前说想学习 Python，现在进度如何？"** → 目标分 P0/P1/P2 优先级，自动提醒
🔧 **"上次服务器 502 错误怎么解决的？"** → 经验记忆库沉淀最佳实践，避免重复踩坑
💭 **"帮我回忆上个月聊过的创意想法"** → 会话记忆库智能摘要，10:1 压缩比快速查找
❤️ **"我最近心情怎么样？有什么习惯变化？"** → 情感记忆库分析情绪模式，AI 越来越懂你

传统 AI 对话机器人每次会话都是"从零开始"。Heartbeat-Memories 通过**五大记忆库场景化拆解 + 心跳回忆情感连接**，让 OpenClaw 真正理解你、记住你、成为你的专属智能助手。

---

## ✨ Heartbeat-Memories 是什么？

**Heartbeat-Memories (HBM)** 是一个**完全本地化的 AI 长期记忆系统**，包含五大记忆库、语义搜索和情感交互功能。

### 🧠 五大记忆库系统
| 记忆库 | 功能 | 解决什么问题 |
|--------|------|------------|
| **目标记忆库** | 追踪用户目标（P0/P1/P2优先级） | 目标容易遗忘，缺乏追踪 |
| **经验记忆库** | 记录技术问题和解决方案 | 重复踩坑，经验无法沉淀 |
| **情感记忆库** | 分析用户情绪和习惯偏好 | AI 不懂你的情绪和习惯 |
| **会话记忆库** | 每日对话摘要（10:1压缩比） | 对话历史太长，难以查找 |
| **版本记忆库** | 系统变更历史记录 | 配置变更缺乏记录 |

### 🔍 智能检索能力
- **语义搜索**: 基于 ChromaDB 向量数据库，自然语言查询记忆
- **关键词检索**: 从 Markdown 文件快速查找相关信息
- **混合检索**: 向量 + 关键词结合，提升检索准确性
- **RAG 增强**: 检索增强生成，提升回答质量和相关性

### ❤️ 心跳回忆情感交互（核心创新）
**模仿人类对话，建立长期情感连接**——解决 AI 回复冗长、缺乏情感的问题：

#### 🎭 高度仿真的人类互动
- **智能触发机制**: AI 像朋友一样主动回忆："对了，想起来上周聊的‘海边咖啡厅’‘日落’‘拍照’，你后来去了吗？"
- **自然对话流**: 随机在日常对话中插入回忆（30%概率），避免机械感
- **情感智能识别**: 分析你的情绪状态（高兴/平静/疑惑/成就），调整互动方式

#### ⚙️ 灵活可调的配置系统
- **概率可配置**: 每个触发场景的概率可单独调整（30%/50%/100%）
- **频率控制**: 每日上限、最小间隔、节假日特殊规则
- **场景定制**: 支持日常对话、任务完成、目标遗忘、节日关怀等多种场景
- **敏感日规避**: 自动规避清明节等敏感节日，尊重文化传统

#### 🌱 长期养成与专属感
- **习惯学习**: 记录你的工作模式、偏好话题、常用关键词
- **专属记忆**: 基于你的历史对话构建个性化回忆库
- **渐进式优化**: 通过静默复盘不断优化触发时机和话术
- **情感进化**: AI 随着时间越来越懂你，建立真正的“长期关系”

#### 🔧 完全可控的用户体验
- **开关控制**: 所有功能默认开启但可随时关闭
- **实时调整**: 可根据反馈即时修改配置参数
- **透明规则**: 所有触发逻辑和频率限制完全公开
- **零干扰承诺**: 紧急任务、深夜时段、忙碌状态自动暂停触发

### 🚀 技术优势
- **完全本地化**: 零 API Key、零 Token 消耗、完全离线运行
- **跨平台支持**: Windows (WSL/Git Bash)、Linux、macOS
- **易于集成**: 标准 OpenClaw Skill 格式，一键安装
- **可配置性强**: 所有功能都有开关控制，按需启用

---

## 📦 安装指南

### ⚠️ 前置要求
1. **OpenClaw v1.0+** 已安装并运行
2. **exec 权限开启**（OpenClaw 需要执行 shell 命令）
   ```bash
   # 在 ~/.openclaw/openclaw.json 中设置
   "tools": { "profile": "coding" }
   # 然后重启: openclaw gateway restart
   ```
3. **Python 3.8+** 环境
4. **约 100MB** 磁盘空间（含向量模型）

### 🚀 一句话安装（像 agent-reach 一样简单）

#### 方案 A：复制给 AI 自动安装
```bash
# 复制这句话给你的 AI 助手（OpenClaw/Claude Code 等）：
帮我安装 Heartbeat-Memories：https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/install_hbm.py

# AI 会自动：
# 1. 下载最新代码
# 2. 安装到正确位置
# 3. 配置 Python 依赖
# 4. 初始化记忆系统
# 5. 验证安装结果
```

#### 方案 B：手动执行安装命令
```bash
# 一行命令自动完成所有步骤
curl -s https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/install_hbm.py | python3
```

#### 方案 C：GitHub 手动安装
```bash
# 1. 克隆仓库
git clone https://github.com/JamieYang9996/Heartbeat-Memories.git

# 2. 复制到技能目录
cp -r Heartbeat-Memories ~/.openclaw/skills/hbm

# 3. 初始化系统
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_init.py
```

### 🔄 一键更新
已经装过了？更新也是一句话：

```bash
# 复制给 AI 自动更新：
帮我更新 Heartbeat-Memories：https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/update_hbm.py

# 或手动更新：
curl -s https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/update_hbm.py | python3
```

### 🩺 系统诊断
```bash
# 检查 HBM 系统状态
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_doctor.py

# 或复制给 AI：
帮我检查 Heartbeat-Memories：运行 hbm_doctor.py
```

---

## 🚀 快速开始

### 第一次使用
1. **安装完成**后，重启 OpenClaw
2. 在对话中使用触发词测试功能
3. Heartbeat-Memories 会自动开始记录重要对话

### 常用触发词
```
# 中文触发词
"记忆系统"、"长期记忆"、"帮我回忆"
"记下来"、"查看目标"、"上次怎么解决的"
"心情记录"、"习惯观察"

# 英文触发词  
"memory system"、"recall"、"save this"
"check goals"、"how did we solve this"
```

### 使用示例
```markdown
用户: "记下来，我要学习 React 框架"
AI: ✅ 已记录到目标记忆库

用户: "上次服务器 502 错误怎么解决的？"
AI: 🔍 从经验记忆库检索到解决方案...

用户: "帮我回忆上周聊过的项目"
AI: ❤️ 想起来上周提到的"用户仪表板设计"...
```

### 心跳回忆示例
```
AI: ❤️ 对了，想起来上周五聊到的"海边咖啡厅""日落""拍照"，你后来有没有去成呢？

用户: "去了！特别美!" 
→ AI 记录成功回忆，增强情感连接

用户: "好像忘了有这事了..." 
→ AI 补充完整细节，恢复丢失记忆
```

---

## 🏗️ 系统架构

```
Heartbeat-Memories/
├── SKILL.md                    # OpenClaw Skill 描述文件
├── README.md                   # 项目说明文档
├── CHANGELOG.md                # 版本更新日志
├── LICENSE                     # MIT 许可证
├── requirements.txt            # Python 依赖列表
├── .gitignore                  # Git 忽略规则
├── memory/                     # 五大记忆库模板
│   ├── 目标记忆库/GOALS_template.md
│   ├── 经验记忆库/TIPS_template.md
│   ├── 情感记忆库/DAILY_EMOTIONS_template.md
│   ├── 会话记忆库/YYYY-MM-DD_template.md
│   ├── 版本记忆库/CHANGELOG_template.md
│   └── 心跳回忆/心跳回忆机制.md
├── scripts/                    # 核心脚本
│   ├── hbm_init.py            # 初始化脚本
│   ├── install_hbm.py         # 在线安装脚本
│   ├── update_hbm.py          # 更新脚本
│   ├── hbm_doctor.py          # 诊断工具
│   ├── local_memory_system_v2.py  # 语义搜索
│   ├── rag_system.py          # RAG 系统
│   └── log_compressor.py      # 日志压缩器
├── config/                     # 配置文件
│   └── hbm_config_template.json
└── docs/                       # 文档
    ├── install.md
    └── update.md
```

---

## ⚙️ 技术规格

| 组件 | 规格 | 说明 |
|------|------|------|
| **Python** | 3.8+ | 必需版本 |
| **向量模型** | all-MiniLM-L6-v2 | 384 维度，80MB，自动下载 |
| **向量数据库** | ChromaDB 0.4.22+ | SQLite 后端，完全本地 |
| **依赖包** | 3 个核心包 | chromadb, sentence-transformers, faiss-cpu |
| **存储占用** | ~100MB | 模型 80MB + 代码 20MB |
| **内存占用** | 200-300MB | 运行时占用 |
| **跨平台** | ✅ Windows/Linux/macOS | 自动检测系统 |

---

## 🔧 高级功能

### RAG 系统优化（可选）
- **Token 限制和去重**: 防止回答过长（默认关闭）
- **内存缓存**: 提升检索速度（默认关闭）
- **日志压缩**: 按月自动压缩日志文件（保留最近一个月详细版）

### 自定义扩展
```python
# 扩展新的记忆库类型
# 在 scripts/local_memory_system_v2.py 中添加新集合

# 自定义触发逻辑
# 修改 memory/心跳回忆/心跳回忆机制.md 中的触发条件
```

### 开发者 API
```python
from scripts.rag_system import RAGSystem

# 初始化 RAG 系统
rag = RAGSystem()

# 执行检索
results = rag.retrieve("如何配置 Python 虚拟环境？")

# 获取上下文
context = rag.format_context(results)
```

---

## 🐛 故障排除

### 常见问题

**Q: 安装后没有反应？**
A: 检查目录是否正确：`~/.openclaw/skills/hbm/`，重启 OpenClaw。

**Q: 模型下载失败？**
A: 国内用户使用镜像：
```bash
export HF_ENDPOINT=https://mirrors.tuna.tsinghua.edu.cn/hugging-face
python3 scripts/hbm_init.py
```

**Q: 内存不足？**
A: 可禁用部分功能：
```json
{"启用语义搜索": false, "启用心跳回忆": false}
```

**Q: 跨平台问题？**
A: 确保使用正确路径分隔符，Windows 用户建议使用 Git Bash。

### 诊断命令
```bash
# 检查 HBM 状态
python3 scripts/hbm_init.py --check

# 测试语义搜索
python3 scripts/local_memory_system_v2.py --test

# 查看日志
tail -f logs/hbm_system.log
```

---

## 🤝 贡献与支持

### GitHub 仓库
- 项目地址：https://github.com/JamieYang9996/Heartbeat-Memories
- Issues：报告问题或建议功能
- Pull Requests：欢迎贡献代码

### 版本更新
```bash
# 更新到最新版本
cd ~/.openclaw/skills/hbm
git pull origin main
python3 scripts/hbm_init.py --upgrade
```

---

## 🚀 发布优化（仓库维护者指南）

### GitHub 仓库优化
- **添加 Topics 标签**：提升搜索曝光 300-500%（建议：`openclaw`, `ai-assistant`, `memory-system`, `local-ai`）
- **完善仓库描述**：在 GitHub Settings → About 中填写详细描述
- **检查渲染效果**：确保 README 表格、徽章、代码块正常显示

### 社区推广策略
- **Discord**：OpenClaw #skills 频道首发，分享安装命令和亮点
- **中文社区**：V2EX、知乎、SegmentFault 技术分享
- **ClawHub 上架**：积累 10+ stars 后申请官方技能库上架

📖 **完整发布指南**：[docs/发布优化指南.md](docs/发布优化指南.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

**Heartbeat-Memories 让你的 OpenClaw 真正拥有长期记忆，成为更懂你的智能助手！**

⭐ 如果这个项目对你有帮助，请给个 Star 支持！

</div>