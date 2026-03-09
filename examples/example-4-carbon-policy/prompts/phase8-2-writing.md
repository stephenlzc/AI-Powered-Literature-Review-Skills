# Phase 8.2: Writing - 撰写综述初稿Prompt

## 用途
基于大纲撰写完整的综述内容，建立文献间的逻辑联系

---

## Prompt

```
You are a literature writing expert tasked with creating a high-quality, comprehensive academic literature review.

Input materials:
<outline>
{{在此处插入Phase 8.1生成的大纲}}
</outline>

<collected_literature>
{{在此处插入文献清单和摘要}}
</collected_literature>

<detailed_analysis>
{{在此处插入Phase 6生成的单篇文献深度分析}}
</detailed_analysis>

Target language: 中文

Writing instructions:

1. Expand EACH section in the outline into detailed content:
   - Section 1 (Introduction): 300-500 words
   - Section 2 (Policy Background): 500-800 words
   - Section 3 (Main Body): 1500-2500 words (divided among subsections)
   - Section 4 (Discussion): 500-800 words
   - Section 5 (Conclusion): 200-300 words

2. For each subsection:
   - Start with a topic sentence summarizing the main point
   - Synthesize 3-5 relevant papers (do not summarize one by one)
   - Compare and contrast different studies
   - Highlight agreements and disagreements in the literature
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
