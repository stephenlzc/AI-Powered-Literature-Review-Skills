# AGENTS.md - Literature Survey Skill

## 项目概述

本项目是一个 **Kimi CLI Skill**（技能插件），名为 `literature-survey`，用于帮助用户进行系统性的学术文献回顾（Literature Survey）。

**版本**: 2.1.0 (简化版)  
**最后更新**: 2024-03

### 核心特性

- **8阶段工作流**：完整的文献调研流程（简化执行版）
- **浏览器自动化**：无需API配置，直接访问数据库
- **多数据库支持**：CNKI、Web of Science、ScienceDirect、PubMed
- **结构化输出**：GB/T 7714-2015引文 + 标题 + 摘要的Markdown文档
- **综述生成**：自动生成结构化的文献综述

---

## 技术栈

- **语言**: Python 3.8+
- **架构**: 顺序执行工作流
- **数据库访问**: 浏览器自动化（Playwright）
- **外部依赖**:
  - Kimi CLI 的 `browser` skill
  - Kimi CLI 的 `docx` skill（可选）

---

## 项目结构

```
literature-survey/
├── SKILL.md                          # Skill 定义文件（主入口）
├── AGENTS.md                         # 本文件
├── README.md                         # 项目说明文档
│
├── agents/                           # Agent 模板目录
│   ├── explore-agent.md              # 搜索 Agent 模板
│   ├── verify-agent.md               # 验证 Agent 模板
│   ├── synthesize-agent.md           # 综述 Agent 模板
│   └── orchestrator.md               # 协调器 Agent 模板
│
├── references/                       # 参考资料文档
│   ├── cnki-guide.md                 # CNKI 检索详细指南
│   ├── database-access.md            # 各数据库访问指南
│   └── gb-t-7714-2015.md             # GB/T 7714-2015 引用格式规范
│
└── assets/                           # 资源目录（预留）
```

---

## 8阶段工作流

### Phase 0: Session Log（会话管理）

**目标**：创建会话目录，记录工作进度，支持中断续传

**目录结构**：
```
sessions/{YYYYMMDD}_{topic_short}/
├── session_log.md              # 工作日志
├── metadata.json               # 会话元数据
├── papers_raw.json             # 原始检索结果
├── papers_deduplicated.json    # 去重后文献
└── output/
    ├── references.md           # 文献清单（含摘要）
    └── literature_review.md    # 最终综述
```

**输出**:
- `sessions/{session_id}/session_log.md`
- `sessions/{session_id}/metadata.json`

---

### Phase 1: Query Analysis（查询分析）

**目标**：从用户输入提取核心概念，生成中英文检索策略

**步骤**：
1. **识别核心概念**
   - 研究主题（Topic）
   - 研究方法（Method）
   - 研究对象（Object）

2. **生成中英文关键词**

   | 类别 | 中文关键词 | 英文关键词 |
   |------|-----------|-----------|
   | 核心概念 | 深度学习 | deep learning |
   | 同义词扩展 | 深度神经网络 | deep neural network |

3. **构建检索表达式**

   **CNKI检索式**：
   ```
   SU=('深度学习'+'深度神经网络')*('医学图像'+'医学影像')
   ```
   
   **WOS检索式**：
   ```
   ("deep learning" OR "deep neural network") AND ("medical imaging")
   ```

---

### Phase 2: Parallel Search（并行检索）

**目标**：通过浏览器自动化在多个数据库执行检索

**核心数据库**（无需API）：

| 数据库 | 优先级 | 访问方式 |
|--------|--------|----------|
| CNKI | 1 | 浏览器访问高级检索页面 |
| Web of Science | 2 | 浏览器访问检索页面 |
| ScienceDirect | 3 | 浏览器访问检索页面 |
| PubMed | 4 | 网页搜索 + 浏览器访问 |
| Google Scholar | 5 | 网页搜索 |

**检索执行**（使用Playwright）：
1. 使用 `browser_navigate` 访问数据库检索页面
2. 填充检索式，执行搜索
3. 提取前50条结果
4. 保存到 `papers_raw.json`

**数据模型**：
```json
{
  "source_db": "cnki",
  "title": "文献标题",
  "authors": ["作者1", "作者2"],
  "journal": "期刊名称",
  "year": 2023,
  "volume": "46",
  "issue": "5",
  "pages": "1023-1035",
  "doi": "10.xxxx",
  "abstract": "摘要内容...",
  "keywords": ["关键词1", "关键词2"],
  "url": "原文链接"
}
```

---

### Phase 3: Deduplication（去重筛选）

**目标**：合并多源结果，去除重复

**简化去重策略**：
1. **DOI精确匹配** - 相同DOI视为重复
2. **标题相似度** - Levenshtein距离 > 0.85 视为重复
3. **保留规则** - 保留信息更完整的记录

**筛选条件**：
- 时间范围：近10年优先
- 来源质量：优先核心期刊
- 最终数量：中英文各15-25篇，总计30-50篇

---

### Phase 4: Verification（基础验证）

