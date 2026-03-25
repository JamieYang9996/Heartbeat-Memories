# HBM (Humanized Brain Memory) - OpenClaw Skill

<div align="center">

![HBM Logo](https://img.shields.io/badge/HBM-Humanized%20Brain%20Memory-blue)
![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

**完全本地化的长期记忆系统**，让你的 OpenClaw 记住一切重要对话、目标、经验和情感。

</div>

> **📝 使用前注意**: 本项目中的 GitHub 链接包含占位符 `OpenClaw-CN`。  
> 发布前请替换为自己的 GitHub 用户名，或 Fork 后修改脚本中的仓库地址。

## 🎯 核心理念

> **"让 AI 真正理解你，记住你，成为更懂你的智能助手"**

传统 AI 对话机器人每次会话都是"从零开始"，无法记住之前的对话、目标和经验。HBM 解决了这个问题，通过五大记忆库 + 语义搜索 + 情感交互，让 OpenClaw 拥有真正的长期记忆。

## ✨ 核心特性

### 🧠 五大记忆库系统
| 记忆库 | 功能 | 示例 |
|--------|------|------|
| **目标记忆库** | 追踪用户目标（P0/P1/P2优先级） | 学习 Python、项目开发、技能提升 |
| **经验记忆库** | 记录技术问题和解决方案 | Bug 修复、配置优化、最佳实践 |
| **情感记忆库** | 分析用户情绪和习惯偏好 | 高兴/平静/疑惑/成就等情绪记录 |
| **会话记忆库** | 每日对话摘要（10:1压缩比） | 关键决策、待办事项、重要讨论 |
| **版本记忆库** | 系统变更历史记录 | 功能新增、配置变更、问题修复 |

### 🔍 智能检索能力
- **语义搜索**: 基于 ChromaDB 向量数据库，自然语言查询记忆
- **关键词检索**: 从 Markdown 文件快速查找相关信息
- **混合检索**: 向量 + 关键词结合，提升检索准确性
- **RAG 增强**: 检索增强生成，提升回答质量和相关性

### ❤️ 情感交互体验
- **心跳回忆**: 智能触发回忆对话，增强情感连接
- **情绪识别**: 自动分析用户情绪状态
- **习惯学习**: 记录用户偏好和工作习惯
- **敏感节日规避**: 尊重文化传统，规避清明节等敏感节日

### 🚀 技术优势
- **完全本地化**: 零 API Key、零 Token 消耗、完全离线运行
- **跨平台支持**: Windows (WSL/Git Bash)、Linux、macOS
- **易于集成**: 标准 OpenClaw Skill 格式，一键安装
- **可配置性强**: 所有功能都有开关控制，按需启用

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

### 🚀 一句话安装（推荐，像 agent-reach 一样简单）

#### 方案 A：复制给 AI 自动安装
```bash
# 复制这句话给你的 AI 助手（OpenClaw/Claude Code 等）：
帮我安装 HBM：https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py

# AI 会自动：
# 1. 下载最新代码
# 2. 安装到正确位置
# 3. 配置 Python 依赖
# 4. 初始化记忆系统
```

#### 方案 B：手动执行安装命令
```bash
# 一行命令自动完成所有步骤
curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/install_hbm.py | python3
```

#### 方案 C：GitHub 手动安装
```bash
# 1. 克隆仓库
git clone https://github.com/OpenClaw-CN/hbm-skill.git

# 2. 复制到技能目录
cp -r hbm-skill ~/.openclaw/skills/hbm

# 3. 初始化系统
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_init.py
```

### 🔄 一键更新
已经装过了？更新也是一句话：

```bash
# 复制给 AI 自动更新：
帮我更新 HBM：https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/update_hbm.py

# 或手动更新：
curl -s https://raw.githubusercontent.com/OpenClaw-CN/hbm-skill/main/scripts/update_hbm.py | python3
```

### 🩺 系统诊断
```bash
# 检查 HBM 系统状态
cd ~/.openclaw/skills/hbm && python3 scripts/hbm_doctor.py

# 或复制给 AI：
帮我检查 HBM：运行 hbm_doctor.py
```

## 🚀 快速开始

### 第一次使用
1. **安装完成**后，重启 OpenClaw
2. 在对话中使用触发词测试功能
3. HBM 会自动开始记录重要对话

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

## 🏗️ 系统架构

```
hbm-skill/
├── SKILL.md                    # OpenClaw Skill 描述文件
├── README.md                   # 项目说明文档
├── LICENSE                     # MIT 许可证
├── memory/                     # 五大记忆库模板
│   ├── 目标记忆库/GOALS_template.md
│   ├── 经验记忆库/TIPS_template.md
│   ├── 情感记忆库/DAILY_EMOTIONS_template.md
│   ├── 会话记忆库/YYYY-MM-DD_template.md
│   ├── 版本记忆库/CHANGELOG_template.md
│   └── 心跳回忆/心跳回忆机制.md
├── scripts/                    # 核心脚本
│   ├── hbm_init.py            # 初始化脚本
│   ├── local_memory_system_v2.py  # 语义搜索核心
│   ├── rag_system.py          # RAG 检索增强系统
│   └── log_compressor.py      # 日志压缩器
├── config/                     # 配置文件
│   └── hbm_config_template.json
├── models/                     # 向量模型（自动下载）
├── logs/                       # 系统日志
└── docs/                       # 详细文档
```

## ⚙️ 配置说明

主要配置文件: `config/hbm_config.json`

### 关键配置项
```json
{
  "向量检索配置": {
    "启用语义搜索": true,
    "向量模型": "all-MiniLM-L6-v2",
    "相似度阈值": 0.75
  },
  "RAG配置": {
    "开关控制": {
      "enable_limit_and_dedupe": false,
      "enable_cache": false,
      "enable_log_compression": true
    }
  },
  "心跳回忆配置": {
    "enabled": true,
    "daily_limit": 3,
    "avoid_sensitive_festivals": true
  }
}
```

### 环境变量
```bash
export HBM_ROOT="~/custom/path"      # 自定义 HBM 根目录
export HBM_DEBUG="true"              # 启用调试模式
export HF_ENDPOINT="镜像地址"        # 国内用户加速下载
```

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **启动时间** | 2-5秒 | 首次加载模型较慢，后续有缓存 |
| **检索速度** | <1秒 | 向量检索 + 关键词检索 |
| **存储占用** | ~100MB | 向量模型 80MB + 记忆库 |
| **内存占用** | 200-300MB | ChromaDB + 模型加载 |
| **兼容性** | 全平台 | Windows/Linux/macOS 测试通过 |

## 🔧 高级功能

### RAG 系统优化
- **Token 限制和去重**: 防止回答过长（默认关闭）
- **内存缓存**: 提升检索速度（默认关闭）
- **日志压缩**: 按月自动压缩日志（保留最近一个月详细版）

### 自定义扩展
```python
# 扩展新的记忆库类型
# 修改 scripts/local_memory_system_v2.py

# 自定义触发逻辑
# 修改 memory/心跳回忆/心跳回忆机制.md
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

## 🤝 贡献指南

### 提交 Issue
1. 描述清晰的问题现象
2. 提供复现步骤
3. 附上相关日志和配置

### 提交 Pull Request
1. Fork 本仓库
2. 创建功能分支
3. 提交清晰的 commit 信息
4. 更新相关文档

### 开发环境设置
```bash
# 1. 克隆仓库
git clone https://github.com/[你的用户名]/hbm-skill.git

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 或 venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements-dev.txt

# 4. 运行测试
pytest tests/
```

## 📁 文件说明

| 文件 | 用途 | 重要性 |
|------|------|--------|
| `SKILL.md` | OpenClaw Skill 入口文件 | ⭐⭐⭐⭐⭐ |
| `scripts/hbm_init.py` | 初始化脚本 | ⭐⭐⭐⭐⭐ |
| `scripts/local_memory_system_v2.py` | 语义搜索核心 | ⭐⭐⭐⭐⭐ |
| `memory/*_template.md` | 记忆库模板 | ⭐⭐⭐⭐ |
| `config/hbm_config_template.json` | 配置模板 | ⭐⭐⭐⭐ |
| `docs/` | 详细文档 | ⭐⭐⭐ |

## 📈 路线图

### v1.0 (当前)
- ✅ 五大记忆库基础功能
- ✅ 语义搜索和向量检索
- ✅ 心跳回忆情感交互
- ✅ RAG 检索增强
- ✅ 跨平台支持

### v1.1 (规划中)
- 🔄 图形化配置界面
- 🔄 记忆库导入/导出功能
- 🔄 多用户支持
- 🔄 云端同步选项

### v2.0 (未来)
- 🔄 独立情感交互插件
- 🔄 多 AI 系统适配
- 🔄 社区记忆共享
- 🔄 高级分析报表

## 📚 相关资源

### 官方文档
- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Skill 开发指南](https://docs.openclaw.ai/skills)
- [ChromaDB 文档](https://docs.trychroma.com)

### 学习资源
- [HBM 使用教程视频](https://youtube.com/playlist?list=...) (计划中)
- [社区讨论区](https://discord.com/invite/clawd)
- [GitHub Discussions](https://github.com/[你的用户名]/hbm-skill/discussions)

### 类似项目
- [OpenAI Memory](https://openai.com/blog/memory) - 云端记忆服务
- [MemGPT](https://memgpt.ai) - 大语言模型记忆系统
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/) - 开发框架记忆模块

## 📄 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有贡献者和用户的支持！

特别感谢：
- **OpenClaw 团队** 创造了优秀的 AI 助手平台
- **ChromaDB 团队** 提供强大的向量数据库
- **Sentence Transformers 社区** 提供高质量的文本向量化模型
- **所有测试用户** 的宝贵反馈和建议

---

<div align="center">

**让 OpenClaw 真正拥有长期记忆，成为更懂你的智能助手！**

⭐ 如果这个项目对你有帮助，请给个 Star 支持！

</div>