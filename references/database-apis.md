# 数据库 API 参考

本文档汇总了各学术数据库的 API 接口信息，用于 Agent Swarm 并行检索。

---

## 数据库概览

| 数据库 | 类型 | 认证 | 速率限制 | 主要用途 |
|--------|------|------|---------|---------|
| Semantic Scholar | 学术图谱 | 无需 | 100/5min | 首选英文检索 |
| PubMed | 生物医学 | 可选 | 3/sec | 医学文献 |
| arXiv | 预印本 | 无需 | 无限制 | 预印本、CS |
| OpenAlex | 开放数据 | 建议邮箱 | 无限制 | 开放获取 |
| Crossref | DOI注册 | 礼貌限制 | 无限制 | DOI验证 |
| IEEE Xplore | 工程 | API Key | 视计划 | 工程技术 |
| CNKI | 中文 | 需登录 | 人工 | 中文文献 |

---

## Paper 对象字段映射

不同数据库的字段名称映射到统一 Paper 对象：

| Paper 字段 | Semantic Scholar | PubMed | arXiv | Crossref | OpenAlex |
|-----------|------------------|--------|-------|----------|----------|
| `title` | `title` | `title` | `title` | `title` | `display_name` |
| `authors` | `authors[].name` | `authors` | `author` | `author[]` | `authorships` |
| `year` | `year` | `pubdate` | `published` | `published-print` | `publication_year` |
| `journal` | `venue` | `source` | - | `container-title` | `host_venue` |
| `doi` | `externalIds.DOI` | - | - | `DOI` | `doi` |
| `citation_count` | `citationCount` | - | - | `is-referenced-by-count` | `cited_by_count` |
| `abstract` | `abstract` | `abstract` | `summary` | `abstract` | `abstract` |

---

## 查询语法对比

### 基本检索

| 数据库 | 语法 | 示例 |
|--------|------|------|
| Semantic Scholar | 自然语言 | `deep learning medical imaging` |
| PubMed | 字段标签 | `deep learning[Title/Abstract]` |
| arXiv | 字段前缀 | `ti:deep learning` |
| IEEE | 布尔逻辑 | `(("deep learning") AND "medical")` |

### 布尔逻辑

| 操作 | Semantic Scholar | PubMed | arXiv | IEEE |
|------|-----------------|--------|-------|------|
| AND | 空格/AND | AND | AND | AND |
| OR | OR | OR | OR | OR |
| NOT | - | NOT | ANDNOT | NOT |
| 短语 | `"phrase"` | `"phrase"` | `"phrase"` | `"phrase"` |
| 通配符 | * | * | * | * |

### 高级检索示例

**Semantic Scholar**:
```
("deep learning" OR "neural network") AND ("image recognition" OR "classification") AND year:2020-2024
```

**PubMed**:
```
("deep learning"[Title/Abstract] OR "neural network"[Title/Abstract]) AND ("image recognition"[Title/Abstract]) AND ("2020"[Date - Publication] : "3000"[Date - Publication])
```

**arXiv**:
```
(cat:cs.CV OR cat:cs.LG) AND (ti:deep OR abs:learning)
```

---

## 速率限制汇总

| 数据库 | 默认限制 | 推荐间隔 | 批量策略 |
|--------|---------|---------|---------|
| Semantic Scholar | 100 req/5min | 3秒 | 单次查询获取最大结果 |
| PubMed | 3 req/s | 0.4秒 | 使用 EFetch 批量获取 |
| arXiv | 无明确限制 | 1秒 | 分页获取，每页100 |
| Crossref | 礼貌限制 | 1秒 | 批量DOI查询 |
| OpenAlex | 无限制 | 1秒 | 分页获取，每页200 |
| IEEE | 视订阅 | 1-5秒 | 按需查询 |

---

## 错误代码汇总

### HTTP 状态码

| 代码 | 含义 | 处理建议 |
|------|------|---------|
| 200 | 成功 | - |
| 400 | 请求错误 | 检查查询语法 |
| 401 | 未授权 | 检查 API Key |
| 403 | 禁止访问 | 检查权限/订阅 |
| 404 | 未找到 | 资源不存在 |
| 429 | 速率限制 | 等待后重试 |
| 500 | 服务器错误 | 稍后重试 |
| 503 | 服务不可用 | 稍后重试 |

### 数据库特定错误

**Semantic Scholar**:
- `RateLimitExceeded`: 超出速率限制

**PubMed**:
- `ESEARCH: Empty result`: 无结果
- `EFETCH: Invalid ID`: 无效ID

---

## 重试策略建议

### 指数退避

```python
delay = min(base_delay * (2 ** attempt), max_delay)
```

### 分类重试

| 错误类型 | 重试次数 | 延迟策略 |
|----------|---------|---------|
| 速率限制 (429) | 5 | 指数退避，5-60秒 |
| 超时 | 3 | 线性增加，1-5秒 |
| 服务器错误 (5xx) | 3 | 指数退避，5-30秒 |
| 客户端错误 (4xx) | 0 | 不重试，记录错误 |

### 断路器模式

连续失败5次后，暂停对该服务的请求1分钟。

---

## 批量处理建议

### 分页策略

| 数据库 | 默认页大小 | 最大页大小 | 建议 |
|--------|-----------|-----------|------|
| Semantic Scholar | 100 | 100 | 使用最大值 |
| PubMed | 20 | 10000 | EFetch批量获取 |
| arXiv | 10 | 2000 | 每页100-200 |
| OpenAlex | 25 | 200 | 使用200 |
| Crossref | 20 | 1000 | 每页100 |

### 并行请求控制

```python
# 最多5个并发请求
semaphore = asyncio.Semaphore(5)

async def fetch_with_limit(url):
    async with semaphore:
        return await fetch(url)
```

---

## 数据质量与清洗

### 标准化处理

1. **DOI 标准化**
   - 移除前缀：`https://doi.org/`
   - 转小写
   - 去除空格

2. **作者名标准化**
   - 统一格式：姓, 名首字母
   - 处理Unicode字符

3. **标题标准化**
   - 去除多余空格
   - 统一大小写（用于比较）

### 去重策略

1. **DOI 精确匹配**（优先级1）
2. **标题相似度 > 0.85**（优先级2）
3. **作者+年份+期刊匹配**（优先级3）
