#!/usr/bin/env python3
"""
EXA神经网络搜索引擎适配器

EXA (https://exa.ai) 是一个AI原生的神经网络搜索引擎，
使用语义嵌入而非关键词匹配来检索相关学术文献。

特点：
1. 语义搜索 - 理解查询意图而非关键词匹配
2. 相似性搜索 - 基于已有论文发现相关文献
3. 高质量学术源 - 专注研究论文
4. 支持结构化内容提取

安装依赖：
    pip install exa-py

获取API Key：
    https://dashboard.exa.ai/api-keys
"""

import os
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class EXASearchConfig:
    """EXA搜索配置"""
    api_key: str
    search_type: str = "neural"  # neural, keyword, auto
    num_results: int = 50
    use_autoprompt: bool = True
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    category: Optional[str] = "research_paper"  # research_paper, news, etc.
    start_published_date: Optional[str] = None
    end_published_date: Optional[str] = None


class EXAAdapter:
    """
    EXA神经网络搜索引擎适配器
    
    使用示例：
        config = EXASearchConfig(
            api_key=os.getenv("EXA_API_KEY"),
            search_type="neural",
            num_results=50
        )
        adapter = EXAAdapter(config)
        
        # 语义搜索
        results = await adapter.discover(
            "Recent advances in transformer architectures for medical image analysis"
        )
        
        # 相似性扩展
        similar = await adapter.expand_similar([seed_paper])
    """
    
    def __init__(self, config: EXASearchConfig):
        """
        初始化EXA适配器
        
        Args:
            config: EXA搜索配置
        
        Raises:
            ValueError: 如果没有提供API key
            ImportError: 如果没有安装exa-py
        """
        self.config = config
        self.api_key = config.api_key or os.getenv("EXA_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "EXA API key is required. "
                "Get one at https://dashboard.exa.ai/api-keys"
            )
        
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化EXA客户端"""
        try:
            from exa_py import Exa
            self.client = Exa(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "exa-py is required. Install with: pip install exa-py"
            )
    
    async def discover(
        self, 
        research_topic: str,
        num_results: Optional[int] = None,
        year_range: Optional[Tuple[int, int]] = None
    ) -> List[Dict]:
        """
        EXA神经网络搜索 - 发现相关文献
        
        这是主要的搜索方法，使用自然语言描述而非布尔逻辑。
        EXA的神经网络会理解查询的语义含义，返回概念相关的文献。
        
        Args:
            research_topic: 自然语言研究主题描述
            num_results: 返回结果数量（覆盖配置中的默认值）
            year_range: (start_year, end_year) 时间范围筛选
        
        Returns:
            标准化的文献列表，每个文献包含：
            - id: 内部ID
            - source_db: "exa"
            - title: 标题
            - url: 原文链接
            - exa_score: 相关度分数
            - published_date: 发表日期
            - author: 作者
            - text: 内容片段（如请求）
        
        Example:
            results = await adapter.discover(
                "Transformer attention mechanisms for computer vision",
                num_results=30,
                year_range=(2020, 2024)
            )
        """
        search_params = {
            "query": research_topic,
            "type": self.config.search_type,
            "num_results": num_results or self.config.num_results,
            "use_autoprompt": self.config.use_autoprompt,
            "category": self.config.category,
            "text": True,  # 获取文本内容
            "highlights": True,  # 获取高亮片段
        }
        
        # 添加时间范围
        if year_range:
            if year_range[0]:
                search_params["start_published_date"] = f"{year_range[0]}-01-01"
            if year_range[1]:
                search_params["end_published_date"] = f"{year_range[1]}-12-31"
        
        # 添加域名过滤
        if self.config.include_domains:
            search_params["include_domains"] = self.config.include_domains
        if self.config.exclude_domains:
            search_params["exclude_domains"] = self.config.exclude_domains
        
        # 执行搜索（在线程池中运行同步SDK）
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.search_and_contents(**search_params)
        )
        
        return self._normalize_results(response.results)
    
    async def expand_similar(
        self,
        seed_papers: List[Dict],
        num_results_per_paper: int = 5
    ) -> List[Dict]:
        """
        相似性扩展 - 基于种子文献发现更多相关文献
        
        这是EXA的强大功能：给定一篇或多篇高质量文献，
        可以找到语义相似的其他文献，常用于：
        - 基于关键论文扩展检索
        - 发现遗漏的相关研究
        - 构建文献网络
        
        Args:
            seed_papers: 种子文献列表，每个需要包含 "url" 字段
            num_results_per_paper: 每篇种子文献返回的相似文献数
        
        Returns:
            扩展的文献列表，每篇标记了 discovered_from 来源
        
        Example:
            # 先获取种子论文
            seeds = await adapter.discover("attention mechanism", num_results=5)
            
            # 基于种子扩展
            expanded = await adapter.expand_similar(seeds, num_results_per_paper=3)
        """
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
                        category=self.config.category,
                        text=True
                    )
                )
                
                similar_papers = self._normalize_results(response.results)
                
                # 标记来源
                for p in similar_papers:
                    p["discovered_from"] = paper.get("id")
                    p["similarity_source"] = "exa_find_similar"
                
                all_results.extend(similar_papers)
                
            except Exception as e:
                print(f"Error finding similar papers for {paper.get('id')}: {e}")
                continue
        
        # 去重
        seen_urls = set()
        unique_results = []
        for p in all_results:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                unique_results.append(p)
        
        return unique_results
    
    async def iterative_search(
        self,
        initial_query: str,
        llm_client,
        max_iterations: int = 3,
        target_papers: int = 100
    ) -> Dict:
        """
        迭代搜索 - 自动优化查询并扩展结果
        
        流程：
        1. 初始EXA搜索
        2. LLM评估结果质量
        3. 如果质量不够，生成优化查询
        4. 重复直到达到目标
        
        Args:
            initial_query: 初始研究主题
            llm_client: LLM客户端，用于评估和优化
            max_iterations: 最大迭代次数
            target_papers: 目标文献数量
        
        Returns:
            {
                "papers": 收集的所有文献,
                "iterations": 实际迭代次数,
                "final_query": 最终使用的查询,
                "quality_score": 结果质量评分
            }
        """
        all_papers = []
        iteration = 0
        current_query = initial_query
        
        while iteration < max_iterations and len(all_papers) < target_papers:
            # 搜索
            results = await self.discover(
                current_query,
                num_results=min(50, target_papers - len(all_papers))
            )
            
            # 去重并添加
            new_papers = self._filter_duplicates(results, all_papers)
            all_papers.extend(new_papers)
            
            # LLM评估
            if len(all_papers) < target_papers and iteration < max_iterations - 1:
                evaluation = await self._evaluate_with_llm(
                    llm_client,
                    initial_query,
                    all_papers
                )
                
                if evaluation["quality_score"] >= 0.8:
                    break  # 质量足够
                
                # 生成优化查询
                current_query = await self._refine_query(
                    llm_client,
                    initial_query,
                    current_query,
                    evaluation["gaps"]
                )
            
            iteration += 1
        
        return {
            "papers": all_papers,
            "iterations": iteration,
            "final_query": current_query,
            "queries_tried": []
        }
    
    def _normalize_results(self, exa_results) -> List[Dict]:
        """
        将EXA结果标准化为统一Paper格式
        
        Args:
            exa_results: EXA API返回的结果
        
        Returns:
            标准化的文献字典列表
        """
        papers = []
        for idx, result in enumerate(exa_results, 1):
            # 从URL提取可能的DOI
            doi = self._extract_doi_from_url(result.url)
            
            # 解析年份
            year = None
            pub_date = getattr(result, 'published_date', None)
            if pub_date:
                year_match = re.search(r'(\d{4})', str(pub_date))
                if year_match:
                    year = int(year_match.group(1))
            
            paper = {
                "id": f"EX{idx:03d}",
                "source_db": "exa",
                "exa_id": result.id,
                "title": result.title,
                "url": result.url,
                "doi": doi,
                "published_date": pub_date,
                "year": year,
                "author": getattr(result, 'author', None),
                "exa_score": result.score,
                "abstract": getattr(result, 'text', None),
                "highlights": getattr(result, 'highlights', []),
                
                # 待后续验证补全的字段
                "authors": [],
                "venue": None,
                "citation_count": None,
                "references": [],
            }
            papers.append(paper)
        
        return papers
    
    def _extract_doi_from_url(self, url: str) -> Optional[str]:
        """从URL中提取DOI"""
        if not url:
            return None
        
        doi_pattern = r'10\.\d{4,}/[^\s"<>]+'
        match = re.search(doi_pattern, url)
        return match.group(0) if match else None
    
    def _filter_duplicates(
        self,
        new_papers: List[Dict],
        existing_papers: List[Dict]
    ) -> List[Dict]:
        """过滤重复文献"""
        existing_urls = {p["url"] for p in existing_papers}
        return [p for p in new_papers if p["url"] not in existing_urls]
    
    async def _evaluate_with_llm(
        self,
        llm_client,
        original_query: str,
        papers: List[Dict]
    ) -> Dict:
        """使用LLM评估搜索结果质量"""
        # 准备样本
        sample_papers = papers[:10]
        papers_summary = "\n".join([
            f"- {p['title']} ({p.get('year', 'N/A')})"
            for p in sample_papers
        ])
        
        prompt = f"""
