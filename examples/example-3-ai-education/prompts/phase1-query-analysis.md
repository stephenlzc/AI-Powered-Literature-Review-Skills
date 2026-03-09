# Phase 1: Query Analysis - 查询分析Prompt

## 用途
AI智能分析研究主题，生成相关关键词和检索策略

---

## Prompt

```
You are tasked with generating relevant keywords or phrases for a given research direction.

The research direction is provided below:
<research_direction>
人工智能在教育评估中的应用
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

## 预期输出格式

```yaml
研究主题: "人工智能在教育评估中的应用"

中文关键词:
  - 人工智能
  - 教育评估
  - 学习分析
  - 智能评测
  - 自适应学习
  - 教育数据挖掘
  - 机器学习
  - 自然语言处理
  
英文关键词:
  - artificial intelligence
  - educational assessment
  - learning analytics
  - intelligent tutoring
  - adaptive learning
  - educational data mining
  - machine learning
  - natural language processing

检索策略:
  CNKI: "SU=('人工智能'+'机器学习'+'深度学习')*('教育评估'+'学习分析'+'智能评测') AND CSSCI=1"
  WOS: "TS=((\"artificial intelligence\" OR \"machine learning\" OR \"deep learning\") AND (\"educational assessment\" OR \"learning analytics\"))"
```

---

## 使用说明

1. 将 `<research_direction>` 中的内容替换为您的研究主题
2. 运行Prompt获取中英文关键词
3. 根据关键词构建各数据库的检索式
4. 保存结果到 `metadata.json` 的 `query_analysis` 字段
