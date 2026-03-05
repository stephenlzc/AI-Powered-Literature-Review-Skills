# AI LLM驱动的文献调研工作流架构设计

## 1. 架构概览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI Literature Survey System                                  │
│                              (LLM-Driven Architecture)                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         Intelligent Orchestrator                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │    │
│  │  │ LLM Router  │  │ Path Config │  │ Session Mgr │  │ Quality Gate            │  │    │
│  │  │ (流程决策)   │  │ (路径管理)   │  │ (会话管理)   │  │ (质量评估)              │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                    │
│         ┌──────────────────────────┼──────────────────────────┐                          │
│         │                          │                          │                          │
│         ▼                          ▼                          ▼                          │
│  ┌─────────────┐          ┌─────────────────┐        ┌─────────────────┐                │
│  │  LLM Query  │          │   LLM Synthesis │        │  LLM Quality    │                │
│  │  Analyzer   │          │   Engine        │        │  Evaluator      │                │
│  │             │          │                 │        │                 │                │
│  │ • 智能分词   │          │ • 主题聚类      │        │ • 文献质量评分   │                │
│  │ • 领域识别   │          │ • 综述生成      │        │ • 来源可信度    │                │
│  │ • 同义词扩展 │          │ • Gap识别       │        │ • 内容相关性    │                │
│  │ • 检索式生成 │          │ • 交叉引用      │        │ • 引用建议      │                │
│  └─────────────┘          └─────────────────┘        └─────────────────┘                │
│         │                          │                          │                          │
│         └──────────────────────────┼──────────────────────────┘                          │
│                                    │                                                    │
│         ┌──────────────────────────┼──────────────────────────┐                          │
│         │                          │                          │                          │
│         ▼                          ▼                          ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         Search Adapters (搜索适配层)                              │    │
│  │  ┌─────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │  EXA    │ │   CNKI      │ │   PubMed    │ │  Semantic   │ │   arXiv     │    │    │
│  │  │ Adapter │ │   Agent     │ │   Agent     │ │   Scholar   │ │   Agent     │    │    │
│  │  │(Neural) │ │ (Playwright)│ │   (API)     │ │   Agent     │ │   (API)     │    │    │
│  │  └─────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                                    │
│         ┌──────────────────────────┼──────────────────────────┐                          │
│         │                          │                          │                          │
│         ▼                          ▼                          ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                      Cross-Reference Engine (交叉引用引擎)                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │    │
│  │  │ Citation    │  │ Similarity  │  │ Chain       │  │ Insertion               │  │    │
│  │  │ Graph       │  │ Analysis    │  │ Analysis    │  │ Advisor                 │  │    │
│  │  │ (引用图)     │  │ (相似度分析) │  │ (引用链)     │  │ (插入建议)              │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 描述 | 实现方式 |
|------|------|----------|
| **LLM-First** | 优先使用LLM进行决策和生成 | 流程分支、关键词提取、综述生成均由LLM驱动 |
| **Adaptive** | 自适应不同研究领域 | LLM自动识别领域，动态调整策略 |
| **Configurable** | 高度可配置 | 环境变量 + 配置文件 + 运行时参数 |
| **Extensible** | 易于扩展新的数据源 | 适配器模式，统一接口 |
| **Resilient** | 容错和优雅降级 | 断路器、重试、备选方案 |

---

## 2. 关键模块设计

### 2.1 LLM Query Analyzer (查询分析器)

**替换现有的硬编码TERM_MAPPINGS**

