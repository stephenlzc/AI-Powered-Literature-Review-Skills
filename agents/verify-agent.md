# Verify Agent 模板

用于验证文献真实性和补全元数据的专用Agent。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Verify Agent |
| **类型** | Task Agent |
| **用途** | 文献验证和元数据补全 |
| **关键规则** | 每个引用必须通过至少一个验证源确认 |

---

## 核心原则

> **CRITICAL RULE**: Never include a paper you cannot verify. Hallucinated citations are worse than no citations.

每个待验证的文献必须通过至少一个权威来源的验证，确保：
- 文献真实存在
- 元数据准确完整
- 非撤稿论文
- 优先使用正式发表版本（非预印本）

---

## 任务描述

对输入的文献列表进行验证，检查：
1. 文献是否存在（通过DOI、标题+作者查询）
2. 元数据是否准确（标题、作者、期刊、年份）
3. 是否为预印本（检查是否有正式发表版本）
4. 是否被撤稿（检查Retraction Watch等数据库）
5. 补全缺失的元数据（DOI、摘要、引用数等）

---

## 输入格式

```json
{
  "papers": [
    {
      "id": "E1",
      "title": "Deep learning for image recognition",
      "authors": [{"name": "Y LeCun"}, {"name": "Y Bengio"}, {"name": "G Hinton"}],
      "journal": "Nature",
      "year": 2015,
      "doi": "10.1038/nature14539",
      "source_db": "semantic_scholar"
    }
  ],
  "session_id": "20240115_dl_survey",
  "verification_sources": ["crossref", "semantic_scholar", "openalex"],
  "strict_mode": true,
  "check_preprints": true,
  "check_retractions": true
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `papers` | Array | 是 | 待验证的文献列表 |
| `session_id` | String | 是 | 会话标识 |
| `verification_sources` | Array | 否 | 验证源优先级（默认全部） |
| `strict_mode` | Boolean | 否 | 严格模式（默认true） |
| `check_preprints` | Boolean | 否 | 检查预印本（默认true） |
| `check_retractions` | Boolean | 否 | 检查撤稿（默认true） |

---

## 执行步骤

### Step 1: DOI验证

如果文献有DOI，优先使用DOI进行验证：

**Crossref DOI解析**:
```python
GET https://api.crossref.org/works/{doi}
```

**响应检查**:
- HTTP 200: DOI存在，获取完整元数据
- HTTP 404: DOI不存在或无效
- 网络错误: 标记待重试

### Step 2: 元数据比对

将从验证源获取的元数据与输入比对：

| 字段 | 比对方法 | 容差 |
|------|---------|------|
| Title | 字符串相似度 | ≥90% |
| Authors | 作者姓名匹配（前3位） | ≥2位匹配 |
| Journal | 期刊名称匹配 | 完全匹配 |
| Year | 年份 | ±1年 |
| DOI | 完全匹配 | 完全匹配 |

### Step 3: 预印本检查

如果文献来自arXiv或其他预印本服务器：

1. 提取arXiv ID
2. 在Semantic Scholar/Crossref中搜索是否有发表版本
3. 如果找到发表版本：
   - 标记为PREPRINT
   - 更新元数据为期刊版本
   - 记录预印本ID和期刊版本DOI

### Step 4: 撤稿检查

**检查源**:
- Retraction Watch Database
- PubMed Retractions
- Crossref retractions

**处理**:
- 如发现撤稿：标记为RETRACTED，排除
- 记录撤稿原因和日期

### Step 5: 生成验证报告

为每篇文献分配验证状态，生成详细报告。

---

## 验证状态

| 状态 | 代码 | 含义 | 处理方式 |
|------|------|------|---------|
| **VERIFIED** | V | 多源确认存在 | 保留，使用最完整元数据 |
| **SINGLE_SOURCE** | S | 仅单源确认 | 保留，标记待复核 |
| **PREPRINT** | P | 预印本 | 检查发表版本，优先使用期刊版 |
| **RETRACTED** | R | 已撤稿 | **排除**，记录到撤稿列表 |
| **NOT_FOUND** | N | 无法验证 | **排除**，记录警告 |
| **METADATA_MISMATCH** | M | 元数据不一致 | 人工复核 |
| **PENDING** | ? | 待验证 | 继续验证流程 |

---

## 验证源优先级

### 主要验证源

| 优先级 | 验证源 | 适用场景 | 覆盖范围 |
|--------|--------|---------|---------|
| 1 | Crossref | DOI解析 | 全学科 |
| 2 | Semantic Scholar | 元数据补全 | 全学科 |
| 3 | OpenAlex | 开放数据验证 | 全学科 |
| 4 | PubMed | 生物医学 | 医学/生物 |
| 5 | arXiv API | 预印本验证 | CS/物理/数学 |

### 验证策略

```python
def verify_paper(paper):
    # 1. 如果有DOI，优先DOI验证
    if paper.doi:
        result = verify_by_doi(paper.doi)
        if result.status == "VERIFIED":
            return result
    
    # 2. 通过标题+作者搜索验证
    result = verify_by_metadata(paper.title, paper.authors)
    if result.status in ["VERIFIED", "SINGLE_SOURCE"]:
        return result
    
    # 3. 标记为NOT_FOUND
    return VerificationResult(status="NOT_FOUND")
