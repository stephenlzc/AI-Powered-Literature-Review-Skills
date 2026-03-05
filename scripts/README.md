# Literature Survey 脚本工具

本目录包含 Literature Survey Skill 的辅助脚本工具。

---

## 脚本列表

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `keyword_extractor.py` | 关键词提取与扩展 | Phase 1: 查询分析 |
| `citation_formatter.py` | 引用格式化（GB/T/BibTeX） | Phase 6: 引用导出 |
| `verify_references.py` | 引用验证 | Phase 4: 验证 |
| `deduplicate_papers.py` | 文献去重 | Phase 3: 去重 |
| `sync_zotero.py` | Zotero 导出 | Phase 6: 导出 |
| `session_manager.py` | 会话管理 | Phase 0: 会话 |

---

## 快速开始

### 统一导入

```python
from scripts import (
    KeywordExtractor,
    CitationFormatter,
    ReferenceVerifier,
    deduplicate_papers,
    export_to_zotero,
    create_resumable_session
)
```

### 完整工作流示例

```python
from scripts import (
    KeywordExtractor,
    deduplicate_papers,
    export_to_zotero,
    create_resumable_session
)

# 1. 创建可恢复会话
manager, session = create_resumable_session("基于深度学习的医学图像诊断研究")

# 2. 关键词提取
extractor = KeywordExtractor()
report = extractor.analyze(session.query, domain="medicine")
print(f"中文关键词: {report['keywords']['zh']}")
print(f"CNKI检索式: {report['search_queries']['cnki']}")

# 保存检查点
manager.save_checkpoint(1, "Query Analysis", report)

# 3. ... 进行文献检索 ...

# 4. 文献去重
# papers = [...]  # 检索到的文献
# unique_papers, removed = deduplicate_papers(papers)

# 5. 导出到 Zotero
# exported = export_to_zotero(unique_papers, formats=["bibtex", "ris"])

# 6. 完成会话
manager.complete_session(success=True)
```

---

## 各脚本详细说明

### keyword_extractor.py

从论文标题提取关键词，扩展同义词，生成多数据库检索表达式。

```python
from scripts import KeywordExtractor

extractor = KeywordExtractor(domain="medicine")
report = extractor.analyze("基于深度学习的医学图像诊断研究")

# 查看结果
print(report['keywords']['zh'])           # 中文关键词
print(report['keywords']['en'])           # 英文关键词
print(report['search_queries']['cnki'])   # CNKI检索式
print(report['search_queries']['pubmed']) # PubMed检索式
```

### citation_formatter.py

格式化文献引用，支持 GB/T 7714-2015 和 BibTeX 格式。

```python
from scripts import format_citation, format_reference_list

# 单篇格式化
citation = format_citation(paper, "E1", style="gb7714")
bibtex = format_citation(paper, "E1", style="bibtex")

# 批量格式化
citations = format_reference_list(papers, prefix="E")
```

### verify_references.py

验证文献真实性，防止幻觉引用。

```python
from scripts import ReferenceVerifier
import asyncio

async def verify():
    async with ReferenceVerifier() as verifier:
        results = await verifier.verify_papers(papers)
        for r in results:
            print(f"{r.paper_id}: {r.status.value}")

asyncio.run(verify())
```

### deduplicate_papers.py

智能文献去重，支持多层匹配策略。

```python
from scripts import deduplicate_papers

unique_papers, removed = deduplicate_papers(papers)
print(f"去重后: {len(unique_papers)} 篇")
print(f"移除重复: {len(removed)} 篇")
```

### sync_zotero.py

导出文献到 Zotero 支持的格式。

```python
from scripts import export_to_zotero

exported = export_to_zotero(
    papers,
    output_dir="./zotero_export",
    formats=["bibtex", "ris", "csl_json"]
)

print(f"BibTeX: {exported['bibtex']}")
print(f"RIS: {exported['ris']}")
```

### session_manager.py

管理文献调研会话，支持中断续传。

```python
from scripts import create_resumable_session

# 创建新会话
manager, session = create_resumable_session("研究主题")

# 或恢复已有会话
# manager, session = create_resumable_session(
#     "研究主题",
#     session_id="20240115_abc123"
# )

# 保存检查点
manager.save_checkpoint(phase=1, phase_name="Query Analysis", data={...})

# 加载检查点
checkpoint = manager.load_checkpoint(phase=1)

# 完成会话
manager.complete_session(success=True)
```

---

## 数据模型

### Paper 对象

```python
from scripts.models import Paper, Author

paper = Paper(
    id="E1",
    title="Deep learning for image recognition",
    authors=[
        Author(full_name="Yann LeCun"),
        Author(full_name="Yoshua Bengio"),
        Author(full_name="Geoffrey Hinton")
    ],
    journal="Nature",
    year=2015,
    doi="10.1038/nature14539"
)

# 转换为字典
data = paper.to_dict()

# 从字典创建
paper2 = Paper.from_dict(data)
```

### PaperCollection 对象

```python
from scripts.models import PaperCollection

collection = PaperCollection(
    session_id="20240115_dl_survey",
    query="深度学习图像识别"
)

# 添加文献
collection.add_paper(paper)

# 按条件筛选
verified = collection.filter_by_status(VerificationStatus.VERIFIED)
cn_papers = collection.filter_by_language("zh")
recent = collection.filter_by_year(2020, 2024)

# 保存/加载
collection.save_to_json("papers.json")
loaded = PaperCollection.load_from_json("papers.json")
```

---

## 工具函数

### 速率限制

```python
from scripts.utils import rate_limited, RateLimiter

@rate_limited(rate=3.0)  # 每秒最多3次
async def fetch_data():
    pass

# 或使用上下文管理器
limiter = RateLimiter(rate=1.0)
async with limiter:
    await fetch_data()
```

### 重试机制

```python
from scripts.utils import with_retry, RetryPolicy

@with_retry(max_retries=5, base_delay=2.0)
async def api_call():
    pass

# 或使用策略对象
policy = RetryPolicy(max_retries=3)
result = await policy.execute(api_call)
```

### 字符串相似度

```python
from scripts.utils import calculate_similarity

similarity = calculate_similarity("deep learning", "deep neural network")
print(f"相似度: {similarity:.2f}")  # 0.0 - 1.0
```

---

## 运行测试

```bash
# 测试关键词提取
python scripts/keyword_extractor.py

# 测试引用格式化
python scripts/citation_formatter.py

# 测试引用验证
python scripts/verify_references.py

# 测试文献去重
python scripts/deduplicate_papers.py

# 测试 Zotero 导出
python scripts/sync_zotero.py

# 测试会话管理
python scripts/session_manager.py
```

---

## 依赖安装

```bash
# 基础依赖（必需）
pip install asyncio aiohttp

# 可选依赖（增强功能）
pip install aiofiles fuzzywuzzy python-Levenshtein
```

---

## 注意事项

1. **API 密钥**：部分数据库（如 PubMed）建议使用 API Key 以提高速率限制
2. **速率限制**：遵守各数据库的速率限制，使用脚本中的 `@rate_limited` 装饰器
3. **错误处理**：使用 `@with_retry` 装饰器处理网络错误
4. **会话保存**：定期保存检查点，支持中断续传