```python
# core/query_analyzer.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class ResearchDomain(Enum):
    COMPUTER_SCIENCE = "computer_science"
    MEDICINE = "medicine"
    ECONOMICS = "economics"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    SOCIAL_SCIENCE = "social_science"
    UNKNOWN = "unknown"

@dataclass
class QueryAnalysisResult:
    """查询分析结果"""
    original_query: str
    domain: ResearchDomain
    confidence: float  # 领域识别置信度
    
    # 核心概念提取
    core_concepts: List[Dict]  # [{"concept": "深度学习", "type": "method", "importance": 0.9}]
    
    # 多语言关键词
    keywords_zh: List[str]
    keywords_en: List[str]
    
    # 同义词扩展 (LLM生成)
    synonyms_zh: Dict[str, List[str]]  # {"深度学习": ["深度神经网络", "DNN"]}
    synonyms_en: Dict[str, List[str]]  # {"deep learning": ["deep neural network"]}
    
    # 检索表达式
    search_queries: Dict[str, str]  # 各数据库检索式
    
    # 扩展建议
    related_topics: List[str]  # 相关研究方向
    suggested_databases: List[str]  # 建议检索的数据库


class LLMQueryAnalyzer:
    """
    LLM驱动的查询分析器
    
    功能：
    1. 自动识别研究领域
    2. 智能分词和概念提取
    3. 生成多语言同义词
    4. 构建优化的检索表达式
    """
    
    def __init__(self, llm_client, config: Optional[Dict] = None):
        self.llm = llm_client
        self.config = config or {}
    
    async def analyze(self, query: str, context: Optional[str] = None) -> QueryAnalysisResult:
        """分析用户查询"""
        # 使用LLM进行领域识别
        domain_result = await self._identify_domain(query, context)
        
        # 使用LLM提取核心概念
        concepts = await self._extract_concepts(query, context)
        
        # 使用LLM生成同义词
        synonyms = await self._generate_synonyms(concepts, domain_result["domain"])
        
        # 生成检索表达式
        queries = self._build_search_queries(concepts, synonyms)
        
        return QueryAnalysisResult(
            original_query=query,
            domain=ResearchDomain(domain_result["domain"]),
            confidence=domain_result["confidence"],
            core_concepts=concepts,
            keywords_zh=synonyms["zh_main"],
            keywords_en=synonyms["en_main"],
            synonyms_zh=synonyms["zh_expanded"],
            synonyms_en=synonyms["en_expanded"],
            search_queries=queries,
            related_topics=domain_result.get("related_topics", []),
            suggested_databases=domain_result.get("suggested_databases", [])
        )
    
    async def _identify_domain(self, query: str, context: Optional[str]) -> Dict:
        """使用LLM识别研究领域"""
        prompt = f"""
分析以下研究主题，识别其学科领域：

研究主题：{query}

请输出JSON格式：
{{
    "domain": "computer_science|medicine|economics|education|engineering|social_science|unknown",
    "confidence": 0.0-1.0,
    "subfield": "具体子领域",
    "reasoning": "识别理由",
    "suggested_databases": ["建议检索的数据库列表"],
    "related_topics": ["相关的研究方向"]
}}
"""
        response = await self.llm.complete(prompt, response_format="json")
        return json.loads(response)
```

**LLM Prompts设计**

```yaml
# prompts/query_analysis.yaml

domain_identification: |
  你是一个学术研究领域分析专家。请分析给定的研究主题，识别其学科领域。
  
  可选领域：
  - computer_science: 计算机科学（AI、软件工程、网络安全等）
  - medicine: 医学（临床医学、生物医学、公共卫生等）
  - economics: 经济学（金融、产业经济、国际贸易等）
  - education: 教育学（教育技术、课程设计、教育心理等）
  - engineering: 工程技术（电子、机械、土木、材料等）
  - social_science: 社会科学（社会学、政治学、心理学等）
  
  输出要求：
  1. 选择最匹配的领域
  2. 给出置信度评分(0-1)
  3. 说明识别理由
  4. 推荐适合的数据库

synonym_generation: |
  为学术检索生成同义词扩展：
  
  扩展策略：
  1. 同义词：意义相近的术语
  2. 上下位词：更广泛或更具体的概念
  3. 缩写形式：领域内常用缩写
  4. 相关术语：经常同时出现的概念
  
  注意事项：
  - 保持术语的学术规范性
  - 考虑中英文表达差异
  - 避免过于宽泛的词汇
```

### 2.2 EXA Search Adapter (EXA搜索适配器)

