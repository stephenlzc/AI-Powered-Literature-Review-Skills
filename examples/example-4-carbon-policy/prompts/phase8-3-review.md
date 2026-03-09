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
中国碳中和政策体系研究
</original_topic>

<collected_papers>
{{在此处插入原始文献清单}}
</collected_papers>

Review criteria:

a) ACCURACY AND COMPREHENSIVENESS (Weight: 25%)
   - Are all factual claims accurate?
   - Are there any misrepresentations of cited studies?
   - Does it cover all important aspects of the topic?
   - Score: ___/10

b) LOGICAL ARGUMENTATION (Weight: 25%)
   - Is the overall structure logical and coherent?
   - Do arguments flow naturally?
   - Score: ___/10

c) LITERATURE CITATIONS (Weight: 20%)
   - Are citations accurate and properly formatted?
   - Is the citation density appropriate?
   - Score: ___/10

d) CRITICAL ANALYSIS (Weight: 15%)
   - Does it go beyond mere summarization?
   - Are contradictions identified?
   - Score: ___/10

e) LANGUAGE AND STYLE (Weight: 10%)
   - Is the language clear and academic?
   - Score: ___/10

f) INNOVATION AND INSIGHT (Weight: 5%)
   - Are future directions clearly identified?
   - Score: ___/10

Deliverables:

1. Overall Quality Score: ___/100

2. Detailed Assessment with sections for:
   - Major strengths
   - Critical issues (must fix)
   - Areas for improvement
   - Missing elements
   - Specific suggestions
   - Citation issues

3. Revision Priority: CRITICAL / HIGH / MEDIUM
```
