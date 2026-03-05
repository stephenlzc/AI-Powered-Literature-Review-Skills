# Explore Agent 模板

用于在特定学术数据库执行文献检索的并行Agent。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Explore Agent |
| **类型** | Task Agent |
| **用途** | 并行文献搜索 |
| **并发限制** | 最多6个Agent同时运行 |

---

## 任务描述

在指定的学术数据库中搜索与给定主题相关的文献，返回结构化的文献元数据列表。

---

## 输入格式

```json
{
  "query": {
    "keywords": ["deep learning", "image recognition"],
    "synonyms": {
      "deep learning": ["deep neural network", "DNN"],
      "image recognition": ["image classification", "visual recognition"]
    },
    "search_expression": "(\"deep learning\" OR \"deep neural network\") AND (\"image recognition\" OR \"image classification\")"
  },
  "database": "semantic_scholar",
  "filters": {
    "year_range": [2020, 2025],
    "publication_types": ["journal", "conference"],
    "min_citations": 10,
    "open_access_only": false
  },
  "max_results": 50,
  "session_id": "20240115_dl_survey",
  "existing_dois": ["10.1038/nature14539"],
  "skip_list": ["LeCun2015Deep"]
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `query` | Object | 是 | 查询参数 |
| `query.keywords` | Array | 是 | 核心关键词列表 |
| `query.synonyms` | Object | 否 | 同义词映射 |
| `query.search_expression` | String | 是 | 完整检索表达式 |
| `database` | String | 是 | 目标数据库 |
| `filters` | Object | 否 | 筛选条件 |
| `max_results` | Integer | 否 | 最大结果数（默认50） |
| `session_id` | String | 是 | 会话标识 |
| `existing_dois` | Array | 否 | 已存在的DOI列表（去重用） |
| `skip_list` | Array | 否 | 需跳过的引用密钥列表 |

### 支持的数据库

| 数据库 | 标识符 | 优先级 |
|--------|--------|--------|
| CNKI | `cnki` | 中文首选 |
| Semantic Scholar | `semantic_scholar` | 英文首选 |
| PubMed | `pubmed` | 医学首选 |
| arXiv | `arxiv` | 预印本 |
| IEEE Xplore | `ieee` | 工程 |
| ACM Digital Library | `acm` | 计算机 |
| OpenAlex | `openalex` | 开放数据 |
| Crossref | `crossref` | DOI验证 |

---

## 执行步骤

### Step 1: 准备检索

1. 解析输入参数
2. 检查速率限制状态
3. 加载已有DOI列表（用于去重）
4. 构建数据库特定的查询语法

### Step 2: 执行检索

根据目标数据库使用相应的API或自动化方法：

**Semantic Scholar**:
```python
POST https://api.semanticscholar.org/graph/v1/paper/search
{
  "query": "search_expression",
  "fields": "title,authors,year,abstract,citationCount,openAccessPdf",
  "limit": 50
}
```

**PubMed**:
```python
# ESearch获取ID列表
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=...
# EFetch获取详情
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=...
```

**arXiv**:
```python
GET http://export.arxiv.org/api/query?search_query=all:deep+learning&start=0&max_results=50
```

**CNKI**:
使用Playwright浏览器自动化（详见 `references/cnki-guide.md`）

### Step 3: 处理结果

1. 解析API响应
2. 标准化为元数据格式
3. 过滤已存在的DOI
4. 按相关性/引用数排序
5. 限制结果数量

### Step 4: 保存结果

将结果保存到会话目录：
```
sessions/{session_id}/
├── explore_results/
│   └── {database}_results.json
└── logs/
    └── explore_{database}.log