```python
# adapters/exa_adapter.py

from typing import List, Dict, Optional
from dataclasses import dataclass
import os

@dataclass
class EXASearchConfig:
    """EXA搜索配置"""
    api_key: str
    search_type: str = "neural"  # neural, keyword, auto
    num_results: int = 50
    use_autoprompt: bool = True
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    category: Optional[str] = "research_paper"


class EXAAdapter:
    """
    EXA神经网络搜索引擎适配器
    
    特点：
    1. 语义搜索 - 理解查询意图而非关键词匹配
    2. 相似性搜索 - 基于已有论文发现相关文献
    3. 高质量学术源 - 专注研究论文
    """
    
    def __init__(self, config: EXASearchConfig):
        self.config = config
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """初始化EXA客户端"""
        try:
            from exa_py import Exa
            return Exa(api_key=self.config.api_key)
        except ImportError:
            raise ImportError("Please install exa-py: pip install exa-py")
    
    async def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """执行EXA搜索"""
        search_params = {
            "query": query,
            "type": self.config.search_type,
            "num_results": self.config.num_results,
            "use_autoprompt": self.config.use_autoprompt,
            "category": self.config.category,
        }
        
        if self.config.include_domains:
            search_params["include_domains"] = self.config.include_domains
        
        # 执行搜索
        response = self.client.search(**search_params)
        
        # 标准化结果
        return self._normalize_results(response.results)
    
    async def search_similar(self, paper_url: str, num_results: int = 10) -> List[Dict]:
        """基于已有论文搜索相似文献"""
        response = self.client.find_similar(
            url=paper_url,
            num_results=num_results,
            category=self.config.category
        )
        return self._normalize_results(response.results)
    
    def _normalize_results(self, exa_results) -> List[Dict]:
        """将EXA结果标准化为统一Paper格式"""
        papers = []
        for idx, result in enumerate(exa_results, 1):
            paper = {
                "id": f"EX{idx}",
                "source_db": "exa",
                "paper_id": result.id,
                "title": result.title,
                "url": result.url,
                "published_date": getattr(result, 'published_date', None),
                "author": getattr(result, 'author', None),
                "score": result.score,
                "text": getattr(result, 'text', None),
                "doi": None,
                "abstract": None,
                "authors": [],
                "year": None,
                "venue": None,
            }
            papers.append(paper)
        return papers
```

### 2.3 Cross-Reference Engine (交叉引用引擎)

```python
# core/cross_reference_engine.py

from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import networkx as nx

@dataclass
class CitationSuggestion:
    """引用建议"""
    paper_id: str
    reason: str
    relevance_score: float
    suggested_position: str
    suggested_context: str


class CrossReferenceEngine:
    """
    智能交叉引用引擎
    
    功能：
    1. 构建引用图
    2. 分析引用关系
    3. 推荐相关文献
    4. 建议引用位置
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.citation_graph = nx.DiGraph()
    
    def build_citation_graph(self, papers: List[Dict]) -> nx.DiGraph:
        """构建引用关系图"""
        G = nx.DiGraph()
        
        # 添加节点
        for paper in papers:
            G.add_node(paper["id"], **paper)
        
        # 添加边
        for paper in papers:
            if "references" in paper:
                for ref_id in paper["references"]:
                    if ref_id in G.nodes:
                        G.add_edge(paper["id"], ref_id)
        
        self.citation_graph = G
        return G
    
    async def recommend_citations(
        self, 
        section_text: str, 
        available_papers: List[Dict],
        current_citations: List[str]
    ) -> List[CitationSuggestion]:
        """智能引用推荐"""
        suggestions = []
        topics = await self._extract_topics(section_text)
        
        for paper in available_papers:
            if paper["id"] in current_citations:
                continue
            
            similarity = await self._calculate_relevance(section_text, paper, topics)
            
            if similarity > 0.6:
                reason = await self._generate_citation_reason(section_text, paper)
                context = await self._suggest_insertion_context(section_text, paper)
                
                suggestions.append(CitationSuggestion(
                    paper_id=paper["id"],
                    reason=reason,
                    relevance_score=similarity,
                    suggested_position=self._detect_section(section_text),
                    suggested_context=context
                ))
        
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        return suggestions[:5]
    
    def detect_citation_gaps(self, papers: List[Dict]) -> List[Dict]:
        """检测引用缺失"""
        G = self.citation_graph
        gaps = []
        all_cited = set()
        
        for paper in papers:
            if "references" in paper:
                all_cited.update(paper["references"])
        
        for cited_id in all_cited:
            if cited_id not in [p["id"] for p in papers]:
                citation_count = sum(
                    1 for p in papers if cited_id in p.get("references", [])
                )
                if citation_count >= 2:
                    gaps.append({
                        "paper_id": cited_id,
                        "cited_by_count": citation_count,
                        "suggestion": f"被{citation_count}篇论文引用，建议获取"
                    })
        
        return sorted(gaps, key=lambda x: x["cited_by_count"], reverse=True)
```

