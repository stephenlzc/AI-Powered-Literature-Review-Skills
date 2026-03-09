# 文献综述技能 - 使用示例

本目录包含使用示例，展示如何运用 literature-reviewer-skill 技能进行系统性文献回顾。

> **注意**: `examples/` 文件夹仅作为使用参考，不包含在 Skill 安装包中。

---

## 示例列表

| 示例 | 主题 | 学科领域 | 特点 |
|------|------|----------|------|
| [示例3](example-3-ai-education/) | 人工智能在教育评估中的应用 | 教育技术/计算机 | 技术导向、实证研究为主 |
| [示例4](example-4-carbon-policy/) | 中国碳中和政策体系研究 | 环境政策/经济学 | 政策导向、案例分析为主 |
| [示例5](example-5-uniqlo-social-media/) | 社会化媒体发展背景下优衣库的营销模式研究 | 市场营销/传播学 | 品牌营销、社交媒体分析、真实运行示例 |

> **示例5说明**: 本示例是真实运行生成的完整综述，约6000字，包含22篇中英文文献（中文10篇+英文12篇），展示从检索到综述生成的完整流程。

---

## 各阶段Prompt汇总

### Phase 1: Query Analysis - 查询分析

**用途**: AI智能分析研究主题，生成相关关键词和检索策略

```
You are tasked with generating relevant keywords or phrases for a given research direction.

The research direction is provided below:
<research_direction>
{{研究主题}}
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
```

---

### Phase 6: Paper Analysis - 单篇文献深度分析

**用途**: 对每篇文献进行深度分析，提取关键信息

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

---

以下是待分析的文献：

<articles>
{{文献列表}}
</articles>
```

---

### Phase 8.1: Outline - 生成综述大纲

**用途**: 基于文献主题聚类，构建逻辑清晰的综述结构

```
You are a renowned professor specializing in research methodology and academic writing.
Your task is to create a comprehensive, well-structured, and logically sound literature review outline.

Research topic:
<research_topic>
{{研究主题}}
</research_topic>

Collected literature analysis:
<collected_literature>
{{文献深度分析结果}}
</collected_literature>

Target language:
<language>
{{中文/英文}}
</language>

Instructions:

1. Analyze all collected papers and identify 3-5 main themes or research directions.

2. Structure the outline as follows:
   a) Introduction (background, objectives, search strategy)
   b) Theoretical Foundation and Methods
   c) Main Body (3-5 sections based on theme clustering)
   d) Discussion (comparative analysis, research gaps, trends)
   e) Conclusion
   f) References

3. For each main section, provide 3-5 specific subsections with clear titles.

4. Ensure logical flow:
   - From general to specific
   - From theory to application
   - From past to future directions

5. Allocate literature to appropriate sections.

6. Output format:
   # Literature Review Outline: [Research Topic]
   ## 1 Introduction
   ### 1.1 Research Background
   ...

7. Do not write any content for the sections, only the structure.

8. Ensure the outline can support a 3000-5000 word literature review.
```

---

### Phase 8.2: Writing - 撰写综述初稿

**用途**: 基于大纲撰写完整的综述内容，建立文献间的逻辑联系

```
You are a literature writing expert tasked with creating a high-quality, comprehensive academic literature review.

Input materials:
<outline>
{{综述大纲}}
</outline>

<collected_literature>
{{文献清单和摘要}}
</collected_literature>

<detailed_analysis>
{{单篇文献深度分析}}
</detailed_analysis>

Target language: {{中文/英文}}

Writing instructions:

1. Expand EACH section in the outline into detailed content:
   - Section 1 (Introduction): 300-500 words
   - Section 2 (Theoretical Foundation): 500-800 words
   - Section 3 (Main Body): 1500-2500 words
   - Section 4 (Discussion): 500-800 words
   - Section 5 (Conclusion): 200-300 words

2. For each subsection:
   - Start with a topic sentence summarizing the main point
   - Synthesize 3-5 relevant papers (do not summarize one by one)
   - Compare and contrast different studies
   - Highlight agreements and disagreements
   - Identify patterns and trends

3. Critical analysis requirements:
   - Evaluate methodological strengths and weaknesses
   - Point out inconsistencies or contradictions
   - Question assumptions and limitations
   - Suggest alternative interpretations

4. Citation format:
   - Use ([C1](url)), ([E1](url)) for in-text citations
   - Every claim should be supported by at least one citation
   - Group related citations: ([C1], [C2], [E1])

5. Writing style:
   - Academic and formal tone
   - Clear and concise sentences
   - Logical transitions between paragraphs
   - Avoid bullet points in main text (use prose)

6. Structure each paragraph:
   - Topic sentence
   - Evidence from literature (with citations)
   - Critical commentary
   - Transition to next point

7. Output the complete review in Markdown format without XML tags.

8. Do not include abstract or keywords yet (will be added in Phase 8.4).
```

---

### Phase 8.3: Review - 质量审查与评估

**用途**: 系统性审查综述质量，识别问题和改进点

```
You are an experienced academic review expert specializing in literature reviews.
Conduct a comprehensive, rigorous multi-dimensional assessment of the submitted literature review.