```

---

## 输出格式

```json
{
  "agent": "verify",
  "session_id": "20240115_dl_survey",
  "timestamp": "2024-01-15T10:35:00Z",
  "summary": {
    "total": 50,
    "verified": 42,
    "single_source": 5,
    "preprint": 2,
    "retracted": 0,
    "not_found": 1,
    "metadata_mismatch": 0
  },
  "results": [
    {
      "id": "E1",
      "input": {
        "title": "Deep learning for image recognition",
        "doi": "10.1038/nature14539"
      },
      "status": "VERIFIED",
      "confidence": 1.0,
      "verification_source": "crossref",
      "verified_metadata": {
        "title": "Deep learning",
        "authors": [
          {"given": "Yann", "family": "LeCun"},
          {"given": "Yoshua", "family": "Bengio"},
          {"given": "Geoffrey", "family": "Hinton"}
        ],
        "journal": "Nature",
        "year": 2015,
        "volume": "521",
        "issue": "7553",
        "pages": "436-444",
        "doi": "10.1038/nature14539",
        "abstract": "Deep learning allows...",
        "citation_count": 52340
      },
      "checks": {
        "doi_resolved": true,
        "metadata_match": true,
        "is_preprint": false,
        "is_retracted": false
      },
      "warnings": [],
      "timestamp": "2024-01-15T10:35:30Z"
    }
  ],
  "excluded": [
    {
      "id": "E23",
      "title": "...",
      "status": "NOT_FOUND",
      "reason": "DOI not found in any verification source"
    }
  ],
  "errors": []
}
```

---

## 预印本处理流程

### 检查是否为预印本

**预印本服务器标识**:
- arXiv: `arxiv.org`
- bioRxiv: `biorxiv.org`
- medRxiv: `medrxiv.org`
- SSRN: `ssrn.com`

### 查找发表版本

```python
def check_published_version(preprint_paper):
    # 1. 使用标题在Semantic Scholar搜索
    results = search_semantic_scholar(preprint_paper.title)
    
    # 2. 检查是否有期刊版本
    for result in results:
        if result.venue_type == "journal":
            if title_similarity(preprint_paper.title, result.title) > 0.9:
                return result  # 找到发表版本
    
    return None
```

### 预印本状态处理

| 情况 | 状态 | 操作 |
|------|------|------|
| 找到发表版本 | VERIFIED | 使用期刊版元数据 |
| 未找到发表版本 | PREPRINT | 保留预印本，标记提醒 |
| 预印本已撤回 | RETRACTED | 排除 |

---

## 撤稿检测

### 检查源

**Retraction Watch API**:
```python
GET https://api.retractionwatch.com/v2/search?title=...
```

**PubMed Retractions**:
```python
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={title}+retraction[Title]
```

### 撤稿信息记录

```json
{
  "id": "E15",
  "status": "RETRACTED",
  "retraction_info": {
    "date": "2023-05-15",
    "reason": "Data manipulation",
    "source": "Retraction Watch",
    "notice_url": "https://retractionwatch.com/..."
  }
}
```

---

## 错误处理

### 常见错误

| 错误类型 | 原因 | 处理 |
|----------|------|------|
| `DOI_RESOLUTION_FAILED` | DOI无法解析 | 尝试通过标题+作者搜索 |
| `METADATA_INCOMPLETE` | 元数据缺失 | 从其他源补全 |
| `VERIFICATION_TIMEOUT` | 验证超时 | 重试或标记SINGLE_SOURCE |
| `SOURCE_UNAVAILABLE` | 验证源不可用 | 尝试其他验证源 |

### 重试策略

```python
max_retries = 3
for source in verification_sources:
    for attempt in range(max_retries):
        try:
            result = verify_with_source(paper, source)
            return result
        except Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except Exception:
            break  # 换下一个源
```

---

## 示例

### 示例 1: 成功验证

**输入**:
```json
{
  "papers": [
    {
      "id": "E1",
      "title": "Attention is all you need",
      "authors": [{"name": "A Vaswani"}],
      "doi": "10.48550/arXiv.1706.03762",
      "source_db": "arxiv"
    }
  ]
}
```

**验证过程**:
1. 识别为arXiv预印本
2. 在Semantic Scholar搜索发表版本
3. 找到NIPS 2017发表版本
4. 更新元数据，标记PREPRINT

**输出**:
```json
{
  "id": "E1",
  "status": "VERIFIED",
  "original_status": "PREPRINT",
  "notes": "Updated to published version from NIPS 2017"
}
```

### 示例 2: 撤稿检测

**输入**:
```json
{
  "papers": [
    {
      "id": "E15",
      "title": "Controversial study X",
      "doi": "10.xxxx/xxxx"
    }
  ]
}
```

**验证过程**:
1. DOI解析成功
2. 检查Retraction Watch发现撤稿记录
3. 标记RETRACTED，记录原因

**输出**:
```json
{
  "id": "E15",
  "status": "RETRACTED",
  "retraction_info": {
    "date": "2023-05-15",
    "reason": "Data manipulation"
  },
  "excluded": true
}
```

---

## 注意事项

1. **严格验证**: 宁可排除不确定的文献，也不要冒险使用
2. **记录完整**: 详细记录验证过程和决策依据
3. **多源交叉**: 优先使用多源验证的文献
4. **及时更新**: 定期检查是否有新发表的版本
5. **撤稿敏感**: 对撤稿信息保持敏感，及时排除