### 2.4 Path Configuration Manager (路径配置管理器)

```python
# core/path_config.py

import os
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class PathConfig:
    """路径配置"""
    base_output_dir: Path
    sessions_dir: Path
    cache_dir: Path
    temp_dir: Path
    pdfs_dir: Path
    metadata_dir: Path
    checkpoints_dir: Path
    results_dir: Path
    
    @classmethod
    def from_env(cls) -> "PathConfig":
        """从环境变量加载配置"""
        base_dir = Path(
            os.getenv("LIT_SURVEY_BASE_DIR", "./literature-survey-output")
        )
        
        sessions_dir = Path(os.getenv("LIT_SURVEY_SESSIONS_DIR", base_dir / "sessions"))
        cache_dir = Path(os.getenv("LIT_SURVEY_CACHE_DIR", base_dir / ".cache"))
        temp_dir = Path(os.getenv("LIT_SURVEY_TEMP_DIR", base_dir / ".temp"))
        
        return cls(
            base_output_dir=base_dir,
            sessions_dir=sessions_dir,
            cache_dir=cache_dir,
            temp_dir=temp_dir,
            pdfs_dir=sessions_dir / "pdfs",
            metadata_dir=sessions_dir / "metadata",
            checkpoints_dir=sessions_dir / "checkpoints",
            results_dir=sessions_dir / "results"
        )
    
    def ensure_directories(self):
        """确保所有目录存在"""
        for dir_path in [
            self.sessions_dir, self.cache_dir, self.temp_dir,
            self.pdfs_dir, self.metadata_dir, self.checkpoints_dir, self.results_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def resolve_path(self, path: str, session_id: Optional[str] = None) -> Path:
        """解析路径（支持变量替换）"""
        resolved = path
        
        replacements = {
            "{base_dir}": str(self.base_output_dir),
            "{sessions_dir}": str(self.sessions_dir),
            "{cache_dir}": str(self.cache_dir),
            "{temp_dir}": str(self.temp_dir),
        }
        
        if session_id:
            replacements["{session_id}"] = session_id
        
        for old, new in replacements.items():
            resolved = resolved.replace(old, new)
        
        return Path(resolved)
```

---

## 3. 配置文件结构

### 3.1 主配置文件 (config.yaml)

```yaml
# literature-survey/config.yaml

# ==================== 系统配置 ====================
system:
  name: "AI Literature Survey System"
  version: "2.0.0"
  debug: false
  log_level: "INFO"
  
# ==================== 路径配置 ====================
paths:
  base_dir: "${LIT_SURVEY_BASE_DIR:-./literature-survey-output}"
  sessions_dir: "${LIT_SURVEY_SESSIONS_DIR:-{base_dir}/sessions}"
  cache_dir: "${LIT_SURVEY_CACHE_DIR:-{base_dir}/.cache}"
  temp_dir: "${LIT_SURVEY_TEMP_DIR:-{base_dir}/.temp}"
  pdfs_dir: "${LIT_SURVEY_PDFS_DIR:-{sessions_dir}/pdfs}"
  metadata_dir: "${LIT_SURVEY_METADATA_DIR:-{sessions_dir}/metadata}"
  checkpoints_dir: "${LIT_SURVEY_CHECKPOINTS_DIR:-{sessions_dir}/checkpoints}"
  results_dir: "${LIT_SURVEY_RESULTS_DIR:-{sessions_dir}/results}"

# ==================== LLM配置 ====================
llm:
  default_provider: "openai"
  
  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      base_url: "${OPENAI_BASE_URL:-https://api.openai.com/v1}"
      default_model: "gpt-4o"
      fallback_model: "gpt-4o-mini"
      
    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      default_model: "claude-3-5-sonnet-20241022"
  
  model_selection:
    query_analysis: "gpt-4o"
    synthesis: "gpt-4o"
    quality_check: "gpt-4o-mini"

# ==================== 搜索配置 ====================
search:
  default_strategy: "parallel"
  
  exa:
    enabled: true
    api_key: "${EXA_API_KEY}"
    search_type: "neural"
    num_results: 50
    use_autoprompt: true
    category: "research_paper"
    include_domains:
      - "arxiv.org"
      - "pubmed.ncbi.nlm.nih.gov"
      - "semanticscholar.org"
    
  databases:
    semantic_scholar:
      enabled: true
      rate_limit: 100
      
    pubmed:
      enabled: true
      api_key: "${PUBMED_API_KEY}"
      email: "${PUBMED_EMAIL}"
      rate_limit: 3
      
    cnki:
      enabled: true
      headless: false
      timeout: 300

# ==================== 处理配置 ====================
processing:
  deduplication:
    title_similarity_threshold: 0.85
    metadata_match_threshold: 0.9
    
  quality:
    min_citations: 5
    year_range: [2020, null]
    
  concurrency:
    max_parallel_search: 5
    max_parallel_download: 3

# ==================== 输出配置 ====================
output:
  citation_formats:
    - "gb7714"
    - "bibtex"
    - "apa"
    
  export_formats:
    - "markdown"
    - "docx"
    - "json"
    
  synthesis:
    template: "standard"
    target_word_count: 3000
```