评估以下文献搜索结果的相关性和多样性：

原始查询：{original_query}

找到的文献样本（共{len(papers)}篇）：
{papers_summary}

请评估：
1. 整体相关性（0-1分）
2. 覆盖的方面
3. 遗漏的方面
4. 建议的改进

输出JSON格式：
{{
    "quality_score": 0.0-1.0,
    "coverage": ["已覆盖的方面"],
    "gaps": ["遗漏的方面"],
    "suggestion": "改进建议"
}}
"""
        response = await llm_client.complete(prompt, response_format="json")
        import json
        return json.loads(response)
    
    async def _refine_query(
        self,
        llm_client,
        original_query: str,
        current_query: str,
        gaps: List[str]
    ) -> str:
        """生成优化查询"""
        prompt = f"""
基于搜索反馈，优化EXA搜索查询：

原始查询：{original_query}
当前查询：{current_query}
发现的问题：{', '.join(gaps)}

请生成一个改进的自然语言查询，以：
1. 覆盖遗漏的方面
2. 保持学术专业性
3. 适合神经网络搜索引擎

只输出优化后的查询语句，不要其他内容。
"""
        return await llm_client.complete(prompt)


# 便捷函数
def create_exa_adapter_from_config(config: Dict) -> EXAAdapter:
    """
    从配置字典创建EXA适配器
    
    Args:
        config: 配置字典，应包含 exa 部分的配置
    
    Returns:
        EXAAdapter实例
    """
    exa_config = EXASearchConfig(
        api_key=config.get("api_key") or os.getenv("EXA_API_KEY"),
        search_type=config.get("search_type", "neural"),
        num_results=config.get("num_results", 50),
        use_autoprompt=config.get("use_autoprompt", True),
        category=config.get("category", "research_paper"),
        include_domains=config.get("include_domains"),
    )
    return EXAAdapter(exa_config)


if __name__ == "__main__":
    # 测试
    import asyncio
    
    async def test():
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            print("Please set EXA_API_KEY environment variable")
            return
        
        config = EXASearchConfig(
            api_key=api_key,
            search_type="neural",
            num_results=10
        )
        
        adapter = EXAAdapter(config)
        
        print("Testing EXA discover...")
        results = await adapter.discover(
            "Transformer architectures for medical image segmentation",
            num_results=5
        )
        
        print(f"Found {len(results)} papers:")
        for p in results:
            print(f"  - {p['title']} (Score: {p['exa_score']:.3f})")
    
    asyncio.run(test())
