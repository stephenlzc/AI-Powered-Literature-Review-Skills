# Literature Survey Skill

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Kimi-Skill-green.svg" alt="Kimi Skill">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/GB/T%207714-2015-red.svg" alt="GB/T 7714-2015">
</p>

<p align="center">
  <b>系统性学术文献回顾（Literature Survey）Skill for Kimi CLI</b>
</p>

<p align="center">
  采用 8阶段工作流，浏览器自动化检索，支持 CNKI/WOS/ScienceDirect，零配置输出 GB/T 7714-2015 格式文献综述
</p>

---

## 📖 简介

**Literature Survey Skill** 是一个为 Kimi CLI 设计的 Skill 插件，用于帮助用户进行系统性的学术文献回顾。

### 核心优势

- 🚀 **8阶段工作流**：从查询分析到综述生成的完整流程
- 🌐 **浏览器自动化**：无需API配置，直接访问学术数据库
- ✅ **多数据库支持**：CNKI、Web of Science、ScienceDirect、PubMed
- 📚 **结构化输出**：GB/T 7714-2015引文 + 标题 + 摘要的Markdown文档
- 🔄 **中断续传**：支持会话保存和恢复

---

## ✨ 功能特性

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| 🔍 查询分析 | 自动生成中英文检索策略 | ✅ 可用 |
| 🌏 中文文献检索 | CNKI 浏览器自动化 | ✅ 可用 |
| 🌍 英文文献检索 | WOS/ScienceDirect/PubMed | ✅ 可用 |
| 🔄 智能去重 | 标题相似度匹配 | ✅ 可用 |
| ✅ 元数据验证 | 基础完整性校验 | ✅ 可用 |
| 📝 引用格式化 | GB/T 7714-2015 | ✅ 可用 |
| 📄 数据导出 | Markdown格式（含摘要） | ✅ 可用 |
| 📝 综述生成 | 结构化文献综述 | ✅ 可用 |

---

## 🔄 8阶段工作流

```mermaid
flowchart TD
    P0[Phase 0: Session Log<br/>会话管理] --> P1
    P1[Phase 1: Query Analysis<br/>查询分析] --> P2
    P2[Phase 2: Parallel Search<br/>并行检索] --> P3
    P3[Phase 3: Deduplication<br/>去重筛选] --> P4
    P4[Phase 4: Verification<br/>基础验证] --> P5
    P5[Phase 5: Data Export<br/>数据导出] --> P6
    P6[Phase 6: Citation Format<br/>引用格式化] --> P7
    P7[Phase 7: Synthesis<br/>综述生成] --> END[完成]
    
    P2 -.-> CNKI[(CNKI)]
    P2 -.-> WOS[(Web of Science)]
    P2 -.-> SD[(ScienceDirect)]
    P2 -.-> PM[(PubMed)]
```

### 各阶段详细说明

| 阶段 | 名称 | 主要任务 | 输出 |
|------|------|---------|------|
| 0 | Session Log | 创建会话目录，记录工作进度 | `session_log.md` |
| 1 | Query Analysis | 关键词提取、检索式构建 | `keywords.json`, `queries.json` |
| 2 | Parallel Search | 浏览器访问各数据库检索 | `papers_raw.json` |
| 3 | Deduplication | 去重、筛选 | `papers_deduplicated.json` |
| 4 | Verification | 元数据完整性校验 | 验证后的文献列表 |
| 5 | Data Export | 导出文献信息到Markdown | `references.md` |
| 6 | Citation Format | GB/T 7714-2015格式化 | 格式化的引文列表 |
| 7 | Synthesis | 生成结构化综述 | `literature_review.md` |

---

## 🚀 快速开始

### 安装

#### 方式一：自然语言安装（推荐）

如果你使用 **Kimi CLI**、**OpenCode**、**Claude Code** 等 AI 编程工具，可以直接用自然语言安装：

> 💬 *"请帮我安装 Literature Survey Skill，从 https://github.com/stephenlzc/AI-Powered-Literature-Review-Skills 克隆到 skills 目录"*

AI 助手会自动完成克隆和配置。

#### 方式二：手动安装

1. 将本 Skill 复制到 Kimi CLI 的 skills 目录：

```bash
cd ~/.kimi/skills  # 或你的 Kimi CLI skills 目录
git clone https://github.com/stephenlzc/AI-Powered-Literature-Review-Skills.git literature-survey
```

2. 完成！无需额外配置，直接使用。

### 使用方法

在 Kimi CLI 中输入触发关键词：

```
/ 文献回顾 基于深度学习的医学图像诊断研究
```

或：

```
/ 帮我找文献 Transformer模型在自然语言处理中的应用
```