### 3.2 环境变量模板 (.env.example)

```bash
# ============================================
# AI Literature Survey - Environment Variables
# ============================================

# ----- 基础路径配置 -----
# LIT_SURVEY_BASE_DIR=./literature-survey-output
# LIT_SURVEY_SESSIONS_DIR=./literature-survey-output/sessions

# ----- LLM API Keys -----
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# ----- 搜索服务 API Keys -----
EXA_API_KEY=exa-...
PUBMED_API_KEY=...
PUBMED_EMAIL=your-email@example.com
IEEE_API_KEY=...

# ----- 代理配置 -----
# HTTP_PROXY=http://proxy.example.com:8080
```

---

## 4. EXA搜索集成方案

### 4.1 EXA与传统数据库的协同策略

```
┌─────────────────────────────────────────────────────────────────┐
│                    智能搜索 orchestrator                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Phase 1: EXA语义发现                                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 输入: 自然语言研究主题                                     │   │
│   │ 输出: 高相关度文献集合 (50篇)                               │   │
│   │ 特点: 理解语义，发现意外相关文献                             │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│   Phase 2: 传统数据库补充                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 基于EXA结果生成优化查询                                     │   │
│   │ 在Semantic Scholar/PubMed/arXiv中检索                      │   │
│   │ 获取完整元数据（DOI、引用数、PDF链接）                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│   Phase 3: 相似性扩展                                            │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 对高质量文献使用EXA find_similar                          │   │
│   │ 发现更多相关但可能遗漏的文献                                │   │
│   │ 特别适用于找到"seed paper"后扩展                            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│   Phase 4: 中文文献检索 (CNKI)                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 使用LLM生成的中文关键词                                     │   │
│   │ CNKI高级检索                                              │   │
│   │ 补充中文学术视角                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 完整EXA Adapter

```python
# adapters/exa_adapter.py (完整版)

