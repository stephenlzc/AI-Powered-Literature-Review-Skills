---
name: literature-survey
description: |
  根据用户提供的论文标题进行系统性文献回顾（Literature Survey）。
  采用8阶段工作流和Agent Swarm并行架构：
  (0) Session Log (1) Query Analysis (2) Parallel Search (3) Deduplication 
  (4) Verification (5) PDF Management (6) Citation Export (7) Synthesis。
  支持CNKI、Semantic Scholar、PubMed、arXiv、IEEE等中英文数据库。
  输出格式：GB/T 7714-2015、BibTeX、Zotero。
  当用户提到"文献回顾"、"文献综述"、"帮我找文献"、"中英文文献搜索"、"写综述"等关键词时触发。
---

# 文献回顾（Literature Survey）

根据用户提供的论文标题，进行系统性的中英文文献检索、验证和综述撰写。
采用 **8阶段工作流** 和 **Agent Swarm 并行架构**，确保高效、准确、可追溯的文献调研过程。

---

## 核心架构：Agent Swarm 并行系统

### 子代理职责分工

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Orchestrator (协调器)                              │
│                   管理 Session Log、任务调度、错误恢复                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐         ┌─────────────────┐         ┌───────────────────┐
│  CNKI Agent   │         │  Semantic       │         │  PubMed Agent     │
│  (中文文献)    │         │  Scholar Agent  │         │  (生物医学)       │
└───────────────┘         └─────────────────┘         └───────────────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Deduplicator (去重器)                                 │
│              DOI精确匹配 + 标题相似度 + 作者/年份/期刊匹配                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Verifier (验证器)                                      │
│         DOI验证 + Crossref查询 + 预印本检查 + 撤稿检测                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PDF Downloader (下载器)                                 │
│         开放获取检查 + Unpaywall API + 预印本服务器                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Synthesizer (综述生成器)                                │
│         主题聚类 + 趋势分析 + Gap识别 + 交叉引用生成                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 并行搜索策略

| Agent | 目标数据库 | 检索范围 | 预期结果 |
|-------|-----------|---------|---------|
| CNKI Agent | 中国知网 | CSSCI、北大核心、CSCD | 中文高质量期刊论文 |
| Semantic Scholar Agent | Semantic Scholar | 全学科 | 英文期刊论文、预印本 |
| PubMed Agent | PubMed/MEDLINE | 生物医学领域 | 医学相关文献 |
| arXiv Agent | arXiv.org | CS、物理、数学 | 最新预印本研究 |
| IEEE Agent | IEEE Xplore | 工程技术 | 工程领域论文 |
| ACM Agent | ACM Digital Library | 计算机科学 | 顶会论文 |

---

## 8阶段工作流

### Phase 0: Session Log（会话追踪）

**目标**：创建可恢复的检查点，支持中断续传

**操作**：
1. 创建会话目录：`sessions/{YYYYMMDD}_{topic_short}/`
2. 初始化日志文件：`session_log.md`
3. 记录初始参数：查询主题、数据库选择、筛选条件
4. 设置检查点（每完成一个Phase自动保存）

**日志格式**：
```markdown
# Session Log: [主题]
- Created: [时间戳]
- Status: [进行中/已完成/中断]

## Phase 1: Query Analysis ✓
- 输入: [原始查询]
- 输出: [关键词列表]
- 检查点: checkpoint_p1.json

## Phase 2: Parallel Search ◐
- CNKI Agent: 50 results
- Semantic Scholar Agent: 30 results
- ...
```

---

### Phase 1: Query Analysis（查询分析）

**目标**：从用户输入提取核心概念，生成中英文检索策略

**步骤**：
1. **识别核心概念**
   - 研究主题（Topic）
   - 研究方法（Method）
   - 研究对象（Object）
   - 应用领域（Domain）

2. **生成中英文关键词**
   
   | 类别 | 中文关键词 | 英文关键词 |
   |------|-----------|-----------|
   | 核心概念 | 深度学习 | deep learning |
   | 同义词扩展 | 深度神经网络、深层学习 | deep neural network, DNN |
   | 相关术语 | 表示学习 | representation learning |

