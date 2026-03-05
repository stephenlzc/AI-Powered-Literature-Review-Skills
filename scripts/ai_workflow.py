#!/usr/bin/env python3
"""
AI驱动的工作流主控模块

整合了:
- AI策略规划
- AI关键词提取
- 文献搜索
- 智能去重
- 引用管理
- 综述生成

特点：
- 全AI驱动决策
- 动态路径管理
- 支持交互式配置
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# 导入各模块
from config_manager import ConfigManager, load_config
from ai_strategy_planner import AIStrategyPlanner, create_strategy
from ai_keyword_extractor import AIKeywordExtractor, extract_keywords
from citation_manager import CitationManager, create_citation_manager
from session_manager import SessionManager, create_resumable_session


class AIWorkflow:
    """
    AI驱动的文献综述工作流
    
    整合了所有模块的完整工作流
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 interactive: bool = True):
        """
        初始化工作流
        
        Args:
            config_path: 配置文件路径
            interactive: 是否启用交互式配置
        """
        self.config = load_config(config_path)
        self.interactive = interactive
        
        # 初始化组件
        self.strategy_planner = AIStrategyPlanner()
        self.keyword_extractor = AIKeywordExtractor()
        self.citation_manager = None
        self.session_manager = None
        
        # 运行时状态
        self.query = ""
        self.session_id = ""
        self.strategy_plan = None
        self.keywords_result = None
        self.papers = []
    
    async def run(self, 
                  query: str,
                  year_range: Optional[tuple] = None,
                  num_papers: int = 50,
                  language: str = "both",
                  output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        运行完整工作流
        
        Args:
            query: 研究主题
            year_range: 年份范围 (start, end)
            num_papers: 期望文献数量
            language: 语言 (zh/en/both)
            output_dir: 输出目录（覆盖配置）
        
        Returns:
            工作流结果
        """
        self.query = query
        
        # 0. 配置和初始化
        print("\n" + "="*70)
        print("AI驱动的文献综述工作流 v2.0")
        print("="*70)
        
        if self.interactive:
            await self._interactive_setup()
        
        # 设置运行时变量
        self.session_id = self._generate_session_id()
        self.config.set_runtime_var("SESSION_ID", self.session_id)
        self.config.set_runtime_var("TOPIC", query[:50])
        
        if output_dir:
            self.config.set("paths.output_dir", output_dir)
        
        # 创建目录
        self.config.create_directories()
        
        # 初始化会话管理器
        self.session_manager, _ = create_resumable_session(
            query=query,
            base_dir=self.config.get_path("base_dir")
        )
        
        results = {
            "session_id": self.session_id,
            "query": query,
            "phases": {}
        }
        
        try:
            # Phase 1: AI策略规划
            print("\n[Phase 1] AI策略规划...")
            self.strategy_plan = await create_strategy(
                query=query,
                year_range=year_range or (datetime.now().year - 5, datetime.now().year),
                num_papers=num_papers
            )
            self.session_manager.save_checkpoint(
                phase=1, 
                phase_name="AI Strategy Planning",
                data={
                    "domain": self.strategy_plan.domain_analysis,
                    "databases": [db.name for db in self.strategy_plan.selected_databases],
                    "strategy": {
                        "year_range": self.strategy_plan.search_strategy.year_range,
                        "quality_threshold": self.strategy_plan.search_strategy.quality_threshold
                    }
                }
            )
            print(f"  ✓ 识别领域: {self.strategy_plan.domain_analysis.get('primary_domain')}")
            print(f"  ✓ 选择数据库: {', '.join([db.name for db in self.strategy_plan.selected_databases if db.enabled])}")
            results["phases"]["strategy_planning"] = {
                "domain": self.strategy_plan.domain_analysis.get('primary_domain'),
                "databases": [db.name for db in self.strategy_plan.selected_databases],
                "confidence": self.strategy_plan.confidence
            }
            
            # Phase 2: AI关键词提取
            print("\n[Phase 2] AI关键词提取...")
            self.keywords_result = await extract_keywords(
                query=query,
                year_range=year_range,
                target_language=language
            )
            self.session_manager.save_checkpoint(
                phase=2,
                phase_name="Keyword Extraction",
                data={
                    "keywords_zh": self.keywords_result.keywords.zh.primary,
                    "keywords_en": self.keywords_result.keywords.en.primary,
                    "search_queries": {sq.database: sq.query for sq in self.keywords_result.search_queries}
                }
            )
            print(f"  ✓ 英文关键词: {', '.join(self.keywords_result.keywords.en.primary)}")
            print(f"  ✓ 中文关键词: {', '.join(self.keywords_result.keywords.zh.primary)}")
            results["phases"]["keyword_extraction"] = {
                "en": self.keywords_result.keywords.en.primary,
                "zh": self.keywords_result.keywords.zh.primary
            }
            
            # Phase 3: 并行文献搜索（待实现具体搜索逻辑）
            print("\n[Phase 3] 并行文献搜索...")
            print("  (此阶段需要接入具体的搜索API)")
            # TODO: 实现并行搜索
            self.session_manager.save_checkpoint(
                phase=3,
                phase_name="Parallel Search",
                data={"papers_found": 0}
            )
            
            # Phase 4: 智能去重
            print("\n[Phase 4] 智能去重...")
            print("  (此阶段需要实际文献数据)")
            # TODO: 实现去重
            self.session_manager.save_checkpoint(
                phase=4,
                phase_name="Deduplication",
                data={"unique_papers": 0}
            )
            
            # Phase 5: 引用管理
            print("\n[Phase 5] 引用管理...")
            self.citation_manager = create_citation_manager(
                style="gb7714",
                cross_ref="bookmark"
            )
            # TODO: 添加文献到引用管理器
            
            # Phase 6: 综述生成（待实现）
            print("\n[Phase 6] 综述生成...")
            print("  (此阶段需要接入LLM进行撰写)")
            
            # 完成
            self.session_manager.complete_session(success=True)
            print("\n" + "="*70)
            print("工作流完成!")
            print(f"会话ID: {self.session_id}")
            print(f"输出目录: {self.config.get_path('output_dir')}")
            print("="*70)
            
            return results
            
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            self.session_manager.interrupt_session(str(e))
            raise
    
    async def _interactive_setup(self):
        """交互式配置"""
        print("\n--- 交互式配置 ---")
        
        # 检查API Keys
        required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "EXA_API_KEY"]
        missing = []
        for key in required_keys:
            if not os.getenv(key):
                missing.append(key)
        
        if missing:
            print(f"\n缺少以下API Keys: {', '.join(missing)}")
            print("您可以选择:")
            print("  1. 现在输入")
            print("  2. 跳过（部分功能将不可用）")
            choice = input("选择 (1/2): ").strip()
            
            if choice == "1":
                for key in missing:
                    value = input(f"请输入 {key}: ").strip()
                    if value:
                        os.environ[key] = value
        
        # 输出路径确认
        current_output = self.config.get_path("output_dir")
        print(f"\n当前输出路径: {current_output}")
        change = input("是否修改输出路径? (y/N): ").strip().lower()
        if change == 'y':
            new_path = input("请输入新的输出路径: ").strip()
            if new_path:
                self.config.set("paths.output_dir", new_path)
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return datetime.now().strftime("%Y%m%d") + "_" + uuid.uuid4().hex[:8]
    
    def get_output_path(self, filename_key: str) -> str:
        """获取输出文件路径"""
        return self.config.get_full_path(filename_key)
    
    def print_summary(self):
        """打印工作流摘要"""
        print("\n--- 工作流摘要 ---")
        print(f"研究主题: {self.query}")
        print(f"会话ID: {self.session_id}")
        
        if self.strategy_plan:
            print(f"识别领域: {self.strategy_plan.domain_analysis.get('primary_domain')}")
            print(f"置信度: {self.strategy_plan.confidence:.2f}")
        
        if self.keywords_result:
            print(f"\n英文关键词: {', '.join(self.keywords_result.keywords.en.primary)}")
            print(f"中文关键词: {', '.join(self.keywords_result.keywords.zh.primary)}")
        
        print(f"\n输出文件:")
        for key in ["keywords", "outline", "draft", "final"]:
            try:
                path = self.get_output_path(key)
                print(f"  {key}: {path}")
            except:
                pass


# 便捷函数
async def run_workflow(query: str,
                       year_range: Optional[tuple] = None,
                       num_papers: int = 50,
                       language: str = "both",
                       output_dir: Optional[str] = None,
                       interactive: bool = True,
                       config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    运行AI驱动的文献综述工作流
    
    Args:
        query: 研究主题
        year_range: 年份范围 (start, end)
        num_papers: 期望文献数量
        language: 语言 (zh/en/both)
        output_dir: 输出目录
        interactive: 是否启用交互式配置
        config_path: 配置文件路径
    
    Returns:
        工作流结果字典
    
    Example:
        >>> results = await run_workflow(
        ...     query="基于深度学习的医学图像诊断研究",
        ...     year_range=(2020, 2024),
        ...     num_papers=50,
        ...     interactive=True
        ... )
    """
    workflow = AIWorkflow(
        config_path=config_path,
        interactive=interactive
    )
    
    return await workflow.run(
        query=query,
        year_range=year_range,
        num_papers=num_papers,
        language=language,
        output_dir=output_dir
    )


# CLI接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI驱动的文献综述工作流")
    parser.add_argument("query", help="研究主题")
    parser.add_argument("--year-start", type=int, default=datetime.now().year - 5,
                       help="起始年份")
    parser.add_argument("--year-end", type=int, default=datetime.now().year,
                       help="结束年份")
    parser.add_argument("--num-papers", type=int, default=50,
                       help="期望文献数量")
    parser.add_argument("--language", choices=["zh", "en", "both"], default="both",
                       help="语言")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--non-interactive", action="store_true",
                       help="非交互式模式")
    
    args = parser.parse_args()
    
    async def main():
        results = await run_workflow(
            query=args.query,
            year_range=(args.year_start, args.year_end),
            num_papers=args.num_papers,
            language=args.language,
            output_dir=args.output,
            interactive=not args.non_interactive,
            config_path=args.config
        )
        
        print("\n结果摘要:")
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    asyncio.run(main())
