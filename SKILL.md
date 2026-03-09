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
Phase 6: Paper Analysis   → 单篇文献深度分析
Phase 7: Citation Format  → GB/T 7714-2015格式化
Phase 8: Synthesis        → 生成综述文档
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
├── papers_analysis.json    # 文献分析结果
└── output/
    ├── references.md       # 文献清单（含摘要）
    ├── papers_analysis.md  # 单篇文献分析
    └── literature_review.md # 最终综述
```

---

## Phase 1: Query Analysis（查询分析）

AI 智能分析研究主题，生成相关关键词和检索策略。

### AI 提示词模板

```
You are tasked with generating relevant keywords or phrases for a given research direction.

The research direction is provided below:
<research_direction>
{{用户输入的研究主题}}
</research_direction>

To complete this task:

1. Carefully analyze the provided research direction.
2. Identify core concepts, methods, techniques, or topics in this research area.
3. Generate 5 to 8 of the most relevant and representative keywords or phrases.
4. Ensure keywords are concise, typically 1-3 words each.
5. Make sure the keywords cover different aspects of the research direction.
6. Order the keywords by importance or relevance.
7. Separate keywords with English commas (,).
8. Do not include any explanations, descriptions, or additional text.
9. Provide keywords in both Chinese and English.

Present your result in the following format:

中文关键词：keyword1, keyword2, keyword3, ...
英文关键词：english_keyword1, english_keyword2, english_keyword3, ...

Example for "人工智能在医疗诊断中的应用":
中文关键词：人工智能, 医疗诊断, 机器学习, 深度学习, 医学影像, 辅助诊断, 疾病预测, 智能诊疗
英文关键词：artificial intelligence, medical diagnosis, machine learning, deep learning, medical imaging, computer-aided diagnosis, disease prediction, intelligent diagnosis
```

### 输出格式

```yaml
研究主题: "基于深度学习的医学图像诊断研究"

中文关键词:
  - 深度学习
  - 医学图像
  - 诊断
  - 神经网络
  - 计算机辅助诊断
  
英文关键词:
  - deep learning
  - medical imaging
  - diagnosis
  - neural network
  - computer-aided diagnosis

检索策略:
  CNKI: "SU=('深度学习'+'神经网络')*('医学图像'+'影像')*('诊断'+'辅助诊断')"
  WOS: "TS=((deep learning OR neural network) AND (medical imaging) AND (diagnosis))"
```

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
```

---

## Phase 6: Paper Analysis（单篇文献分析）

对每篇文献进行深度分析，提取关键信息。

### AI 提示词模板

```
You are an AI assistant tasked with analyzing and interpreting academic articles.

For each article, follow these steps:

1. Identify and summarize the main research question(s) and objective(s) of the article.
2. Describe the theoretical framework or model used in the study.
3. Summarize the research methodology and design employed.
4. Extract and summarize the key findings and conclusions.
5. Highlight any innovative aspects of the study and point out potential limitations.
6. Analyze how this article relates to other research in the field.
7. Identify any controversial points or unresolved issues mentioned in the article.
8. Identify any trends or emerging directions in the research field mentioned.

Present your analysis in the following structured format:

**文章[N]：[Article Title]**
**主要观点和结论**：[Summary of main points and conclusions]
**局限性**：[Discussion of limitations]
**争议点**：[Identified controversies or disputed points]
**研究内容缺陷**：[Areas not covered by the research]
**参考文献格式**：[GB/T 7714-2015 format for this paper]

Use "---" to separate each article analysis.

Ensure that you analyze and provide output for ALL articles. Do not omit any article from your analysis.
```

### 输出格式

```markdown
# 文献深度分析

---

**文章1：基于深度学习的医学图像诊断研究**

**主要观点和结论**：
本文提出了一种基于卷积神经网络的医学图像诊断方法，在肺结节检测任务上取得了95%的准确率。研究表明深度学习方法能够有效辅助医生进行病灶识别。

**局限性**：
1. 数据集规模相对较小，仅有1000例样本
2. 缺乏多中心验证
3. 模型对少见病例的泛化能力有待验证

**争议点**：
- 深度学习模型的"黑盒"特性与医疗可解释性需求的矛盾
- 辅助诊断系统的责任归属问题

**研究内容缺陷**：
- 未涉及模型的临床部署方案
- 缺少与现有商用系统的对比
- 未讨论数据隐私保护机制

**参考文献格式**：
张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.

---
```

---

## Phase 7: Citation Format（引用格式化）

生成GB/T 7714-2015格式引文。

**中文期刊格式**：
```
[C1] 张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.
```

**英文期刊格式**：
```
[E1] Smith J, Johnson K, Lee M. Deep learning for medical image analysis[J]. Nature Medicine, 2022, 28(8): 1500-1510. DOI:10.1038/s41591-022-01900-0.
```

---

## Phase 8: Synthesis（综述生成）

生成高质量结构化文献综述。

### Step 1: 生成综述大纲 (Outline)

**AI 提示词模板**：

```
You are a renowned professor specializing in research methodology and academic writing.
Your task is to create a comprehensive, well-structured, and logically sound literature review outline.

Research topic:
<research_topic>
{{研究主题}}
</research_topic>

Collected literature:
<collected_literature>
{{文献清单和分析}}
</collected_literature>

Target language:
<language>
{{中文/英文}}
</language>

Please follow these instructions:

1. Structure the outline as follows:
   a) Introduction
   b) Methodology
   c) Main body (3-5 sections based on topic clustering)
   d) Discussion
   e) Conclusion
   f) References

2. For each main section, provide 3-5 key points or subsections.

3. Ensure logical coherence between all sections.

4. Balance the content, giving appropriate weight to each aspect.

5. Use standard outline format with titles, subtitles, and bullet points.

6. Include innovative perspectives or organizational approaches.

7. Focus solely on creating the outline. Do not write content for the sections.

8. Present only the outline itself, without any introductory or concluding remarks.
```

