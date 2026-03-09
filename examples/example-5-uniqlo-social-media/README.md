# 示例5：社会化媒体发展背景下优衣库的营销模式研究

## 研究主题

**中文**：社会化媒体发展背景下优衣库的营销模式研究

**英文**: Uniqlo's Marketing Model in the Context of Social Media Development

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
example-5-uniqlo-social-media/
├── README.md                          # 本文件
├── prompts/                           # 各阶段使用的Prompt
│   ├── phase1-query-analysis.md       # Phase 1: 查询分析Prompt
│   ├── phase6-paper-analysis.md       # Phase 6: 文献分析Prompt
│   ├── phase8-1-outline.md            # Phase 8.1: 大纲生成Prompt
│   ├── phase8-2-writing.md            # Phase 8.2: 撰写Prompt
│   ├── phase8-3-review.md             # Phase 8.3: 审查Prompt
│   └── phase8-4-final.md              # Phase 8.4: 定稿Prompt
└── sample-output/                     # 示例输出文件
    ├── references_raw.md              # 文献清单（原始）
    └── literature_review.md           # 最终综述（约6000字）
```

---

## Phase 1 输出示例：检索策略

### 中文关键词
社会化媒体, 社交媒体, 优衣库, 快时尚, 营销模式, 数字营销, 品牌传播, 新媒体营销, 消费者行为, 内容营销

### 英文关键词
social media, Uniqlo, fast fashion, marketing strategy, digital marketing, brand communication, content marketing, consumer behavior, social commerce

### 检索策略

**CNKI检索式**：
```
SU=('社会化媒体'+'社交媒体'+'新媒体')*('优衣库'+'快时尚')*('营销'+'品牌') AND CSSCI=1
```

**Web of Science检索式**：
```
TS=(("social media" OR "digital marketing") AND ("Uniqlo" OR "fast fashion") AND ("marketing strategy" OR "brand communication"))
```

---

## 文献统计

| 类型 | 数量 | 说明 |
|------|------|------|
| 中文文献 | 10篇 | 学位论文5篇 + 期刊5篇 |
| 英文文献 | 12篇 | 期刊论文12篇 |
| **总计** | **22篇** | 时间跨度2012-2024年 |

---

## 综述结构

1. **摘要**（200+字）- 含关键词
2. **引言** - 研究背景、目的、方法
3. **理论基础与概念框架**
   - 社会化媒体营销理论
   - 快时尚与"Mass Prestige"理论
   - O2O与全渠道营销理论
4. **优衣库营销策略研究**
   - 本土化策略
   - 社会化媒体营销策略
   - 联名营销与饥饿营销
5. **社会化媒体营销效果研究**
   - 对消费者行为的影响
   - 视觉内容策略
6. **数字化转型的创新实践**
   - O2O全渠道整合
   - 数据驱动的个性化营销
7. **讨论** - 研究发现、研究空白、未来方向
8. **结论**
9. **参考文献**（GB/T 7714-2015格式）

---

## 核心研究发现

### 三大研究主题

1. **优衣库本土化营销策略**
   - 产品本土化
   - 渠道本土化
   - 营销本土化

2. **社会化媒体营销实践**
   - 微博：品牌曝光与话题营销
   - 微信：私域流量与闭环营销
   - 抖音/TikTok：短视频与年轻群体

3. **O2O全渠道数字化转型**
   - 线上下单、门店取货
   - 统一价格体系
   - 库存互通

### 核心理论框架

- **社会化媒体营销理论** (Li et al., 2021)
- **Mass Prestige理论** (Bilro et al., 2021)
- **O2O全渠道营销理论**

### 未来研究方向

- 短视频平台营销（抖音/TikTok）
- 直播电商
- Z世代消费者行为
- AI与营销创新
- 可持续营销传播

---

## 使用说明

1. **复制Prompt**：从 `prompts/` 目录复制对应阶段的Prompt
2. **替换变量**：将 `{{变量}}` 替换为实际内容
3. **执行工作流**：按顺序执行8个阶段
4. **参考输出**：查看 `sample-output/literature_review.md` 了解预期输出格式

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
- 最终综述字数：约6000字（不含参考文献）
