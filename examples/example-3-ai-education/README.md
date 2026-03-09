# 示例3：人工智能在教育评估中的应用

## 研究主题

**中文**：人工智能在教育评估中的应用研究

**英文**：Applications of Artificial Intelligence in Educational Assessment

---

## 8阶段工作流概览

```
Phase 0: Session Log      → 创建会话目录
Phase 1: Query Analysis   → 生成中英文检索策略  
Phase 2: Parallel Search  → 浏览器自动化检索
Phase 3: Deduplication    → 标题相似度去重
Phase 4: Verification     → 基础元数据校验
Phase 5: Data Export      → 导出文献信息
Phase 6: Paper Analysis   → 单篇文献深度分析
Phase 7: Citation Format  → GB/T 7714-2015格式化
Phase 8: Synthesis        → 生成综述文档
```

---

## 文件结构

```
example-3-ai-education/
├── README.md                          # 本文件
├── prompts/                           # 各阶段使用的Prompt
│   ├── phase1-query-analysis.md       # Phase 1: 查询分析Prompt
│   ├── phase6-paper-analysis.md       # Phase 6: 文献分析Prompt
│   ├── phase8-1-outline.md            # Phase 8.1: 大纲生成Prompt
│   ├── phase8-2-writing.md            # Phase 8.2: 撰写Prompt
│   ├── phase8-3-review.md             # Phase 8.3: 审查Prompt
│   └── phase8-4-final.md              # Phase 8.4: 定稿Prompt
└── sample-output/                     # 示例输出文件
    ├── session_log.md                 # 会话日志示例
    ├── metadata.json                  # 元数据示例
    ├── references.md                  # 文献清单示例
    ├── papers_analysis.md             # 单篇文献分析示例
    ├── outline.md                     # 综述大纲示例
    ├── draft.md                       # 综述初稿示例
    ├── review_report.md               # 审查报告示例
    └── literature_review.md           # 最终综述示例
```

---

## Phase 1 输出示例：检索策略

### 中文关键词
- 人工智能, 教育评估, 学习分析, 智能评测, 自适应学习, 教育数据挖掘, 机器学习, 自然语言处理

### 英文关键词
- artificial intelligence, educational assessment, learning analytics, intelligent tutoring, adaptive learning, educational data mining, machine learning, NLP

### 检索策略

**CNKI检索式**：
```
SU=('人工智能'+'机器学习'+'深度学习')*('教育评估'+'学习分析'+'智能评测') AND CSSCI=1
```

**Web of Science检索式**：
```
TS=(("artificial intelligence" OR "machine learning" OR "deep learning") AND ("educational assessment" OR "learning analytics"))
```

---

## 使用说明

1. **复制Prompt**：从 `prompts/` 目录复制对应阶段的Prompt
2. **替换变量**：将 `{{变量}}` 替换为实际内容
3. **执行工作流**：按顺序执行8个阶段
4. **参考输出**：查看 `sample-output/` 了解预期输出格式

---

## 数据库访问地址

| 数据库 | 访问地址 |
|--------|----------|
| CNKI | https://kns.cnki.net/kns8/AdvSearch |
| Web of Science | https://www.webofscience.com/wos/woscc/advanced-search |
| ScienceDirect | https://www.sciencedirect.com/search |
| Google Scholar | https://scholar.google.com |

---

## 注意事项

- 文献编号：中文以C开头（C1, C2...），英文以E开头（E1, E2...）
- 引用格式：遵循GB/T 7714-2015标准
- 最终综述字数：3000-5000字（不含参考文献）