Materials to review:
<literature_review_draft>
{{综述初稿}}
</literature_review_draft>

<original_topic>
{{研究主题}}
</original_topic>

<collected_papers>
{{原始文献清单}}
</collected_papers>

Review criteria:

a) ACCURACY AND COMPREHENSIVENESS (Weight: 25%)
   Score: ___/10

b) LOGICAL ARGUMENTATION (Weight: 25%)
   Score: ___/10

c) LITERATURE CITATIONS (Weight: 20%)
   Score: ___/10

d) CRITICAL ANALYSIS (Weight: 15%)
   Score: ___/10

e) LANGUAGE AND STYLE (Weight: 10%)
   Score: ___/10

f) INNOVATION AND INSIGHT (Weight: 5%)
   Score: ___/10

Deliverables:

1. Overall Quality Score: ___/100

2. Detailed Assessment:
   <review>
   <major_strengths>[3-5 strengths]</major_strengths>
   <critical_issues>[Must fix]</critical_issues>
   <areas_for_improvement>[Suggestions]</areas_for_improvement>
   <missing_elements>[What's missing]</missing_elements>
   <specific_suggestions>[Actionable fixes]</specific_suggestions>
   <citation_issues>[Citation problems]</citation_issues>
   </review>

3. Revision Priority: CRITICAL / HIGH / MEDIUM
```

---

### Phase 8.4: Final - 最终润色与定稿

**用途**: 根据审查报告修订并生成最终版本，添加摘要和关键词

```
You are tasked with finalizing a literature review article based on a draft and review feedback.

Input materials:
<draft>
{{综述初稿}}
</draft>

<review_report>
{{审查报告}}
</review_report>

<research_topic>
{{研究主题}}
</research_topic>

Finalization steps:

1. ADDRESS REVIEW FEEDBACK:
   - Fix all CRITICAL issues
   - Address HIGH priority suggestions
   - Consider MEDIUM priority improvements

2. STRUCTURE AND FORMATTING:
   - Ensure proper Markdown formatting
   - Apply consistent heading levels
   - Check citation format ([X](url))

3. CONTENT REFINEMENT:
   - Strengthen weak arguments
   - Add missing citations
   - Improve transitions

4. WRITE ABSTRACT (200-300 words):
   - Background (1-2 sentences)
   - Objective (1 sentence)
   - Methods (1-2 sentences)
   - Results (2-3 sentences)
   - Conclusion (1-2 sentences)

5. SELECT KEYWORDS (5-8 keywords):
   - Include main research topics
   - Include key methods/technologies
   - Include application domains
   - Separate with semicolons

6. COMPILE REFERENCES:
   - Convert to GB/T 7714-2015 format
   - Sort by citation number ([C1], [C2]..., [E1], [E2]...)

7. FINAL POLISH:
   - Proofread for spelling and grammar
   - Check word count (3000-5000 words)

Output format:

# [Research Topic]: A Literature Review

## Abstract
[200-300 word abstract]

**Keywords**: keyword1; keyword2; keyword3...

---

[Main content with revisions]

---

## References

[C1] ...
[C2] ...
[E1] ...
```

Requirements:
- Output ONLY the finalized review in Markdown
- No XML tags
- No meta-commentary
- Ready for direct use
```

---

## 快速使用指南

### 1. 复制Prompt
从上方复制对应阶段的Prompt

### 2. 替换变量
将 `{{变量}}` 替换为实际内容，例如：
- `{{研究主题}}` → `深度学习在医学影像诊断中的应用`
- `{{文献列表}}` → 实际的文献数据

### 3. 执行工作流
按照 Phase 1 → 6 → 8.1 → 8.2 → 8.3 → 8.4 的顺序执行

### 4. 迭代优化
根据Phase 8.3的评分决定是否需要迭代：
- ≥85分：直接定稿
- 70-85分：根据建议修改后定稿
- <70分：返回对应阶段重写

---

## 文件命名规范

| 阶段 | 输出文件 | 说明 |
|------|----------|------|
| Phase 0 | `session_log.md` | 工作日志 |
| Phase 1 | `metadata.json` | 包含关键词和检索策略 |
| Phase 2-5 | `papers_raw.json`, `papers_deduplicated.json` | 文献数据 |
| Phase 6 | `papers_analysis.md` | 单篇文献深度分析 |
| Phase 8.1 | `outline.md` | 综述大纲 |
| Phase 8.2 | `draft.md` | 综述初稿 |
| Phase 8.3 | `review_report.md` | 质量审查报告 |
| Phase 8.4 | `literature_review.md` | **最终定稿** |

---

## 注意事项

1. **文献编号**: 中文以C开头（C1, C2...），英文以E开头（E1, E2...）
2. **引用格式**: 遵循GB/T 7714-2015标准
3. **字数要求**: 最终综述3000-5000字（不含参考文献）
4. **文献数量**: 中英文各15-25篇，总计30-50篇
