# Heartbeat-Memories Skill 版本更新日志

## v1.0.0 (2026-03-25)

### 🎉 初始版本发布

#### 核心功能
- ✅ **五大记忆库系统**：目标、经验、情感、会话、版本记忆库
- ✅ **语义搜索**：基于 ChromaDB 的向量检索
- ✅ **心跳回忆**：智能情感交互机制
- ✅ **RAG 增强**：检索增强生成系统
- ✅ **完全本地化**：零 API Key，零 Token 消耗

#### 安装体验
- ✅ **一句话安装**：复制命令给 AI 自动安装
- ✅ **一键更新**：同样的方式更新系统
- ✅ **系统诊断**：`hbm_doctor.py` 诊断工具
- ✅ **跨平台支持**：Windows/Linux/macOS 自动适配

#### 技术架构
- **向量模型**：all-MiniLM-L6-v2 (80MB，自动下载)
- **向量数据库**：ChromaDB + SQLite
- **文件格式**：Markdown 人类可读
- **配置管理**：JSON 配置文件，所有功能可开关

#### 文档完善
- `SKILL.md`：OpenClaw Skill 标准文档
- `README.md`：GitHub 项目主页
- `docs/install.md`：安装文档（复制给 AI）
- `docs/update.md`：更新文档
- `LICENSE`：MIT 许可证

### 📁 文件结构
```
Heartbeat-Memories/
├── SKILL.md                    # Skill 描述
├── README.md                   # 项目说明
├── CHANGELOG.md                # 版本日志
├── LICENSE                     # MIT 许可证
├── requirements.txt            # 依赖列表
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

### 🔧 技术规格
| 组件 | 规格 | 说明 |
|------|------|------|
| **Python** | 3.8+ | 必需版本 |
| **向量模型** | all-MiniLM-L6-v2 | 384 维度，80MB |
| **向量数据库** | ChromaDB 0.4.22+ | SQLite 后端 |
| **依赖包** | 3 个核心包 | chromadb, sentence-transformers, faiss-cpu |
| **存储占用** | ~100MB | 模型 80MB + 代码 20MB |
| **内存占用** | 200-300MB | 运行时占用 |

### 🚀 安装命令示例
```bash
# 一句话安装（复制给 AI）
帮我安装 Heartbeat-Memories：https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/install_hbm.py

# 手动安装
curl -s https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/install_hbm.py | python3
```

### 🔄 更新命令
```bash
# 一句话更新
帮我更新 Heartbeat-Memories：https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/update_hbm.py

# 手动更新
curl -s https://raw.githubusercontent.com/JamieYang9996/Heartbeat-Memories/main/scripts/update_hbm.py | python3
```

### 📝 使用触发词
- **中文**："记忆系统"、"帮我回忆"、"记下来"、"查看目标"
- **英文**："memory system"、"recall"、"save this"、"check goals"

---

**HBM v1.0.0 已就绪，具备与 agent-reach 同级别的安装便捷性和用户体验！**