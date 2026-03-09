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
人工智能在教育评估中的应用
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
   b) Theoretical Foundation and Methods
   c) Main Body (3-5 sections based on theme clustering)
      - Domestic Research Status (Chinese literature)
      - International Research Status (English literature)
      - Or thematic sections (e.g., Algorithm Research, Clinical Applications)
   d) Discussion (comparative analysis, research gaps, trends)
   e) Conclusion
   f) References

3. For each main section, provide 3-5 specific subsections with clear titles.

4. Ensure logical flow:
   - From general to specific
   - From theory to application
   - From past to future directions

5. Allocate literature to appropriate sections:
   - Each paper should be referenced in at least one section
   - Highlight connections between papers

6. Output format:
   # Literature Review Outline: [Research Topic]
   
   ## 1 Introduction
   ### 1.1 Research Background
   ### 1.2 Research Objectives
   ### 1.3 Search Strategy
   
   ## 2 Theoretical Foundation
   ### 2.1 [Theory/Method 1]
   ### 2.2 [Theory/Method 2]
   
   ## 3 [Main Theme 1]
   ### 3.1 [Sub-theme]
   - Key papers: [C1], [E1], [E2]
   - Main arguments: ...
   ### 3.2 [Sub-theme]
   
   [Continue for all themes...]
   
   ## 4 Discussion
   ### 4.1 Comparative Analysis
   ### 4.2 Research Gaps
   ### 4.3 Future Directions
   
   ## 5 Conclusion
   
   ## References

7. Do not write any content for the sections, only the structure.

8. Ensure the outline can support a 3000-5000 word literature review.
```

---

## 预期输出格式

```markdown
# 文献综述大纲：人工智能在教育评估中的应用

## 1 引言
### 1.1 研究背景
- 人工智能技术的快速发展
- 教育评估面临的挑战与机遇
- 相关文献：C1, E1, E2

### 1.2 研究目的与意义
- 梳理AI在教育评估中的应用现状
- 识别研究热点与前沿趋势
- 相关文献：C2, E3

### 1.3 检索策略
- 数据库选择：CNKI、WOS、ScienceDirect
- 检索词与筛选标准

---

## 2 理论基础与技术框架
### 2.1 教育评估理论
- 形成性评价与总结性评价
- 相关文献：C3, C4

### 2.2 人工智能技术基础
- 机器学习与深度学习
- 自然语言处理技术
- 相关文献：E4, E5, C5

### 2.3 学习分析技术框架
- 数据收集与处理
- 学习行为建模
- 相关文献：E6, C6

---

## 3 智能评估技术研究
### 3.1 自动化评分系统
- 作文自动评分
- 代码自动评估
- 关键文献：C1, C7, E7, E8

### 3.2 学习过程评估
- 学习行为分析
- 参与度监测
- 关键文献：C8, C9, E9

### 3.3 能力诊断与预测
- 知识掌握度诊断
- 学习风险预测
- 关键文献：C10, E10, E11

---

## 4 应用场景与实践
### 4.1 课堂教学评估
- 实时反馈系统
- 课堂互动分析
- 关键文献：C11, C12, E12

### 4.2 在线教育平台
- 大规模开放在线课程评估
- 个性化学习推荐
- 关键文献：E13, E14, C13

### 4.3 高利害考试
- 标准化考试评卷
- 公平性与有效性
- 关键文献：C14, E15

---

## 5 国内外研究比较
### 5.1 研究热点对比
- 中文文献侧重应用实践
- 英文文献侧重技术算法
- 相关文献：综合比较

### 5.2 方法论差异
- 实证研究vs.系统开发
- 定量vs.定性方法

---

## 6 讨论
### 6.1 研究发现总结
- 技术应用日趋成熟
- 伦理与公平性挑战

### 6.2 研究空白与局限
- 长期效果研究不足
- 跨学科整合有限

### 6.3 未来研究方向
- 可解释AI在教育中的应用
- 多模态学习评估
- 人机协作评估模式

---

## 7 结论
- 主要发现回顾
- 对教育实践的启示
- 研究展望

---

## 参考文献
- 中文文献：C1-C20
- 英文文献：E1-E20
```

---

## 使用说明

1. 确保已完成Phase 6的文献分析
2. 将文献分析结果插入 `<collected_literature>`
3. 运行Prompt生成大纲
4. 检查大纲的逻辑性和完整性
5. 根据需要调整章节结构和文献分配
6. 保存为 `outline.md`