class EXAAdapter:
    """EXA神经网络搜索引擎适配器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get("api_key") or os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("EXA API key is required")
        self._init_client()
    
    def _init_client(self):
        try:
            from exa_py import Exa
            self.client = Exa(api_key=self.api_key)
        except ImportError:
            raise ImportError("exa-py is required: pip install exa-py")
    
    async def discover(
        self, 
        research_topic: str,
        num_results: int = 50,
        year_range: Optional[tuple] = None
    ) -> List[Dict]:
        """EXA神经网络搜索"""
        params = {
            "query": research_topic,
            "type": self.config.get("search_type", "neural"),
            "num_results": num_results,
            "use_autoprompt": self.config.get("use_autoprompt", True),
            "category": self.config.get("category", "research_paper"),
            "text": True,
            "highlights": True,
        }
        
        if year_range:
            if year_range[0]:
                params["start_published_date"] = f"{year_range[0]}-01-01"
            if year_range[1]:
                params["end_published_date"] = f"{year_range[1]}-12-31"
        
        if self.config.get("include_domains"):
            params["include_domains"] = self.config["include_domains"]
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.search_and_contents(**params)
        )
        
        return self._normalize_results(response.results)
    
    async def expand_similar(
        self,
        seed_papers: List[Dict],
        num_results_per_paper: int = 5
    ) -> List[Dict]:
        """基于种子文献发现相似文献"""
        all_results = []
        
        for paper in seed_papers:
            if not paper.get("url"):
                continue
            
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.find_similar(
                        url=paper["url"],
                        num_results=num_results_per_paper,
                        category=self.config.get("category", "research_paper"),
                        text=True
                    )
                )
                
                similar_papers = self._normalize_results(response.results)
                for p in similar_papers:
                    p["discovered_from"] = paper.get("id")
                    p["similarity_source"] = "exa_find_similar"
                
                all_results.extend(similar_papers)
            except Exception as e:
                print(f"Error finding similar: {e}")
        
        return all_results
```

---

## 5. 工作流程集成

### 5.1 新的8阶段AI驱动工作流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI-Driven 8-Phase Workflow                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 0: Session Initialization                                            │
│  ├── 加载环境配置                                                            │
│  ├── 创建会话目录（可配置路径）                                               │
│  └── 初始化日志                                                              │
│                                                                             │
│  Phase 1: Intelligent Query Analysis (LLM驱动)                              │
│  ├── LLM识别研究领域                                                         │
│  ├── 智能分词和概念提取                                                       │
│  ├── 多语言同义词扩展（LLM生成）                                              │
│  └── 生成优化的检索表达式（各数据库适配）                                       │
│                                                                             │
│  Phase 2: Hybrid Search (EXA + 传统数据库)                                   │
│  ├── EXA神经网络搜索（语义理解）                                              │
│  ├── 传统数据库并行搜索（精确匹配）                                           │
│  ├── 相似性扩展（基于EXA find_similar）                                       │
│  └── 结果合并与去重                                                          │
│                                                                             │
│  Phase 3: AI-Assisted Deduplication                                          │
│  ├── 基于规则快速去重（DOI、标题相似度）                                       │
│  ├── LLM辅助模糊去重（处理变体标题）                                          │
│  └── 质量评分和排序                                                          │
│                                                                             │
│  Phase 4: Intelligent Verification (LLM评估)                                 │
│  ├── 多源验证（Crossref, OpenAlex等）                                        │
│  ├── LLM评估文献质量（相关性、可信度）                                        │
│  ├── 撤稿检测                                                                │
│  └── 元数据补全                                                              │
│                                                                             │
│  Phase 5: Cross-Reference Analysis                                           │
│  ├── 构建引用关系图                                                          │
│  ├── 分析引用链（前向/后向）                                                  │
│  ├── 识别引用缺失                                                            │
│  └── 生成引用推荐                                                            │
│                                                                             │
│  Phase 6: PDF Management                                                     │
│  ├── 开放获取检查（Unpaywall）                                               │
│  ├── PDF下载                                                                  │
│  └── 本地文献库管理                                                           │
│                                                                             │
│  Phase 7: LLM Synthesis (AI生成综述)                                         │
│  ├── LLM主题聚类                                                             │
│  ├── 智能综述段落生成                                                         │
│  ├── 自动插入交叉引用                                                         │
│  ├── 国内外研究对比                                                           │
│  └── LLM识别研究Gap                                                          │
│                                                                             │
│  Phase 8: Export & Integration                                               │
│  ├── 多格式引用导出（GB7714, BibTeX等）                                       │
│  ├── Word文档生成（含交叉引用）                                               │
│  └── Zotero同步（可选）                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. 架构优势总结

| 方面 | 传统架构 | AI驱动架构 |
|------|---------|-----------|
| **关键词提取** | 硬编码词表，覆盖有限 | LLM智能分词，自适应扩展 |
| **领域识别** | 用户指定或规则匹配 | LLM自动识别，置信度评估 |
| **搜索策略** | 固定布尔检索 | EXA语义搜索 + 传统检索互补 |
| **去重** | 基于规则 | 规则 + LLM辅助模糊匹配 |
| **综述生成** | 模板填充 | LLM生成，逻辑连贯 |
| **交叉引用** | 手动插入 | 智能推荐，自动定位 |
| **路径管理** | 硬编码绝对路径 | 环境变量 + 动态解析 |

### 实施建议

1. **分阶段实施**
   - 阶段1: 路径管理优化 + EXA集成
   - 阶段2: LLM查询分析器
   - 阶段3: LLM综述生成
   - 阶段4: 交叉引用引擎

2. **向后兼容**
   - 保留传统关键词提取作为fallback
   - 支持配置开关启用/禁用LLM功能
   - 渐进式迁移现有会话

3. **性能优化**
   - LLM调用使用缓存
   - 并行处理独立任务
   - 结果增量保存
