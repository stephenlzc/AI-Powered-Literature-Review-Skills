---
name: literature-survey
description: |
  根据用户提供的论文主题，进行系统性中英文文献回顾（Literature Survey）。
  采用8阶段工作流，支持CNKI、Web of Science、ScienceDirect等主流数据库，
  无需API配置，通过浏览器自动化获取文献信息。
  输出包含GB/T 7714-2015引文、标题、摘要的Markdown文档。
  当用户提到"文献回顾"、"文献综述"、"帮我找文献"、"中英文文献搜索"、"写综述"等关键词时触发。
---

# 文献回顾（Literature Survey）

根据用户提供的论文主题，进行系统性的中英文文献检索、整理和综述撰写。
采用 **8阶段工作流**，无需API配置，通过浏览器自动化获取文献。

---

## 8阶段工作流（简化执行版）

```
Phase 0: Session Log      → 创建会话目录
Phase 1: Query Analysis   → 生成中英文检索策略  
Phase 2: Parallel Search  → 浏览器自动化检索
Phase 3: Deduplication    → 标题相似度去重
Phase 4: Verification     → 基础元数据校验
Phase 5: Data Export      → 导出文献信息
Phase 6: Citation Format  → GB/T 7714-2015格式化
Phase 7: Synthesis        → 生成综述文档
```

---

## Phase 0: Session Log（会话管理）

创建会话目录，记录工作进度。

**目录结构**：
```
sessions/{YYYYMMDD}_{topic_short}/
├── session_log.md          # 工作日志
├── metadata.json           # 会话元数据
├── papers_raw.json         # 原始检索结果
├── papers_deduplicated.json # 去重后文献
└── output/
    ├── references.md       # 文献清单（含摘要）
    └── literature_review.md # 最终综述
```

---

## Phase 1: Query Analysis（查询分析）

从用户输入提取核心概念，生成检索策略。

**输入示例**：
```
主题：基于深度学习的医学图像诊断研究
```

**输出检索策略**：

| 数据库 | 检索式 |
|--------|--------|
| CNKI | SU=('深度学习'+'深度神经网络')*('医学图像'+'医学影像')*('诊断'+'识别') AND CSSCI=1 |
| WOS | ("deep learning" OR "deep neural network") AND ("medical imaging" OR "medical image") AND ("diagnosis" OR "classification") |
| ScienceDirect | deep learning AND medical imaging AND diagnosis |

---

## Phase 2: Parallel Search（并行检索）

**核心数据库**（无需API，浏览器自动化）：

| 数据库 | 优先级 | 检索方式 |
|--------|--------|----------|
| CNKI | 1 | 浏览器访问高级检索页面 |
| Web of Science | 2 | 浏览器访问检索页面 |
| ScienceDirect | 3 | 浏览器访问检索页面 |
| PubMed | 4 | 网页搜索 + 浏览器访问 |
| Google Scholar | 5 | 网页搜索 |

**检索步骤**：
1. 使用 `browser_navigate` 访问各数据库检索页面
2. 填充检索式，执行搜索
3. 提取前50条结果的标题、作者、期刊、年份、DOI、摘要
4. 保存到 `papers_raw.json`

**字段提取**：
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

## Phase 3: Deduplication（去重筛选）

**简化去重策略**：

1. **DOI匹配** - 相同DOI视为重复
2. **标题相似度** - Levenshtein距离 > 0.85 视为重复
3. **保留规则** - 保留信息更完整的记录

**筛选条件**：
- 时间：近10年优先
- 来源：优先保留核心期刊/高质量来源
- 数量：中英文各15-25篇，总计30-50篇

---

## Phase 4: Verification（基础验证）

简化验证流程：

1. **元数据完整性检查** - 确保标题、作者、期刊、年份存在
2. **DOI格式校验** - 检查DOI格式有效性
3. **明显错误过滤** - 排除标题为"无"或作者缺失的记录

---

## Phase 5: Data Export（数据导出）

导出文献信息到Markdown文件。

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

### C2
...

## 英文文献

### E1
- **Title**: Deep Learning for Medical Image Analysis
- **Authors**: Smith J, Johnson K, Lee M
- **Journal**: Nature Medicine
- **Year**: 2022
- **Volume/Issue**: 28(8): 1500-1510
- **DOI**: 10.1038/s41591-022-01900-0
- **Abstract**: This study presents...
- **Source**: ScienceDirect

### E2
...
```

---

## Phase 6: Citation Format（引用格式化）

生成GB/T 7714-2015格式引文。

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

## Phase 7: Synthesis（综述生成）

生成结构化文献综述文档。

**文档结构**：
```markdown
# 文献回顾：基于深度学习的医学图像诊断研究

## 1 引言
### 1.1 研究背景
### 1.2 检索策略
- 数据库：CNKI、Web of Science、ScienceDirect
- 检索式：...
- 时间范围：2014-2024
- 最终纳入：中文XX篇，英文XX篇

## 2 国内研究现状
### 2.1 技术研究进展
### 2.2 应用现状分析

## 3 国外研究现状  
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
- SO=Source

### ScienceDirect

**访问地址**：`https://www.sciencedirect.com/search`

---

## 输出文件说明

| 文件 | 内容 | 用途 |
|------|------|------|
| `references.md` | 完整文献清单（含摘要） | 文献查阅 |
| `literature_review.md` | 结构化综述 | 直接使用 |
| `gb7714_citations.txt` | GB/T格式引文列表 | 复制到论文 |

---

## 依赖 Skills

- **docx** - 生成Word格式综述（可选）
- **web_search** - 辅助获取文献信息
- **browser** - 数据库检索自动化

---

## 使用示例

**用户**：帮我做一个关于"深度学习在肺癌早期诊断中的应用"的文献回顾

**执行流程**：
1. 生成中英文检索策略
2. 并行检索 CNKI、WOS、ScienceDirect、PubMed
3. 整理去重，保留中英文各20篇
4. 导出 `references.md`（含摘要）
5. 生成 `literature_review.md`（结构化综述）
6. 输出 GB/T 7714-2015 格式引文

---

## 触发关键词

- "文献回顾"
- "文献综述"
- "帮我找文献"
- "中英文文献搜索"
- "写综述"
- "literature survey"
- "systematic review"
