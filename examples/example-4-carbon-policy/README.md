# 示例4：碳中和政策研究

## 研究主题

**中文**：中国碳中和政策体系研究

**英文**：Carbon Neutrality Policy Framework in China

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
example-4-carbon-policy/
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
    ├── outline.md                     # 综述大纲示例
    ├── review_report.md               # 审查报告示例
    └── literature_review.md           # 最终综述示例
```

---

## Phase 1 输出示例：检索策略

### 中文关键词
- 碳中和, 碳达峰, 气候政策, 低碳转型, 碳排放权交易, 能源政策, 绿色金融, 可持续发展

### 英文关键词
- carbon neutrality, carbon peak, climate policy, low-carbon transition, carbon trading, energy policy, green finance, sustainable development

### 检索策略

**CNKI检索式**：
```
SU=('碳中和'+'碳达峰'+'双碳')*('政策'+'路径'+'战略') AND CSSCI=1
```

**Web of Science检索式**：
```
TS=(("carbon neutrality" OR "carbon peak" OR "net-zero") AND ("China" OR "Chinese") AND ("policy" OR "strategy"))
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

## 与示例3的区别

| 特点 | 示例3：AI教育评估 | 示例4：碳中和政策 |
|------|------------------|------------------|
| 学科领域 | 教育技术/计算机 | 环境政策/经济学 |
| 研究方法 | 技术实现为主 | 政策分析为主 |
| 数据来源 | 实验数据 | 政策文件/统计数据 |
| 综述重点 | 技术发展与应用 | 政策演进与效果 |
