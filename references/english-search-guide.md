# 英文文献数据库检索指南

本文档提供主要英文学术数据库的 API 使用指南和检索策略。

---

## 推荐数据库优先级

### 1. Semantic Scholar（首选）

- **URL**: https://www.semanticscholar.org/
- **API**: https://api.semanticscholar.org/
- **优点**: 免费、API友好、覆盖广泛、引用数据丰富
- **适用**: 所有学科领域
- **速率限制**: 100 requests / 5 minutes

#### API 使用示例

```python
import requests
import time

def search_semantic_scholar(query, fields=None, limit=100):
    """
    搜索 Semantic Scholar
    
    Args:
        query: 检索表达式
        fields: 返回字段列表
        limit: 结果数量
    """
    if fields is None:
        fields = [
            "paperId", "title", "authors", "year", "venue",
            "citationCount", "referenceCount", "abstract",
            "fieldsOfStudy", "publicationTypes", "openAccessPdf"
        ]
    
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "fields": ",".join(fields),
        "limit": limit
    }
    
    headers = {
        "User-Agent": "LiteratureSurvey/2.0"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 429:
        # 速率限制，等待后重试
        time.sleep(60)
        return search_semantic_scholar(query, fields, limit)
    
    response.raise_for_status()
    return response.json()

# 使用示例
results = search_semantic_scholar(
    query='("deep learning" OR "neural network") AND ("image recognition")',
    limit=50
)

for paper in results.get("data", []):
    print(f"{paper['title']} - {paper['year']}")
```

#### 查询语法

| 操作 | 语法 | 示例 |
|------|------|------|
| 短语 | `"phrase"` | `"deep learning"` |
| AND | 空格或 AND | `deep learning AND medical` |
| OR | OR | `CNN OR "convolutional neural network"` |
| 年份 | `year:YYYY-YYYY` | `year:2020-2024` |
| 作者 | `author:"Name"` | `author:"LeCun"` |
| 期刊 | `venue:"Journal"` | `venue:"Nature"` |

---

### 2. PubMed / MEDLINE

