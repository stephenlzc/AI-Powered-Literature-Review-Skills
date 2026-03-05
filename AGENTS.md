# AGENTS.md - Literature Survey Skill

## 项目概述

本项目是一个 **Kimi CLI Skill**（技能插件），名为 `literature-survey`，用于帮助用户进行系统性的学术文献回顾（Literature Survey）。

**版本**: 2.0.0  
**最后更新**: 2024-01

### 核心特性

- **8阶段工作流**：完整的文献调研流程
- **Agent Swarm 架构**：并行多数据库检索
- **引用验证机制**：防止幻觉引用
- **多数据库支持**：17+ 中英文学术平台
- **多格式输出**：GB/T 7714-2015、BibTeX、RIS、Zotero

---

## 技术栈

- **语言**: Python 3.8+
- **架构**: Agent Swarm 并行架构
- **异步**: asyncio + aiohttp
- **外部依赖**:
  - Kimi CLI 的 `docx` skill
  - Kimi CLI 的 `pdf` skill
  - Playwright（CNKI 浏览器自动化）

---

## 项目结构

```
literature-survey/
├── SKILL.md                          # Skill 定义文件（主入口）
├── AGENTS.md                         # 本文件
├── README.md                         # 项目说明文档
│
├── agents/                           # Agent 模板目录
│   ├── explore-agent.md              # 搜索 Agent 模板
│   ├── verify-agent.md               # 验证 Agent 模板
│   ├── download-agent.md             # 下载 Agent 模板
│   ├── synthesize-agent.md           # 综述 Agent 模板
│   └── orchestrator.md               # 协调器 Agent 模板
│
├── scripts/                          # Python 辅助脚本
│   ├── __init__.py                   # 包初始化
│   ├── models.py                     # 统一数据模型（Paper、Author等）
│   ├── utils.py                      # 工具函数（速率限制、重试等）
│   ├── keyword_extractor.py          # 关键词提取与扩展（增强版）
│   ├── citation_formatter.py         # 引用格式化（GB/T/BibTeX）
│   ├── verify_references.py          # 引用验证（DOI/Crossref）
│   ├── deduplicate_papers.py         # 文献去重（多层策略）
│   ├── sync_zotero.py                # Zotero 导出
│   └── session_manager.py            # 会话管理（中断续传）
│
├── references/                       # 参考资料文档
│   ├── cnki-guide.md                 # CNKI 检索详细指南
│   ├── english-search-guide.md       # 英文数据库检索指南
│   ├── gb-t-7714-2015.md             # GB/T 7714-2015 引用格式规范
│   ├── database-apis.md              # 各数据库 API 参考（新增）
│   └── workflow-templates.md         # 工作流模板（新增）
│
└── assets/                           # 资源目录（预留）
```

---

## 8阶段工作流

### Phase 0: Session Log
创建会话目录，初始化日志，支持中断续传。

**输出**:
- `sessions/{session_id}/session_log.md`
- `sessions/{session_id}/metadata.json`

### Phase 1: Query Analysis
关键词提取、同义词扩展、检索式构建。

**工具**: `scripts/keyword_extractor.py`

**输出**:
- `checkpoints/checkpoint_p1.json`
- 关键词列表（中英文）
- 各数据库检索表达式

### Phase 2: Parallel Search
多数据库并行检索。

**Agent**: Explore Agent

**数据库**:
- 中文: CNKI
- 英文: Semantic Scholar, PubMed, arXiv, IEEE Xplore, OpenAlex

**输出**:
- 原始搜索结果（JSON）

### Phase 3: Deduplication
多层去重策略。

**工具**: `scripts/deduplicate_papers.py`

**策略**:
1. DOI 精确匹配
2. 标题相似度匹配（>0.85）
3. 作者+年份+期刊匹配

**输出**:
- 去重后的文献列表
- 去重报告

### Phase 4: Verification
引用验证，防止幻觉引用。

**Agent**: Verify Agent  
**工具**: `scripts/verify_references.py`

**验证源**:
- Crossref（首选）
- Semantic Scholar
- OpenAlex
- PubMed（医学）

**验证状态**:
- VERIFIED: 多源确认
- SINGLE_SOURCE: 单源确认
- PREPRINT: 预印本
- RETRACTED: 已撤稿
- NOT_FOUND: 未找到

### Phase 5: PDF Management
PDF 下载和管理。

**Agent**: Download Agent

**优先级**:
1. 直接 PDF 链接
2. Unpaywall API
3. 预印本服务器（arXiv等）
4. 机构访问

### Phase 6: Citation Export
引用格式化导出。

**工具**: `scripts/citation_formatter.py`, `scripts/sync_zotero.py`

**支持格式**:
- GB/T 7714-2015
- BibTeX（Better BibTeX风格）
- RIS
- CSL JSON

