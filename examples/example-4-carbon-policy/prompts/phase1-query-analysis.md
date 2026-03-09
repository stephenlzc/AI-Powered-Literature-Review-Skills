# Phase 1: Query Analysis - 查询分析Prompt

## 用途
AI智能分析研究主题，生成相关关键词和检索策略

---

## Prompt

```
You are tasked with generating relevant keywords or phrases for a given research direction.

The research direction is provided below:
<research_direction>
中国碳中和政策体系研究
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
研究主题: "中国碳中和政策体系研究"

中文关键词:
  - 碳中和
  - 碳达峰
  - 气候政策
  - 低碳转型
  - 碳排放权交易
  - 能源政策
  - 绿色金融
  - 可持续发展
  
英文关键词:
  - carbon neutrality
  - carbon peak
  - climate policy
  - low-carbon transition
  - carbon trading
  - energy policy
  - green finance
  - sustainable development

检索策略:
  CNKI: "SU=('碳中和'+'碳达峰'+'双碳')*('政策'+'路径'+'战略') AND CSSCI=1"
  WOS: "TS=((\"carbon neutrality\" OR \"carbon peak\" OR \"net-zero\") AND (\"China\" OR \"Chinese\") AND (\"policy\" OR \"strategy\"))"
```