3. **构建检索表达式**

   **CNKI检索式**：
   ```
   SU=('深度学习'+'深度神经网络')*('图像识别'+'图像分类')
   ```
   
   **PubMed检索式**：
   ```
   ("deep learning"[Title/Abstract] OR "deep neural network"[Title/Abstract]) 
   AND ("image recognition"[Title/Abstract] OR "image classification"[Title/Abstract])
   ```
   
   **Semantic Scholar检索式**：
   ```
   ("deep learning" OR "deep neural network") AND ("image recognition" OR "image classification")
   ```

**输出**：
- `keywords.json`: 中英文关键词及同义词
- `queries.json`: 各数据库检索表达式

---

### Phase 2: Parallel Search（并行搜索）

**目标**：在多个数据库并行执行检索

#### 2.1 CNKI 高级检索策略

**访问地址**：`https://kns.cnki.net/kns/AdvSearch?classid=7NS01R8M`

**字段代码**：
| 代码 | 含义 | 使用场景 |
|------|------|---------|
| SU | 主题 | 广泛检索 |
| TI | 篇名 | 精确匹配 |
| KY | 关键词 | 主题相关 |
| TKA | 篇关摘 | 最全面 |
| AU | 作者 | 查找特定作者 |
| JN | 期刊 | 限定期刊范围 |

**来源类别筛选**：
- `CSSCI`: 中文社会科学引文索引
- `hx`: 北大核心期刊
- `CSCD`: 中国科学引文数据库
- `SCI`: SCI来源期刊
- `EI`: EI来源期刊

**检索执行**（使用Playwright自动化）：
```javascript
// 详见 references/cnki-guide.md
```

#### 2.2 英文数据库并行配置

| 数据库 | 优先级 | 检索字段 | 默认排序 |
|--------|--------|---------|---------|
| Semantic Scholar | 1 | title, abstract | citationCount:desc |
| PubMed | 2 (医学) | Title/Abstract | Relevance |
| arXiv | 3 (CS) | title, abstract | submittedDate:desc |
| IEEE Xplore | 4 (工程) | Metadata | Publication Year:desc |

#### 2.3 错误处理与重试机制

**速率限制**：
| 数据库 | 默认限制 | 重试间隔 |
|--------|---------|---------|
| Semantic Scholar | 100 req/5min | 3秒 |
| PubMed | 3 req/s | 0.5秒 |
| arXiv | 无限制 | 1秒 |
| Crossref | 礼貌限制 | 1秒 |

**重试策略**：
- 指数退避：1s → 2s → 4s → 8s → 放弃
- 最大重试次数：5次
- 失败后记录到 `failed_searches.json`

#### 2.4 验证码处理

**CNKI验证码**：
1. 检测到验证码时暂停执行
2. 提示用户手动完成验证
3. 用户确认后继续

---

### Phase 3: Deduplication（去重筛选）

**目标**：合并多源结果，去除重复，筛选高质量文献

#### 3.1 去重策略

**第一层：DOI精确匹配**
```python
# DOI标准化后匹配
normalized_doi = doi.lower().strip()
```

**第二层：标题相似度匹配**
```python
# 使用Levenshtein距离或余弦相似度
similarity = calculate_similarity(title1, title2)
if similarity > 0.85:
    mark_as_duplicate()
```

**第三层：元数据匹配**
- 作者（前3位）+ 年份 + 期刊（前10字符）
- 用于没有DOI的文献

#### 3.2 质量筛选

**筛选条件**：
| 维度 | 中文文献 | 英文文献 |
|------|---------|---------|
| 时间范围 | 近5年优先 | 近5年优先 |
| 来源质量 | CSSCI/北大核心/CSCD | Q1-Q2期刊/顶会 |
| 被引次数 | >10次 | >50次 |
| 开放获取 | 不限 | OA优先 |

#### 3.3 统一数据模型

