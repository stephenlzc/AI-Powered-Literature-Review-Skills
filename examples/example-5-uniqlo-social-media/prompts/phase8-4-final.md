# Phase 8.4: Final - 最终润色与定稿Prompt

## 用途
根据审查报告修订并生成最终版本，添加摘要和关键词

---

## Prompt

```
You are tasked with finalizing a literature review article based on a draft and review feedback.

Input materials:
<draft>
{{在此处插入Phase 8.2生成的综述初稿}}
</draft>

<review_report>
{{在此处插入Phase 8.3生成的审查报告}}
</review_report>

<research_topic>
人工智能在教育评估中的应用
</research_topic>

Finalization steps:

1. ADDRESS REVIEW FEEDBACK:
   - Fix all CRITICAL issues identified in the review
   - Address HIGH priority suggestions
   - Consider MEDIUM priority improvements if time permits

2. STRUCTURE AND FORMATTING:
   - Ensure proper Markdown formatting
   - Apply consistent heading levels (# Title, ## Section, ### Subsection)
   - Check that all citations use format ([X](url))
   - Verify all URLs are valid

3. CONTENT REFINEMENT:
   - Strengthen weak arguments
   - Add missing citations
   - Improve transitions between sections
   - Ensure critical analysis is present throughout
   - Balance coverage across topics

4. WRITE ABSTRACT (200-300 words):
   Structure:
   - Background (1-2 sentences): Context and importance
   - Objective (1 sentence): Purpose of the review
   - Methods (1-2 sentences): Search strategy and inclusion criteria
   - Results (2-3 sentences): Main findings and themes
   - Conclusion (1-2 sentences): Key implications

5. SELECT KEYWORDS (5-8 keywords):
   - Include main research topics
   - Include key methods/technologies
   - Include application domains
   - Separate with semicolons

6. COMPILE REFERENCES:
   - Convert in-text citations to GB/T 7714-2015 format
   - Sort by citation number ([C1], [C2]..., [E1], [E2]...)
   - Ensure all cited papers are in the reference list

7. FINAL POLISH:
   - Proofread for spelling and grammar
   - Check for consistent terminology
   - Ensure academic tone throughout
   - Verify word count (target: 3000-5000 words excluding references)

Output format:

```markdown
# [Research Topic]: A Literature Review

## Abstract

[200-300 word abstract]

**Keywords**: keyword1; keyword2; keyword3; keyword4; keyword5

---

[Main content with all revisions applied]

---

## References

[C1] ...
[C2] ...
[E1] ...
...
```

Requirements:
- Output ONLY the finalized review in Markdown
- No XML tags
- No meta-commentary about the revision process
- Ready for direct use or submission
```

---

## 预期输出格式

```markdown
# 人工智能在教育评估中的应用：文献综述

## 摘要

随着人工智能技术的快速发展，教育评估领域正经历深刻的数字化变革。本研究旨在系统梳理人工智能在教育评估中的应用现状，分析研究热点与发展趋势。通过检索CNKI、Web of Science、ScienceDirect等数据库，纳入2018-2023年间发表的相关文献40篇进行系统性分析。研究发现，自动化评分、学习过程评估和能力诊断是人工智能在教育评估中的三大主要应用场景；深度学习、自然语言处理和学习分析是核心技术方法；智能评估系统在提高评估效率和客观性方面展现出优势，但仍面临可解释性、公平性和隐私保护等挑战。未来研究应重点关注可解释AI的应用、多模态数据整合以及人机协作评估模式的构建。

**关键词**：人工智能；教育评估；学习分析；自动评分；智能辅导系统；教育数据挖掘

---

## 1 引言

随着人工智能技术的快速发展，教育领域正经历深刻的数字化变革...

[正文内容与Phase 8.2类似，但已根据审查报告修正]

---

## 6 结论

人工智能为教育评估带来了深刻的变革机遇...

---

## 参考文献

### 中文文献

[C1] 张三, 李四. 基于深度学习的智能作文评分系统研究[J]. 教育研究, 2023, 44(3): 56-68.

[C2] 王五, 赵六. 智能教育评估系统的应用与挑战[J]. 开放教育研究, 2022, 28(4): 89-102.

[C3] 教育部. 深化新时代教育评价改革总体方案[EB/OL]. (2020-10-13). http://www.moe.gov.cn/...

...

### 英文文献

[E1] Smith J, Johnson K. AI-Driven Personalized Learning: A Systematic Review[J]. Computers & Education, 2022, 178: 104-120. DOI:10.1016/j.compedu.2021.104120.

[E2] Chen X, Li Y, Liu Z. Deep Learning for Educational Data Mining: A Survey[J]. IEEE Transactions on Learning Technologies, 2023, 16(2): 234-248. DOI:10.1109/TLT.2023.1234567.

...
```

---

## GB/T 7714-2015 引用格式说明

### 期刊论文
```
作者. 题名[J]. 刊名, 年, 卷(期): 起止页码. DOI:xxxxx.
```

### 英文期刊
```
Author AA, Author BB. Title of article[J]. Journal Name, Year, Vol(Issue): Pages. DOI:xxxxx.
```

### 专著
```
作者. 书名[M]. 出版地: 出版者, 出版年: 引用页码.
```

### 学位论文
```
作者. 题名[D]. 保存地: 保存单位, 年份.
```

### 电子文献
```
作者. 题名[EB/OL]. (发布日期)[引用日期]. 网址.
```

---

## 使用说明

1. 将初稿、审查报告插入对应位置
2. 运行定稿Prompt
3. 检查输出是否包含：
   - 完整的摘要（200-300字）
   - 5-8个关键词
   - 修正后的正文
   - GB/T 7714-2015格式的参考文献
4. 最终校对语言和格式
5. 保存为 `literature_review.md`

---

## 定稿检查清单

- [ ] 摘要结构完整（背景-目的-方法-结果-结论）
- [ ] 关键词5-8个，覆盖主题、方法、应用领域
- [ ] 所有CRITICAL问题已修复
- [ ] 引用格式统一为GB/T 7714-2015
- [ ] 正文字数3000-5000字（不含参考文献）
- [ ] 中英文文献编号正确（C开头、E开头）
- [ ] 无拼写和语法错误
- [ ] 学术语言规范一致
