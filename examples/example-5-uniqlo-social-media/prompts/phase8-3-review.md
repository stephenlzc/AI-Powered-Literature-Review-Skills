# Phase 8.3: Review - 质量审查与评估Prompt

## 用途
系统性审查综述质量，识别问题和改进点

---

## Prompt

```
You are an experienced academic review expert specializing in literature reviews.
Conduct a comprehensive, rigorous multi-dimensional assessment of the submitted literature review.

Materials to review:
<literature_review_draft>
{{在此处插入Phase 8.2生成的综述初稿}}
</literature_review_draft>

<original_topic>
人工智能在教育评估中的应用
</original_topic>

<collected_papers>
{{在此处插入原始文献清单}}
</collected_papers>

Review criteria:

a) ACCURACY AND COMPREHENSIVENESS (Weight: 25%)
   - Are all factual claims accurate?
   - Are there any misrepresentations of cited studies?
   - Does it cover all important aspects of the topic?
   - Are significant papers missing or overlooked?
   - Score: ___/10

b) LOGICAL ARGUMENTATION (Weight: 25%)
   - Is the overall structure logical and coherent?
   - Do arguments flow naturally from one to another?
   - Are all claims adequately supported by evidence?
   - Are there any logical fallacies or gaps?
   - Score: ___/10

c) LITERATURE CITATIONS (Weight: 20%)
   - Are citations accurate and properly formatted?
   - Is the citation density appropriate (not too sparse or excessive)?
   - Are cited papers relevant to the claims made?
   - Is there a balance between different sources?
   - Score: ___/10

d) CRITICAL ANALYSIS (Weight: 15%)
   - Does it go beyond mere summarization?
   - Are methodological strengths/weaknesses discussed?
   - Are contradictions and controversies identified?
   - Is there genuine synthesis (not just listing papers)?
   - Score: ___/10

e) LANGUAGE AND STYLE (Weight: 10%)
   - Is the language clear, concise, and academic?
   - Are there grammatical errors or awkward phrasing?
   - Is the tone appropriate for academic writing?
   - Score: ___/10

f) INNOVATION AND INSIGHT (Weight: 5%)
   - Does it provide new insights or perspectives?
   - Are future research directions clearly identified?
   - Is there a theoretical framework proposed?
   - Score: ___/10

Deliverables:

1. Overall Quality Score: ___/100

2. Detailed Assessment:

<review>
<major_strengths>
[List 3-5 major strengths of the review with specific examples]
</major_strengths>

<critical_issues>
[List critical issues that MUST be fixed, with specific locations (section/paragraph)]
</critical_issues>

<areas_for_improvement>
[List areas that could be improved for better quality]
</areas_for_improvement>

<missing_elements>
[List important elements missing from the review]
</missing_elements>

<specific_suggestions>
[Provide detailed, actionable suggestions for revision]
1. Section X, Paragraph Y: [Specific issue] → [Suggested fix]
2. ...
</specific_suggestions>

<citation_issues>
[Identify any citation errors or missing citations]
</citation_issues>
</review>

3. Revision Priority:
   - CRITICAL (Must fix): [List]
   - HIGH (Should fix): [List]
   - MEDIUM (Nice to have): [List]
```

---

## 预期输出格式

```markdown
# 综述质量审查报告

## 总体评分：82/100

| 评估维度 | 权重 | 得分 | 加权得分 |
|----------|------|------|----------|
| 准确性和全面性 | 25% | 8/10 | 20/25 |
| 逻辑论证 | 25% | 9/10 | 22.5/25 |
| 文献引用 | 20% | 8/10 | 16/20 |
| 批判分析 | 15% | 7/10 | 10.5/15 |
| 语言表达 | 10% | 8/10 | 8/10 |
| 创新洞察 | 5% | 7/10 | 3.5/5 |

---

## 主要优点

1. **结构清晰逻辑连贯**
   - 从理论基础到技术应用到实践场景的递进结构合理
   - 各章节之间过渡自然，论证链条完整

2. **文献覆盖较为全面**
   - 涵盖了自动化评分、学习分析、能力诊断等主要研究方向
   - 中英文文献平衡，兼顾了国内外研究进展

3. **技术描述准确**
   - 对BERT、深度学习等技术的介绍准确专业
   - 能够恰当引用文献支撑技术论述

4. **讨论部分有深度**
   - 不只罗列研究发现，还进行了有意义的比较分析
   - 对未来研究方向的展望具有参考价值

5. **学术语言规范**
   - 整体语言正式、客观，符合学术写作规范
   - 术语使用准确一致

---

## 关键问题（必须修复）

1. **第3.1节第二段**
   - 问题：提到"ETS的e-rater系统"但未提供引用
   - 修复：添加相应文献引用

2. **第5.2节**
   - 问题：关于研究局限的论述过于笼统，缺乏具体文献支撑
   - 修复：引用具体研究的方法论局限性

3. **参考文献格式**
   - 问题：部分英文文献作者名格式不统一（有的用全名，有的用缩写）
   - 修复：统一采用"姓, 名首字母"格式

---

## 改进建议

1. **增强批判性分析**
   - 目前对文献的评价偏描述性，可增加更多比较性分析
   - 建议对比不同研究方法的优劣

2. **补充定量数据**
   - 部分技术效果描述可加入具体准确率数据
   - 使论述更具说服力

3. **扩展伦理讨论**
   - AI教育评估的伦理问题讨论相对薄弱
   - 建议增加隐私、公平性等议题的探讨

---

## 缺失元素

1. **研究方法说明**
   - 引言部分缺少对文献检索和筛选方法的详细说明
   - 应补充检索词、筛选标准、纳入排除标准

2. **研究局限性声明**
   - 缺少对本综述本身局限性的讨论
   - 应说明文献检索可能的遗漏

---

## 具体修改建议

1. **第1节（引言）**：
   - 补充检索策略的具体说明
   - 明确纳入文献的时间范围

2. **第3.3节**：
   - 对知识追踪模型的论述可增加技术对比
   - 建议对比不同模型的优缺点

3. **第5节（讨论）**：
   - 增加对本综述局限性的说明
   - 补充对纳入文献质量的评价

---

## 修订优先级

### CRITICAL（必须修复）
- [ ] 补充缺失的文献引用（e-rater系统）
- [ ] 统一参考文献格式
- [ ] 第5.2节增加具体文献支撑

### HIGH（应该修复）
- [ ] 补充检索方法详细说明
- [ ] 增强批判性分析深度
- [ ] 扩展伦理讨论内容

### MEDIUM（建议修复）
- [ ] 补充定量效果数据
- [ ] 优化部分段落过渡
- [ ] 增加研究局限性声明
```

---

## 使用说明

1. 将综述初稿、研究主题和文献清单插入对应位置
2. 运行审查Prompt
3. 根据评分决定是否需要迭代：
   - ≥85分：进入Phase 8.4直接润色
   - 70-85分：根据建议修改后进入8.4
   - 60-70分：回到Phase 8.2重写部分章节
   - <60分：回到Phase 8.1重新规划结构
4. 保存审查报告为 `review_report.md`