- **URL**: https://pubmed.ncbi.nlm.nih.gov/
- **API**: E-utilities (https://www.ncbi.nlm.nih.gov/home/develop/api/)
- **优点**: 生物医学领域权威，MeSH术语支持
- **适用**: 医学、生物学、生命科学
- **速率限制**: 3 requests / second

#### E-utilities API 使用

```python
import requests
import xml.etree.ElementTree as ET
from time import sleep

class PubMedClient:
    """PubMed E-utilities 客户端"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key=None, email="user@example.com"):
        self.api_key = api_key
        self.email = email
        self.last_request_time = 0
    
    def _rate_limit(self):
        """速率限制：最多3次/秒"""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.34:  # 1/3 秒
            time.sleep(0.34 - elapsed)
        self.last_request_time = time.time()
    
    def search(self, query, max_results=100):
        """
        ESearch：搜索获取PMID列表
        
        Args:
            query: PubMed检索式
            max_results: 最大结果数
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data["esearchresult"]["idlist"]
    
    def fetch(self, pmids):
        """
        EFetch：获取文献详情
        
        Args:
            pmids: PMID列表
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # 解析 XML
        root = ET.fromstring(response.content)
        return self._parse_articles(root)
    
    def _parse_articles(self, root):
        """解析 XML 响应"""
        articles = []
        for article in root.findall(".//PubmedArticle"):
            # 提取标题
            title = article.find(".//ArticleTitle")
            title_text = title.text if title is not None else ""
            
            # 提取摘要
            abstract = article.find(".//AbstractText")
            abstract_text = abstract.text if abstract is not None else ""
            
            # 提取作者
            authors = []
            for author in article.findall(".//Author"):
                lastname = author.find("LastName")
                forename = author.find("ForeName")
                if lastname is not None:
                    name = f"{forename.text} {lastname.text}" if forename is not None else lastname.text
                    authors.append(name)
            
            articles.append({
                "title": title_text,
                "abstract": abstract_text,
                "authors": authors
            })
        
        return articles

# 使用示例
client = PubMedClient(api_key="your_api_key")

# 搜索
pmids = client.search(
    '"deep learning"[Title/Abstract] AND "medical imaging"[Title/Abstract]',
    max_results=50
)
print(f"Found {len(pmids)} papers")

# 获取详情
articles = client.fetch(pmids[:10])  # 获取前10篇
for article in articles:
    print(article["title"])
```

#### PubMed 检索语法

| 操作 | 语法 | 示例 |
|------|------|------|
| 标题 | `[Title]` | `cancer[Title]` |
| 摘要 | `[Abstract]` | `therapy[Abstract]` |
| 作者 | `[Author]` | `Smith[Author]` |
| MeSH | `[MeSH Terms]` | `Neoplasms[MeSH]` |
| 年份 | `[Date - Publication]` | `2020:2024[Date - Publication]` |
| 文献类型 | `[Publication Type]` | `Review[Publication Type]` |

**高级示例**:
```
("deep learning"[MeSH Terms] OR "deep learning"[Title/Abstract]) 
AND ("medical imaging"[Title/Abstract]) 
AND ("2020"[Date - Publication] : "3000"[Date - Publication])
AND (English[Language])
```

---

### 3. arXiv

- **URL**: https://arxiv.org/
- **API**: http://export.arxiv.org/api/
- **优点**: 免费预印本、计算机科学/物理学权威
- **适用**: CS、物理、数学、量化生物学
- **速率限制**: 无明确限制（建议礼貌使用）

#### API 使用示例

```python
import requests
import xml.etree.ElementTree as ET
from time import sleep

def search_arxiv(query, start=0, max_results=100, sort_by="submittedDate"):
    """
    搜索 arXiv
    
    Args:
        query: 检索表达式
        start: 起始位置
        max_results: 结果数量
        sort_by: 排序方式（relevance, lastUpdatedDate, submittedDate）
    """
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": "descending"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # 解析 XML
    root = ET.fromstring(response.content)
    
    # 定义命名空间
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }
    
    papers = []
    for entry in root.findall("atom:entry", ns):
        paper = {
            "id": entry.find("atom:id", ns).text,
            "title": entry.find("atom:title", ns).text.strip(),
            "summary": entry.find("atom:summary", ns).text.strip(),
            "published": entry.find("atom:published", ns).text,
            "updated": entry.find("atom:updated", ns).text,
            "authors": [
                author.find("atom:name", ns).text 
                for author in entry.findall("atom:author", ns)
            ],
            "categories": [
                cat.get("term") 
                for cat in entry.findall("atom:category", ns)
            ],
            "pdf_url": None
        }
        
        # 获取 PDF 链接
        for link in entry.findall("atom:link", ns):
            if link.get("title") == "pdf":
                paper["pdf_url"] = link.get("href")
                break
        
        papers.append(paper)
    
    return papers

# 使用示例
# 搜索计算机视觉领域的深度学习论文
papers = search_arxiv(
    query="cat:cs.CV AND (ti:deep OR abs:neural)",
    max_results=50
)

for paper in papers:
    print(f"{paper['title']} - {paper['published'][:4]}")
    print(f"  PDF: {paper['pdf_url']}")
```

#### arXiv 查询语法

| 操作 | 前缀 | 示例 |
|------|------|------|
| 标题 | `ti:` | `ti:transformer` |
| 作者 | `au:` | `au:Hinton` |
| 摘要 | `abs:` | `abs:"attention mechanism"` |
| 评论 | `co:` | `co:ICML` |
| 期刊引用 | `jr:` | `jr:Nature` |
| 学科分类 | `cat:` | `cat:cs.LG` |
| ID | `id:` | `id:1706.03762` |

**常用学科分类**:
- `cs.AI`: 人工智能
- `cs.CL`: 计算语言学（NLP）
- `cs.CV`: 计算机视觉
- `cs.LG`: 机器学习
- `cs.IR`: 信息检索
- `stat.ML`: 统计学习
- `q-bio.QM`: 定量生物学

---

### 4. OpenAlex

- **URL**: https://openalex.org/
- **API**: https://docs.openalex.org/
- **优点**: 完全开放、免费、数据丰富
- **适用**: 全学科领域
- **速率限制**: 无限制（建议礼貌使用）

#### API 使用示例

```python
import requests
import asyncio
import aiohttp

async def search_openalex(query, per_page=25, max_results=100):
    """
    搜索 OpenAlex
    
    Args:
        query: 检索表达式
        per_page: 每页数量
        max_results: 最大结果数
    """
    all_results = []
    cursor = "*"
    
    async with aiohttp.ClientSession() as session:
        while len(all_results) < max_results:
            url = "https://api.openalex.org/works"
            params = {
                "search": query,
                "per-page": per_page,
                "cursor": cursor,
                "mailto": "your@email.com"  # 礼貌请求
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    break
                
                data = await response.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                all_results.extend(results)
                
                # 获取下一页 cursor
                cursor = data.get("meta", {}).get("next_cursor")
                if not cursor:
                    break
                
                # 礼貌等待
                await asyncio.sleep(0.5)
    
    return all_results[:max_results]

# 使用示例
async def main():
    papers = await search_openalex(
        query="deep learning medical imaging",
        max_results=50
    )
    
    for paper in papers:
        print(f"{paper['display_name']} - {paper.get('publication_year')}")

asyncio.run(main())
```

---

### 5. Crossref

- **URL**: https://www.crossref.org/
- **API**: https://api.crossref.org/
- **优点**: DOI 注册机构，数据权威
- **适用**: DOI 验证、元数据获取
- **速率限制**: 礼貌限制

#### API 使用示例

```python
import requests
from time import sleep

def query_crossref(doi=None, query=None, rows=20):
    """
    查询 Crossref
    
    Args:
        doi: DOI（用于精确查询）
        query: 检索词（用于模糊查询）
        rows: 结果数量
    """
    if doi:
        url = f"https://api.crossref.org/works/{doi}"
    else:
        url = "https://api.crossref.org/works"
    
    params = {}
    if query:
        params["query"] = query
        params["rows"] = rows
    
    headers = {
        "User-Agent": "LiteratureSurvey/2.0 (mailto:your@email.com)"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    # 礼貌等待
    sleep(0.1)
    
    return response.json()

# 通过 DOI 查询
data = query_crossref(doi="10.1038/nature14539")
work = data.get("message", {})
print(f"Title: {work.get('title', [''])[0]}")

# 搜索
results = query_crossref(query="deep learning", rows=10)
for work in results.get("message", {}).get("items", []):
    print(work.get("title", [""])[0])
```

---

## 检索结果评估标准

1. **相关性**: 与主题的匹配程度
2. **时效性**: 优先近5年文献
3. **影响力**: 被引次数、期刊影响因子
4. **来源质量**: 顶级会议/期刊优先
5. **可获取性**: 开放获取优先

---

## 输出格式

每篇文献记录应包含：
- 标题
- 作者列表
- 期刊/会议名称
- 年份
- DOI
- 摘要
- 被引次数
- URL
- 开放获取状态