**Paper对象（JSON Schema）**：
```json
{
  "id": "E1",
  "type": "journal",
  "source_db": "semantic_scholar",
  "title": "Deep learning for image recognition",
  "authors": [
    {"name": "LeCun Y", "affiliation": "NYU"}
  ],
  "journal": "Nature",
  "year": 2015,
  "volume": "521",
  "issue": "7553",
  "pages": "436-444",
  "doi": "10.1038/nature14539",
  "abstract": "...",
  "keywords": ["deep learning", "neural networks"],
  "citation_count": 50000,
  "impact_factor": 43.07,
  "is_oa": true,
  "pdf_url": "https://...",
  "language": "en",
  "verified": false
}
```

---

### Phase 4: Verification（引用验证）

**目标**：确保引用真实存在，补全准确元数据，避免幻觉引用

#### 4.1 验证流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   输入文献   │────▶│  DOI验证    │────▶│ 元数据比对   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
                   ┌─────────┐          ┌─────────┐          ┌─────────┐
                   │ VERIFIED│          │PREPRINT │          │ RETRACTED│
                   │已验证   │          │预印本   │          │ 已撤稿   │
                   └─────────┘          └─────────┘          └─────────┘
```

#### 4.2 验证规则

**CRITICAL RULE**: 每个引用必须通过至少一个验证源确认

**验证源优先级**：
1. **Crossref**（首选）：DOI解析，获取完整元数据
2. **Semantic Scholar**：覆盖广，引用数据
3. **PubMed**：生物医学文献权威
4. **OpenAlex**：开放学术图谱
5. **arXiv**：预印本验证

**预印本检查**：
- 如果文献来自arXiv，搜索是否已有正式发表版本
- 优先使用期刊版本（通常更完整、经过同行评审）

#### 4.3 验证状态

| 状态 | 含义 | 处理方式 |
|------|------|---------|
| VERIFIED | 多源确认存在 | 保留，使用最完整元数据 |
| SINGLE_SOURCE | 仅单源确认 | 保留，标记待复核 |
| PREPRINT | 预印本 | 搜索发表版本，优先使用期刊版 |
| RETRACTED | 已撤稿 | 排除，记录到 `retracted_papers.json` |
| NOT_FOUND | 无法验证 | 排除，记录警告 |
| METADATA_MISMATCH | 元数据不一致 | 人工复核 |

#### 4.4 异常处理

**DOI解析失败**：
- 尝试去除前缀（`10.` → `https://doi.org/10.`）
- 检查DOI格式有效性
- 尝试通过标题+作者在Crossref搜索

---

### Phase 5: PDF Management（PDF管理）

**目标**：获取可下载的PDF，建立本地文献库

#### 5.1 PDF获取优先级

```
1. 直接PDF链接（从数据库获取）
2. Unpaywall API（开放获取检查）
3. 预印本服务器（arXiv, bioRxiv, medRxiv）
4. 机构访问（通过用户提供的访问权限）
5. 作者主页/ResearchGate（尝试获取）
```

#### 5.2 Unpaywall API使用

```python
# 示例：检查开放获取状态
import requests

response = requests.get(
    f"https://api.unpaywall.org/v2/{doi}",
    params={"email": "your@email.com"}
)
data = response.json()

if data.get("is_oa"):
    pdf_url = data["best_oa_location"]["url_for_pdf"]
```

#### 5.3 文件组织规范

```
project/
└── literature/
    ├── pdfs/
    │   ├── E1_Deep_learning_for_image_recognition.pdf
    │   ├── E2_Attention_is_all_you_need.pdf
    │   └── ...
    ├── metadata/
    │   └── papers_index.json
    └── failed_downloads.txt
```

**文件命名规则**：
```
{ID}_{FirstAuthorSurname}_{Year}_{ShortTitle}.pdf

示例：
E1_LeCun_2015_Deep_learning_image_recognition.pdf
C1_张三_2023_基于深度学习的图像识别研究.pdf
```

---

### Phase 6: Citation Export（引用导出）

**目标**：生成多种格式的引用文件，支持文献管理工具