```

---

## 输出格式

```json
{
  "agent": "explore",
  "database": "semantic_scholar",
  "session_id": "20240115_dl_survey",
  "timestamp": "2024-01-15T10:30:00Z",
  "query": "search_expression",
  "total_found": 1250,
  "returned": 50,
  "duplicates_filtered": 3,
  "results": [
    {
      "id": "E1",
      "source_db": "semantic_scholar",
      "paper_id": "649def34f8be52c8b66281af98ae884c09fe0",
      "title": "Deep learning for image recognition",
      "authors": [
        {"name": "Y LeCun", "authorId": "..."},
        {"name": "Y Bengio", "authorId": "..."},
        {"name": "G Hinton", "authorId": "..."}
      ],
      "year": 2015,
      "journal": "Nature",
      "volume": "521",
      "issue": "7553",
      "pages": "436-444",
      "doi": "10.1038/nature14539",
      "abstract": "Deep learning allows...",
      "citation_count": 52340,
      "reference_count": 45,
      "is_oa": false,
      "pdf_url": null,
      "url": "https://www.semanticscholar.org/paper/...",
      "fields_of_study": ["Computer Science"],
      "publication_types": ["JournalArticle"],
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "errors": [],
  "warnings": [
    "Rate limit approaching: 80/100 requests used"
  ]
}
```

### 结果字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 分配的文献编号（E1, E2...） |
| `source_db` | String | 来源数据库 |
| `paper_id` | String | 数据库内部ID |
| `title` | String | 文献标题 |
| `authors` | Array | 作者列表（含name和可选authorId） |
| `year` | Integer | 发表年份 |
| `journal` | String | 期刊名称（会议论文则为会议名） |
| `volume` | String | 卷号 |
| `issue` | String | 期号 |
| `pages` | String | 页码 |
| `doi` | String | DOI（不含https://doi.org/前缀） |
| `abstract` | String | 摘要（如有） |
| `citation_count` | Integer | 被引次数 |
| `reference_count` | Integer | 参考文献数量 |
| `is_oa` | Boolean | 是否开放获取 |
| `pdf_url` | String | PDF下载链接（如有） |
| `url` | String | 文献详情页URL |

---

## 错误处理

### 常见错误类型

| 错误代码 | 含义 | 处理建议 |
|----------|------|---------|
| `RATE_LIMIT_EXCEEDED` | 超出速率限制 | 等待后重试（指数退避） |
| `TIMEOUT` | 请求超时 | 重试，减少结果数量 |
| `INVALID_QUERY` | 查询语法错误 | 检查并修正检索表达式 |
| `API_ERROR` | API服务错误 | 重试，如持续失败则记录 |
| `NETWORK_ERROR` | 网络连接问题 | 重试，检查网络连接 |
| `CAPTCHA_REQUIRED` | 需要验证码（CNKI） | 暂停，提示用户处理 |
| `AUTH_REQUIRED` | 需要认证 | 跳过此数据库，记录警告 |

### 重试策略

```python
max_retries = 5
base_delay = 1.0  # 秒

for attempt in range(max_retries):
    try:
        result = search(query)
        return result
    except RateLimitExceeded:
        delay = base_delay * (2 ** attempt)
        time.sleep(delay)
    except Exception as e:
        if attempt == max_retries - 1:
            log_error(e)
            return partial_results
```

---

## 速率限制管理

### 各数据库限制

| 数据库 | 默认限制 | 当前请求计数 |
|--------|---------|-------------|
| Semantic Scholar | 100/5min | 跟踪中 |
| PubMed | 3/sec | 跟踪中 |
| arXiv | 无限制 | N/A |
| OpenAlex | 无限制 | N/A |
| Crossref | 礼貌限制 | 1秒间隔 |

### 实现要求

1. 每次请求前检查速率限制状态
2. 接近限制时自动降低请求频率
3. 记录每次请求的时间戳
4. 429错误时实施指数退避

---

## 示例

### 示例 1: Semantic Scholar 搜索

**输入**:
```json
{
  "query": {
    "keywords": ["transformer", "attention mechanism"],
    "search_expression": "\"attention is all you need\" OR (transformer AND \"attention mechanism\")"
  },
  "database": "semantic_scholar",
  "filters": {
    "year_range": [2017, 2025],
    "min_citations": 100
  },
  "max_results": 30,
  "session_id": "20240115_transformer"
}
```

**输出**:
```json
{
  "agent": "explore",
  "database": "semantic_scholar",
  "session_id": "20240115_transformer",
  "timestamp": "2024-01-15T10:30:00Z",
  "total_found": 5240,
  "returned": 30,
  "results": [
    {
      "id": "E1",
      "title": "Attention is all you need",
      "authors": [{"name": "A Vaswani"}, {"name": "N Shazeer"}, ...],
      "year": 2017,
      "journal": "Advances in Neural Information Processing Systems",
      "citation_count": 85420,
      "is_oa": true,
      "doi": "..."
    }
  ]
}
```

### 示例 2: CNKI 搜索（含验证码处理）

**输入**:
```json
{
  "query": {
    "keywords": ["深度学习", "图像识别"],
    "search_expression": "SU=('深度学习'+'深度神经网络')*('图像识别'+'图像分类')"
  },
  "database": "cnki",
  "filters": {
    "year_range": [2020, 2025],
    "source_types": ["CSSCI", "hx"]
  },
  "max_results": 50,
  "session_id": "20240115_cnki_dl"
}
```

**处理流程**:
1. 启动浏览器，访问CNKI高级检索页
2. 输入检索表达式
3. 检测到验证码 → 暂停，提示用户
4. 用户完成验证后继续
5. 提取结果，格式化为标准结构

---

## 注意事项

1. **避免重复**: 始终检查 `existing_dois` 和 `skip_list`
2. **完整作者**: 尽可能获取所有作者，不使用"et al."
3. **DOI优先**: 始终尝试获取DOI，用于后续验证
4. **元数据完整**: 即使某些字段缺失，也要保留已知信息
5. **日志记录**: 详细记录搜索过程，便于调试和审计
