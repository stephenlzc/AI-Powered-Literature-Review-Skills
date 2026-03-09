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
中国碳中和政策体系研究
</research_topic>

Finalization steps:

1. ADDRESS REVIEW FEEDBACK:
   - Fix all CRITICAL issues
   - Address HIGH priority suggestions
   - Consider MEDIUM priority improvements

2. STRUCTURE AND FORMATTING:
   - Ensure proper Markdown formatting
   - Apply consistent heading levels
   - Check citations format ([X](url))

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
   - Include policy areas
   - Separate with semicolons

6. COMPILE REFERENCES:
   - Convert to GB/T 7714-2015 format
   - Sort by citation number

7. FINAL POLISH:
   - Proofread for errors
   - Check word count (3000-5000 words)

Output format:

# [Research Topic]: A Literature Review

## Abstract
[200-300 word abstract]

**Keywords**: keyword1; keyword2; keyword3...

---

[Main content]

---

## References
[C1] ...
[E1] ...
```

Requirements:
- Output ONLY the finalized review
- No XML tags
- Ready for direct use
```