---

## 📁 项目结构

```
literature-survey/
├── SKILL.md                          # Skill 主入口（简化版）
├── README.md                         # 本文件
├── AGENTS.md                         # 项目架构说明
│
├── agents/                           # Agent 模板
│   ├── explore-agent.md              # 搜索 Agent
│   ├── verify-agent.md               # 验证 Agent
│   ├── synthesize-agent.md           # 综述 Agent
│   └── orchestrator.md               # 协调器 Agent
│
├── references/                       # 参考资料
│   ├── cnki-guide.md                 # CNKI检索指南
│   ├── database-access.md            # 数据库访问指南
│   └── gb-t-7714-2015.md             # GB/T 7714-2015引用格式规范
│
└── sessions/                         # 会话目录（运行时生成）
    └── {YYYYMMDD}_{topic}/
        ├── session_log.md            # 工作日志
        ├── metadata.json             # 会话元数据
        ├── papers_raw.json           # 原始检索结果
        ├── papers_deduplicated.json  # 去重后文献
        └── output/
            ├── references.md         # 文献清单（含摘要）
            └── literature_review.md  # 最终综述
```

---

## 🌐 支持的数据库

| 数据库 | 类型 | 访问方式 |
|--------|------|----------|
| CNKI 中国知网 | 全文 | 浏览器自动化 |
| Web of Science | 引文索引 | 浏览器自动化 |
| ScienceDirect | 全文 | 浏览器自动化 |
| PubMed | 生物医学 | 浏览器自动化 |
| Google Scholar | 学术搜索 | 网页搜索 |

**无需API配置**，直接通过浏览器访问数据库检索页面。

---

## 📝 输出格式

### 文献清单 (references.md)

包含完整文献信息：

```markdown
# 文献清单

## 中文文献

### C1
- **标题**: 基于深度学习的医学图像诊断研究
- **作者**: 张三, 李四, 王五
- **期刊**: 计算机学报
- **年份**: 2023
- **卷期**: 46(5): 1023-1035
- **DOI**: 10.xxxx
- **摘要**: 本文研究了...
- **来源**: CNKI

## 英文文献

### E1
- **Title**: Deep Learning for Medical Image Analysis
- **Authors**: Smith J, Johnson K
- **Journal**: Nature Medicine
- **Year**: 2022
- **DOI**: 10.1038/xxxxx
- **Abstract**: This study presents...
- **Source**: ScienceDirect
```

### GB/T 7714-2015 引用格式

**中文期刊**：
```
[C1] 张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.
```

**英文期刊**：
```
[E1] Smith J, Johnson K, Lee M. Deep learning for medical image analysis[J]. Nature Medicine, 2022, 28(8): 1500-1510. DOI:10.1038/s41591-022-01900-0.
```

### 综述文档 (literature_review.md)

结构化综述，包含：
1. 引言（研究背景、检索策略）
2. 国内研究现状（中文文献）
3. 国外研究现状（英文文献）
4. 讨论（对比分析、研究趋势）
5. 结论
6. 参考文献

---

## 📚 参考资料

- `references/cnki-guide.md` - CNKI 高级检索详细指南
- `references/database-access.md` - 各数据库访问指南
- `references/gb-t-7714-2015.md` - GB/T 7714-2015 引用格式规范

---

## 🗺️ 版本历史

### v2.1.0 (2024-03) - 简化版

- ✅ 移除API配置要求
- ✅ 改用浏览器自动化访问数据库
- ✅ 简化去重/验证流程
- ✅ 输出改为Markdown格式（含摘要）
- ✅ 保留8阶段工作流框架

### v2.0.0 (2024-01)

- 重构为8阶段工作流
- 引入Agent Swarm架构
- 新增引用验证机制
- 新增多数据库API支持

### v1.0.0 (2023)

- 初始版本

---

## 🤝 致谢

本项目在开发过程中参考和整合了以下优秀开源项目的思路和设计：

| 项目 | 核心贡献 |
|------|---------|
| [flonat/claude-research](https://github.com/flonat/claude-research) | 8阶段工作流、引用验证、Session Log |
| [openclaw/skills](https://github.com/openclaw/skills) | 多数据库搜索策略、Agent设计模式 |
| [cookjohn/cnki-skills](https://github.com/cookjohn/cnki-skills) | CNKI自动化检索、Zotero导出 |
| [diegosouzapw/awesome-omni-skill](https://github.com/diegosouzapw/awesome-omni-skill) | 统一学术数据接口设计 |

---

## 📄 许可证

MIT License

Copyright (c) 2024 Literature Survey Skill Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<p align="center">
  Made with ❤️ for researchers
</p>
