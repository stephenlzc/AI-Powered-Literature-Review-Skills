# Search Adapters
"""
搜索适配器模块

提供统一的搜索接口，支持多种数据源：
- exa_adapter: EXA神经网络搜索引擎
- semantic_scholar_adapter: Semantic Scholar API
- pubmed_adapter: PubMed E-utilities
- arxiv_adapter: arXiv API
- cnki_adapter: CNKI自动化检索
"""

__all__ = []

try:
    from .exa_adapter import EXAAdapter, EXASearchConfig
    __all__.extend(["EXAAdapter", "EXASearchConfig"])
except ImportError:
    pass
