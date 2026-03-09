# Phase 8.1: Outline - 生成综述大纲Prompt

## 用途
基于文献主题聚类，构建逻辑清晰的综述结构

---

## Prompt

```
You are a renowned professor specializing in research methodology and academic writing.
Your task is to create a comprehensive, well-structured, and logically sound literature review outline.

Research topic:
<research_topic>
中国碳中和政策体系研究
</research_topic>

Collected literature analysis:
<collected_literature>
{{在此处插入Phase 6生成的文献深度分析结果}}
</collected_literature>

Target language:
<language>
中文
</language>

Instructions:

1. Analyze all collected papers and identify 3-5 main themes or research directions.

2. Structure the outline as follows:
   a) Introduction (background, objectives, search strategy)
   b) Theoretical Foundation and Policy Evolution
   c) Main Body (3-5 sections based on theme clustering)
      - Policy Framework Analysis
      - Implementation Pathways
      - Sectoral Policies (energy, industry, transport, etc.)
   d) Discussion (comparative analysis, research gaps, trends)
   e) Conclusion
   f) References

3. For each main section, provide 3-5 specific subsections with clear titles.

4. Ensure logical flow:
   - From policy background to specific measures
   - From national strategy to sectoral implementation
   - From current status to future directions

5. Allocate literature to appropriate sections:
   - Each paper should be referenced in at least one section
   - Highlight connections between papers

6. Output format:
   # Literature Review Outline: [Research Topic]
   
   ## 1 Introduction
   ### 1.1 Research Background
   ### 1.2 Research Objectives
   ### 1.3 Search Strategy
   
   ## 2 Policy Background and Evolution
   ### 2.1 International Climate Agreements
   ### 2.2 China's Carbon Neutrality Commitment
   
   ## 3 [Main Theme 1]
   ### 3.1 [Sub-theme]
   - Key papers: [C1], [E1], [E2]
   - Main arguments: ...

   [Continue for all themes...]
   
   ## 4 Discussion
   ### 4.1 Policy Effectiveness
   ### 4.2 Research Gaps
   ### 4.3 Future Directions
   
   ## 5 Conclusion
   
   ## References

7. Do not write any content for the sections, only the structure.

8. Ensure the outline can support a 3000-5000 word literature review.
```
