# Phase 6: Paper Analysis - 单篇文献深度分析Prompt

## 用途
对每篇文献进行深度分析，提取关键信息

---

## Prompt

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
{{在此处插入文献列表，包含标题、作者、期刊、年份、摘要等信息}}
</articles>
```

---

## 输入数据格式

```json
{
  "papers": [
    {
      "id": "C1",
      "title": "基于深度学习的智能作文评分系统研究",
      "authors": ["张三", "李四"],
      "journal": "教育研究",
      "year": 2023,
      "abstract": "本研究构建了基于深度学习的作文自动评分系统...",
      "keywords": ["深度学习", "作文评分", "自然语言处理"]
    },
    {
      "id": "E1",
      "title": "AI-Driven Personalized Learning: A Systematic Review",
      "authors": ["Smith J", "Johnson K"],
      "journal": "Computers & Education",
      "year": 2022,
      "abstract": "This systematic review examines the applications of AI in personalized learning...",
      "keywords": ["AI", "personalized learning", "adaptive systems"]
    }
  ]
}
```

---

## 预期输出格式

```markdown
# 文献深度分析

---

**文章1：基于深度学习的智能作文评分系统研究**

**主要观点和结论**：
本文提出了一种基于BERT模型的中文作文自动评分方法，在多个评估维度上达到了与人工评分较高的一致性。研究表明深度学习技术能够有效辅助教育评估工作。

**局限性**：
1. 训练数据主要来自特定地区，泛化能力有待验证
2. 对于创意性写作的评价能力有限
3. 缺乏长期跟踪评估

**争议点**：
- AI评分是否能真正理解作文的深层含义
- 自动化评分对写作教学的潜在影响

**研究内容缺陷**：
- 未探讨评分系统的可解释性
- 缺少与教师的协作机制设计
- 未考虑不同文体的差异化处理

**参考文献格式**：
张三, 李四. 基于深度学习的智能作文评分系统研究[J]. 教育研究, 2023, 44(3): 56-68.

---

**文章2：AI-Driven Personalized Learning: A Systematic Review**

**主要观点和结论**：
本系统综述分析了2018-2022年间AI在个性化学习中的89项研究，发现自适应推荐系统和智能辅导系统是最主要的研究方向，学习效果显著提升。

**局限性**：
1. 大部分研究样本量较小
2. 长期效果追踪研究不足
3. 不同学科领域的应用差异未深入探讨

**争议点**：
- 学习者隐私保护与个性化需求的平衡
- AI系统的算法偏见问题

**研究内容缺陷**：
- 对特殊教育需求学生的关注不足
- 缺少跨文化适应性研究

**参考文献格式**：
Smith J, Johnson K. AI-Driven Personalized Learning: A Systematic Review[J]. Computers & Education, 2022, 178: 104-120. DOI:10.1016/j.compedu.2021.104120.
```

---

## 使用说明

1. 收集去重后的文献列表（30-50篇）
2. 将文献信息按上述JSON格式整理
3. 插入到Prompt的 `<articles>` 部分
4. 运行分析，保存结果为 `papers_analysis.md`
