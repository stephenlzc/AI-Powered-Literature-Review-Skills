# AI Literature Survey Core Modules
"""
AI驱动的文献调研核心模块

包含以下组件：
- query_analyzer: LLM查询分析器
- path_config: 路径配置管理器
- cross_reference_engine: 交叉引用引擎
- synthesis_engine: LLM综述生成引擎
- workflow: 主工作流
"""

__version__ = "2.0.0"

from .path_config import PathConfig, RuntimePathResolver

__all__ = [
    "PathConfig",
    "RuntimePathResolver",
]