#### 6.1 GB/T 7714-2015 格式

**期刊论文（中文）**：
```
[C1] 张三, 李四, 王五. 基于深度学习的图像识别研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.
```

**期刊论文（英文）**：
```
[E1] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444. DOI:10.1038/nature14539.
```

**其他类型**：详见 `references/gb-t-7714-2015.md`

#### 6.2 BibTeX 格式

**Better BibTeX 引用密钥规则**：
```bibtex
@article{LeCun2015Deep,
  author    = {LeCun, Yann and Bengio, Yoshua and Hinton, Geoffrey},
  title     = {Deep learning},
  journal   = {Nature},
  year      = {2015},
  volume    = {521},
  number    = {7553},
  pages     = {436--444},
  doi       = {10.1038/nature14539},
  abstract  = {...}
}
```

**密钥格式**：`AuthorYearTitle`（如 `LeCun2015Deep`）

#### 6.3 Zotero 集成

**导出步骤**：
1. 生成 `.bib` 文件
2. 使用Zotero的"导入"功能
3. 或使用Zotero Connector浏览器插件直接导入

**自动同步**（可选）：
- 使用 `scripts/sync_zotero.py` 批量推送

---

### Phase 7: Synthesis（综述生成）

**目标**：撰写结构化的文献综述，建立文献间的逻辑联系

#### 7.1 综述结构模板

```markdown
# 文献回顾：{论文标题}

## 1 引言
### 1.1 研究背景
### 1.2 研究目的与范围
### 1.3 文献检索策略
- 数据库：CNKI、Semantic Scholar、PubMed...
- 检索式：...
- 筛选标准：...

## 2 国内研究现状（中文文献）
### 2.1 {主题分类1}
在{主题1}方面，国内学者主要从...角度展开研究：
- 张三等[C1]从...角度发现...
- 李四等[C2]则关注...
- 王五等[C3]进一步指出...

### 2.2 {主题分类2}
...

## 3 国外研究现状（英文文献）
### 3.1 {主题分类1}
国外研究在{主题1}方面呈现...特点：
- Smith et al.[E1] proposed...
- Johnson et al.[E2] demonstrated...

### 3.2 {主题分类2}
...

## 4 国内外研究比较与讨论
### 4.1 研究热点对比
### 4.2 方法论差异
### 4.3 研究空白与趋势

## 5 结论与展望

## 参考文献
[C1] ...
[C2] ...
[E1] ...
```

#### 7.2 写作原则

**避免简单罗列**：
- ❌ 错误："A研究了X，B研究了Y，C研究了Z"
- ✅ 正确："在X问题上，学者们从不同角度展开：A从...角度发现...；B则关注..."

**建立文献联系**：
- 比较不同研究的异同
- 指出继承关系（如 "基于C1的工作，C2进一步..."）
- 分析方法论差异

**批判性思维**：
- 评价方法优劣
- 指出研究局限性
- 识别研究空白（Gap）

#### 7.3 交叉引用实现

**引用格式**：
| 类型 | 格式 | 示例 |
|------|------|------|
| 单篇中文 | `[C1]` | 张三等[C1]研究发现... |
| 单篇英文 | `[E1]` | Smith et al.[E1] proposed... |
| 多篇连续 | `[C1-C3]` | 早期研究[C1-C3]表明... |
| 多篇不连续 | `[C1,C3,C5]` | 相关研究[C1,C3,C5]显示... |

**Word文档交叉引用**：
1. 为每条参考文献添加书签（如 `ref_C1`、`ref_E1`）
2. 文中引用处使用"交叉引用"功能链接到书签
3. 确保引用编号可点击跳转到参考文献列表

---

## 速率限制与错误处理

### 各数据库速率限制

| 数据库 | 默认限制 | 推荐间隔 | 认证要求 |
|--------|---------|---------|---------|
| Semantic Scholar | 100 req/5min | 3秒 | 无需 |
| PubMed E-utilities | 3 req/s | 0.4秒 | 可选API Key |
| Crossref | 礼貌限制 | 1秒 | 无需 |
| arXiv | 无明确限制 | 1秒 | 无需 |
| CNKI | 人工操作 | N/A | 需登录 |
| OpenAlex | 无限制 | 1秒 | 建议提供邮箱 |