**目标**：确保元数据完整性，过滤明显错误

**验证内容**：
1. **元数据完整性** - 确保标题、作者、期刊、年份存在
2. **DOI格式校验** - 检查DOI格式有效性
3. **错误过滤** - 排除标题为"无"或作者缺失的记录

**验证状态**：
- VERIFIED: 元数据完整
- INCOMPLETE: 部分缺失
- EXCLUDED: 已过滤

---

### Phase 5: Data Export（数据导出）

**目标**：导出文献信息到Markdown文件

**输出文件**：`output/references.md`

**文件格式**：
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

---

### Phase 6: Citation Format（引用格式化）

**目标**：生成GB/T 7714-2015格式引文

**中文期刊格式**：
```
[C1] 张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.
```

**英文期刊格式**：
```
[E1] Smith J, Johnson K, Lee M. Deep learning for medical image analysis[J]. Nature Medicine, 2022, 28(8): 1500-1510. DOI:10.1038/s41591-022-01900-0.
```

**会议论文格式**：
```
[E2] Wang L, Chen X. A novel approach[C]//Proceedings of CVPR. 2023: 1234-1242.
```

---

### Phase 7: Synthesis（综述生成）

**目标**：撰写结构化的文献综述

**综述结构**：
```markdown
# 文献回顾：[研究主题]

## 1 引言
### 1.1 研究背景
### 1.2 检索策略
- 数据库：CNKI、Web of Science、ScienceDirect
- 检索式：...
- 时间范围：2014-2024
- 最终纳入：中文XX篇，英文XX篇

## 2 国内研究现状（中文文献）
### 2.1 技术研究进展
### 2.2 应用现状分析

## 3 国外研究现状（英文文献）
### 3.1 理论研究
### 3.2 临床应用

## 4 讨论
### 4.1 国内外对比
### 4.2 研究趋势与空白

## 5 结论

## 参考文献
[C1] ...
[C2] ...
[E1] ...
```

**写作原则**：
- 按主题分类，避免简单罗列
- 建立文献间的逻辑联系
- 体现批判性思维
- 使用交叉引用 `[C1]`、`[E1]`

---

## 数据库访问指南

### CNKI

**访问地址**：`https://kns.cnki.net/kns8/AdvSearch`

**字段代码**：
| 代码 | 含义 |
|------|------|
| SU | 主题 |
| TI | 篇名 |
| KY | 关键词 |
| TKA | 篇关摘 |

**来源筛选**：CSSCI、北大核心、CSCD

### Web of Science

**访问地址**：`https://www.webofscience.com/wos/woscc/advanced-search`

**常用字段**：
- TS=Topic
- TI=Title
- AB=Abstract

### ScienceDirect

**访问地址**：`https://www.sciencedirect.com/search`

---

## 输出文件说明

| 文件 | 路径 | 内容 |
|------|------|------|
| 文献清单 | `output/references.md` | 完整文献信息（含摘要） |
| 综述文档 | `output/literature_review.md` | 结构化综述 |
| 引文列表 | `output/gb7714_citations.txt` | GB/T格式引文 |

---

## 代码规范

### 命名规范
- 类名: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_CASE`

### 文献编号
- **中文文献**: 以 `C` 开头（C1, C2, C3...）
- **英文文献**: 以 `E` 开头（E1, E2, E3...）

### 注释语言
- 中文注释

---

## 使用示例

**用户请求**：帮我做一个关于"深度学习在肺癌早期诊断中的应用"的文献回顾

**执行流程**：
1. **Phase 1**: 生成检索策略
   - CNKI: SU=('深度学习'+'神经网络')*('肺癌'+'肺结节')*('诊断')
   - WOS: ("deep learning") AND ("lung cancer") AND ("diagnosis")

2. **Phase 2**: 并行检索
   - 访问CNKI高级检索页面，提取50条结果
   - 访问WOS检索页面，提取50条结果
   - 访问ScienceDirect，提取50条结果

3. **Phase 3**: 去重筛选
   - 合并结果，按标题相似度去重
   - 保留中英文各20篇

4. **Phase 4**: 基础验证
   - 检查元数据完整性
   - 过滤错误记录

5. **Phase 5**: 导出数据
   - 生成 `references.md`

6. **Phase 6**: 格式化引文
   - 生成GB/T 7714-2015格式

7. **Phase 7**: 生成综述
   - 生成 `literature_review.md`

---

## 依赖 Skills

- **browser** - 数据库检索自动化
- **docx** - 生成Word格式综述（可选）
- **web_search** - 辅助获取文献信息

---

## 修改历史

### v2.1.0 (2024-03) - 简化版
- 移除API配置要求
- 改用浏览器自动化访问数据库
- 简化去重/验证流程
- 输出改为Markdown格式（含摘要）
- 保留8阶段工作流框架

### v2.0.0 (2024-01)
- 重构为8阶段工作流
- 引入Agent Swarm架构
- 新增引用验证机制
- 新增多数据库API支持

### v1.0.0 (2023)
- 初始版本