### Step 2: 撰写综述 (Writing)

**AI 提示词模板**：

```
You are a literature writing expert tasked with creating a high-quality, comprehensive academic literature review.

1. Carefully read and analyze the provided outline.
2. Understand the main topics and subtopics.
3. Recognize the logical flow and structure.

Expand the content for each section:
- A summary of existing research
- Critical analysis of current studies
- Identification of research gaps
- Suggestions for new research directions

Conduct in-depth analysis:
- Compare and contrast different studies
- Evaluate strengths and weaknesses
- Analyze limitations in methods and results

Apply critical thinking:
- Identify unexplored aspects
- Point out controversial issues
- Assess applicability of frameworks

Construct a theoretical framework:
- Propose a framework explaining the field
- Explain how it integrates existing research

Suggest future research directions:
- Propose 3-5 valuable future directions
- Explain importance and potential contributions

Citation format: Use ([1](url)) for referencing literature to support each argument.

Write without using XML tags. The final product should be a cohesive, well-structured academic text.
```

### Step 3: 质量审查 (Review)

**AI 提示词模板**：

```
You are an experienced academic review expert specializing in literature reviews.
Your task is to conduct a comprehensive, rigorous multi-dimensional assessment.

Conduct a thorough review focusing on:

a) Accuracy and Comprehensiveness:
   - Verify accuracy of all information
   - Ensure coverage of all important research

b) Logical Argumentation:
   - Analyze argumentative structure
   - Check if points are adequately supported

c) Literature Citations:
   - Confirm citations are appropriate
   - Ensure cited literature is up-to-date

d) Article Structure:
   - Examine overall structure for logic
   - Ensure coherence between paragraphs

e) Language Expression:
   - Ensure clear, concise academic language
   - Check for grammatical errors

f) Innovation:
   - Determine if new insights are provided
   - Confirm valuable research directions

Provide assessment in this format:

<review>
<strengths>
[List main strengths]
</strengths>

<weaknesses>
[List weaknesses or areas for improvement]
</weaknesses>

<suggestions>
[Provide detailed, constructive suggestions]
</suggestions>
</review>
```

### Step 4: 最终润色 (Final)

**AI 提示词模板**：

```
You are tasked with finalizing a literature review article based on a reviewed draft.

Steps to finalize:

1. Formatting and Structure:
   - Use Markdown format
   - Apply appropriate heading levels
   - Include: Title, Abstract, Keywords, Introduction, Main Body, Conclusion, References

2. Content Refinement:
   - Identify areas needing improvement
   - Present comprehensive discussion
   - Maintain objective academic tone
   - Strengthen logical flow

3. Citations and References:
   - Use format ([1](url)) for in-text citations
   - Compile reference list in GB/T 7714-2015 format

4. Final Checks:
   - Proofread for errors
   - Verify citations
   - Ensure consistent academic style

5. Abstract and Keywords:
   - Write 200-300 word abstract
   - Provide 5-8 keywords

Output the finalized article in Markdown, free of XML tags.
```

### 最终输出格式

```markdown
# 基于深度学习的医学图像诊断研究文献综述

## 摘要

[200-300字的摘要，概括研究背景、方法、主要发现]

**关键词**：深度学习；医学图像；诊断；人工智能；计算机辅助诊断

---

## 1 引言

### 1.1 研究背景
[背景介绍]

### 1.2 研究目的与范围
[说明综述目的]

### 1.3 检索策略
- 数据库：CNKI、Web of Science、ScienceDirect、PubMed
- 检索式：...
- 时间范围：2014-2024
- 最终纳入：中文XX篇，英文XX篇

---

## 2 理论基础与技术方法

### 2.1 深度学习基础
[理论基础介绍]

### 2.2 医学图像处理技术
[技术方法综述]

---

## 3 国内研究现状

### 3.1 算法研究进展
[引用C1, C2...]

### 3.2 临床应用探索
[引用C3, C4...]

---

## 4 国外研究现状

### 4.1 前沿算法发展
[引用E1, E2...]

### 4.2 临床转化研究
[引用E3, E4...]

---

## 5 讨论

### 5.1 国内外研究对比
[对比分析]

### 5.2 研究空白与机遇
[Gap分析]

### 5.3 未来研究方向
[趋势预测]

---

## 6 结论

[总结主要发现]

---

## 参考文献

[C1] 张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035.

[E1] Smith J, Johnson K, Lee M. Deep learning for medical image analysis[J]. Nature Medicine, 2022, 28(8): 1500-1510.

...
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
| `papers_analysis.md` | 单篇文献深度分析 | 理解每篇文献 |
| `literature_review.md` | 结构化综述（含摘要、关键词） | 直接使用 |
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
1. AI生成中英文关键词和检索策略
2. 并行检索 CNKI、WOS、ScienceDirect、PubMed
3. 整理去重，保留中英文各20篇
4. 导出 `references.md`
5. **单篇文献深度分析** → `papers_analysis.md`
6. 生成综述大纲 → 撰写 → 审查 → 润色 → `literature_review.md`
7. 输出 GB/T 7714-2015 格式引文

---

## 触发关键词

- "文献回顾"
- "文献综述"
- "帮我找文献"
- "中英文文献搜索"
- "写综述"
- "literature survey"
- "systematic review"