### 重试策略配置

```python
# 指数退避策略
RETRY_CONFIG = {
    "max_retries": 5,
    "base_delay": 1.0,      # 秒
    "max_delay": 60.0,      # 秒
    "exponential_base": 2,
    "retry_on": [429, 500, 502, 503, 504]
}
```

### 错误日志记录

**格式**：
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "phase": "Phase 2: Parallel Search",
  "agent": "Semantic Scholar",
  "error_type": "RateLimitExceeded",
  "message": "429 Too Many Requests",
  "retry_count": 3,
  "resolved": false
}
```

---

## 工具与资源

### 脚本工具

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `scripts/keyword_extractor.py` | 关键词提取与扩展 | Phase 1 |
| `scripts/citation_formatter.py` | 引用格式化 | Phase 6 |
| `scripts/verify_references.py` | 引用验证 | Phase 4 |
| `scripts/deduplicate_papers.py` | 文献去重 | Phase 3 |
| `scripts/sync_zotero.py` | Zotero同步 | Phase 6 |
| `scripts/session_manager.py` | 会话管理 | Phase 0 |

### Agent 模板

| Agent | 模板文件 | 用途 |
|-------|---------|------|
| Explore Agent | `agents/explore-agent.md` | 并行搜索 |
| Verify Agent | `agents/verify-agent.md` | 引用验证 |
| Download Agent | `agents/download-agent.md` | PDF下载 |
| Synthesize Agent | `agents/synthesize-agent.md` | 综述生成 |
| Orchestrator | `agents/orchestrator.md` | 整体协调 |

### 参考资料

- `references/cnki-guide.md`：CNKI检索详细指南（含验证码处理）
- `references/english-search-guide.md`：英文数据库API指南
- `references/gb-t-7714-2015.md`：GB/T 7714-2015引用格式规范
- `references/database-apis.md`：各数据库API对比和速率限制
- `references/workflow-templates.md`：工作流模板（快速/系统/计量）

---

## 质量检查清单

### Phase 0-2（检索阶段）
- [ ] 关键词覆盖研究主题的核心概念
- [ ] 中英文关键词均有同义词扩展
- [ ] 检索表达式使用正确的布尔逻辑
- [ ] 中文文献检索覆盖CSSCI、北大核心等高质量期刊
- [ ] 英文文献检索覆盖至少3个主流数据库
- [ ] 已记录各数据库的检索结果数量

### Phase 3-4（处理阶段）
- [ ] 去重后保留文献数量合理（建议30-50篇）
- [ ] 所有保留文献都有DOI或其他唯一标识
- [ ] 验证状态为VERIFIED或SINGLE_SOURCE
- [ ] 已排除撤稿文献（RETRACTED）
- [ ] 预印本已检查是否有正式发表版本

### Phase 5-6（导出阶段）
- [ ] PDF文件命名符合规范
- [ ] GB/T 7714-2015格式正确
- [ ] BibTeX引用密钥符合Better BibTeX规范
- [ ] 所有作者姓名完整（非"et al."）
- [ ] DOI格式正确且可解析

### Phase 7（综述阶段）
- [ ] 综述结构完整（引言-国内-国外-讨论-结论）
- [ ] 文献按主题分类，非简单罗列
- [ ] 建立了文献间的逻辑联系
- [ ] 体现了批判性思维（方法评价、Gap识别）
- [ ] 文中引用与参考文献列表编号一致
- [ ] 交叉引用链接可正常跳转

---

## 依赖 Skills

- **docx**：用于生成 Word 文档
- **pdf**：用于读取 PDF 文献内容

---

## 触发关键词

- "文献回顾"
- "文献综述"
- "帮我找文献"
- "中英文文献搜索"
- "写综述"
- "literature survey"
- "帮我查相关文献"
- "系统性文献回顾"
- "systematic review"