### Phase 7: Synthesis
综述生成。

**Agent**: Synthesize Agent

**功能**:
- 主题聚类
- 趋势分析
- Gap 识别
- 交叉引用生成

---

## Agent Swarm 架构

### 协调器（Orchestrator）

负责整体工作流协调，管理 Session Log，调度子 Agent。

**职责**:
- 任务队列管理
- 并行 Agent 调度
- 错误恢复
- 检查点保存

### 搜索 Agent（Explore Agent）

负责在特定数据库执行检索。

**实例**:
- CNKI Agent
- Semantic Scholar Agent
- PubMed Agent
- arXiv Agent
- IEEE Agent

**输入**: 检索表达式、筛选条件  
**输出**: 结构化文献列表

### 验证 Agent（Verify Agent）

负责验证文献真实性和补全元数据。

**验证规则**:
- 每个引用必须通过至少一个验证源确认
- 预印本检查（查找发表版本）
- 撤稿检测

### 下载 Agent（Download Agent）

负责 PDF 下载。

**优先级策略**:
1. 直接链接
2. Unpaywall
3. 预印本服务器
4. 机构访问

### 综述 Agent（Synthesize Agent）

负责生成综述内容。

**功能**:
- 主题聚类
- 趋势分析
- Gap 识别
- 交叉引用生成

---

## 代码规范

### Python 脚本规范

1. **文件头**
   ```python
   #!/usr/bin/env python3
   """
   模块功能描述
   """
   ```

2. **类型注解**
   ```python
   from typing import List, Dict, Optional
   
   def format_citation(paper: Dict, index: int, lang: str = 'auto') -> str:
   ```

3. **文档字符串**
   ```python
   def extract_keywords(title: str) -> Dict[str, List[str]]:
       """
       从标题中提取关键词
       
       Args:
           title: 论文标题
       
       Returns:
           包含中文和英文关键词的字典
       """
   ```

4. **命名规范**
   - 类名: `PascalCase`（如 `KeywordExtractor`）
   - 函数/变量: `snake_case`（如 `format_citation`）
   - 常量: `UPPER_CASE`（如 `TERM_MAPPINGS`）

5. **注释语言**: 中文

### 文献引用规范

- **中文文献编号**: 以 `C` 开头（C1, C2, C3...）
- **英文文献编号**: 以 `E` 开头（E1, E2, E3...）
- **引用格式**: 严格遵循 GB/T 7714-2015 标准
- **BibTeX 密钥**: Better BibTeX 格式（AuthorYearTitle）

---

## 脚本使用说明

### keyword_extractor.py

```python
from scripts import KeywordExtractor

extractor = KeywordExtractor()
report = extractor.analyze("基于深度学习的医学图像诊断研究", domain="medicine")

print(f"中文关键词: {report['keywords']['zh']}")
print(f"CNKI检索式: {report['search_queries']['cnki']}")
```

### citation_formatter.py

```python
from scripts import CitationFormatter, format_citation

# 使用便捷函数
citation = format_citation(paper, "E1", style="gb7714")

# 使用格式化器实例
formatter = CitationFormatter()
citations = formatter.format_list(papers, prefix="E")
```

### verify_references.py

```python
from scripts import ReferenceVerifier

async with ReferenceVerifier() as verifier:
    results = await verifier.verify_papers(papers)
    for r in results:
        print(f"{r.paper_id}: {r.status.value}")
```

### deduplicate_papers.py

```python
from scripts import deduplicate_papers

unique_papers, removed = deduplicate_papers(papers)
print(f"去重后: {len(unique_papers)} 篇")
```

### sync_zotero.py

```python
from scripts import export_to_zotero

exported = export_to_zotero(
    papers,
    output_dir="./zotero_export",
    formats=["bibtex", "ris"]
)
```

### session_manager.py

```python
from scripts import create_resumable_session

manager, metadata = create_resumable_session("研究主题")
manager.save_checkpoint(1, "Query Analysis", data)
```

---

## 开发注意事项

1. **异步编程**: 使用 `asyncio` 进行并发处理
2. **速率限制**: 遵守各数据库的速率限制
3. **错误处理**: 使用重试机制和错误恢复
4. **会话管理**: 定期保存检查点
5. **依赖管理**: 可选依赖使用 try/except 处理

---

## 修改历史

### v2.0.0 (2024-01)
- 重构为 8阶段工作流
- 引入 Agent Swarm 架构
- 新增引用验证机制
- 新增多数据库支持
- 新增会话管理（中断续传）
- 新增 Zotero 同步
- 重构所有脚本，统一数据模型

### v1.0.0 (2023)
- 初始版本
- 基础的关键词提取
- 基础的引用格式化
- CNKI 检索指南
