#!/usr/bin/env python3
"""
Literature Survey 脚本工具包 v2.0

AI驱动的学术文献综述工具集
"""

__version__ = "2.0.0"

# 核心数据模型
from .models import Paper, Author, Venue, PaperCollection

# 配置管理
from .config_manager import ConfigManager, load_config

# AI驱动模块
from .ai_strategy_planner import AIStrategyPlanner, create_strategy, StrategyPlan
from .ai_keyword_extractor import AIKeywordExtractor, extract_keywords, KeywordExtractionResult

# 引用管理
from .citation_manager import (
    CitationManager, 
    create_citation_manager,
    CitationStyle,
    CrossRefFormat
)

# 原有工具
from .keyword_extractor import KeywordExtractor, KeywordSet, QuerySet
from .citation_formatter import CitationFormatter, format_citation, format_reference_list
from .verify_references import ReferenceVerifier, VerificationResult
from .deduplicate_papers import deduplicate_papers, calculate_similarity
from .sync_zotero import export_to_zotero, format_bibtex, format_ris
from .session_manager import SessionManager, create_resumable_session

# AI工作流
from .ai_workflow import AIWorkflow, run_workflow

__all__ = [
    # 版本
    "__version__",
    
    # 数据模型
    "Paper",
    "Author",
    "Venue",
    "PaperCollection",
    
    # 配置管理
    "ConfigManager",
    "load_config",
    
    # AI驱动模块
    "AIStrategyPlanner",
    "create_strategy",
    "StrategyPlan",
    "AIKeywordExtractor",
    "extract_keywords",
    "KeywordExtractionResult",
    
    # 引用管理
    "CitationManager",
    "create_citation_manager",
    "CitationStyle",
    "CrossRefFormat",
    
    # 原有工具（向后兼容）
    "KeywordExtractor",
    "KeywordSet",
    "QuerySet",
    "CitationFormatter",
    "format_citation",
    "format_reference_list",
    "ReferenceVerifier",
    "VerificationResult",
    "deduplicate_papers",
    "calculate_similarity",
    "export_to_zotero",
    "format_bibtex",
    "format_ris",
    "SessionManager",
    "create_resumable_session",
    
    # AI工作流
    "AIWorkflow",
    "run_workflow",
]
