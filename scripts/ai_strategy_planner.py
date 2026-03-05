#!/usr/bin/env python3
"""
AI策略规划器 - AI驱动的工作流决策

特点：
- 自动识别研究领域
- 智能选择数据库
- 动态调整检索策略
- 自适应质量阈值
"""

import json
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ResearchDomain(Enum):
    """研究领域"""
    MEDICAL = "medical"
    COMPUTER_SCIENCE = "computer_science"
    ENGINEERING = "engineering"
    SOCIAL_SCIENCE = "social_science"
    NATURAL_SCIENCE = "natural_science"
    ARTS_HUMANITIES = "arts_humanities"
    BUSINESS = "business"
    EDUCATION = "education"
    INTERDISCIPLINARY = "interdisciplinary"
    UNKNOWN = "unknown"


@dataclass
class DatabaseSelection:
    """数据库选择"""
    name: str
    priority: int
    reason: str
    enabled: bool = True


@dataclass
class SearchStrategy:
    """检索策略"""
    field_selection: str
    boolean_logic: str
    year_range: Tuple[int, int]
    quality_threshold: Dict[str, Any]
    expected_results: int


@dataclass
class StrategyPlan:
    """策略计划"""
    domain_analysis: Dict[str, Any]
    selected_databases: List[DatabaseSelection]
    excluded_databases: List[DatabaseSelection]
    search_strategy: SearchStrategy
    recommendations: List[str]
    confidence: float


class AIStrategyPlanner:
    """
    AI策略规划器
    
    使用LLM分析研究主题，制定最优检索策略
    """
    
    SYSTEM_PROMPT = """You are an expert academic research strategist specializing in literature review methodology.

Your task is to analyze a research topic and create an optimal search strategy for literature review.

## Analysis Framework:

1. **Domain Identification**
   - Identify the primary academic discipline
   - Recognize interdisciplinary aspects
   - Determine if the topic is China-specific

2. **Database Selection Criteria**
   - Coverage: Does the database cover this field?
   - Quality: Does it index high-quality sources?
   - Language: Does it support needed languages?
   - Recency: Does it include recent publications?

3. **Search Strategy Design**
   - Field selection: Which fields to search (title/abstract/keywords)?
   - Boolean logic: How to combine terms?
   - Quality filters: Citation thresholds, journal tiers
   - Temporal scope: Appropriate year range

## Available Databases:

- **semantic_scholar**: Broad coverage, free, AI-powered (Priority: 1)
- **exa**: Neural search, high relevance (Priority: 1)
- **cnki**: Chinese literature, essential for China topics (Priority: 2)
- **pubmed**: Medical/biomedical, required for health topics (Priority: 1)
- **arxiv**: CS/physics preprints, latest research (Priority: 2)
- **ieee**: Engineering, technology (Priority: 2)
- **acm**: Computer science, software engineering (Priority: 2)
- **openalex**: Open academic graph, comprehensive (Priority: 2)

## Output Format (JSON):

```json
{
    "domain_analysis": {
        "primary_domain": "main field",
        "sub_domains": ["subfield1", "subfield2"],
        "is_medical": false,
        "is_computer_science": false,
        "is_engineering": false,
        "is_chinese_topic": false,
        "is_interdisciplinary": false,
        "confidence": 0.9
    },
    "database_selection": {
        "selected": [
            {
                "name": "database_name",
                "priority": 1,
                "reason": "why this database",
                "enabled": true
            }
        ],
        "excluded": [
            {
                "name": "database_name", 
                "reason": "why excluded"
            }
        ]
    },
    "search_strategy": {
        "field_selection": "title,abstract,keywords",
        "boolean_logic": "AND for concepts, OR for synonyms",
        "year_range": {"start": 2020, "end": 2024, "reason": "recent 5 years"},
        "quality_threshold": {
            "min_citations": 10,
            "journal_tiers": ["Q1", "Q2"],
            "prefer_oa": true
        },
        "expected_results": 50
    },
    "recommendations": [
        "Specific advice for this search",
        "Potential pitfalls to avoid"
    ]
}
```

## Decision Rules:

1. Medical topics (clinical, disease, patient, treatment) → MUST include PubMed
2. Computer Science (algorithm, AI, ML, neural) → MUST include arXiv and ACM
3. Engineering (system, design, performance) → MUST include IEEE
4. China-specific topics (Chinese concepts, domestic research) → MUST include CNKI
5. Interdisciplinary topics → Include multiple databases

Be precise in your analysis. Provide confidence scores for your recommendations."""

    def __init__(self, llm_client=None):
        """
        初始化策略规划器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm = llm_client
    
    async def plan(self, 
                   query: str,
                   year_range: Optional[Tuple[int, int]] = None,
                   num_papers: int = 50,
                   available_databases: Optional[List[str]] = None) -> StrategyPlan:
        """
        制定检索策略
        
        Args:
            query: 研究主题
            year_range: 年份范围
            num_papers: 期望文献数量
            available_databases: 可用数据库列表
        
        Returns:
            StrategyPlan对象
        """
        # 构建提示
        user_prompt = f"""Research Topic: {query}

{f"Preferred Year Range: {year_range[0]}-{year_range[1]}" if year_range else ""}
Target Number of Papers: {num_papers}
{f"Available Databases: {', '.join(available_databases)}" if available_databases else "All databases available"}

Please analyze this topic and create a comprehensive search strategy following the specified format."""

        # 调用LLM
        response = await self._call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=2500
        )
        
        # 解析JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = self._extract_json_from_text(response)
        
        # 构建结果
        domain_analysis = data.get("domain_analysis", {})
        
        selected_dbs = [
            DatabaseSelection(**db) 
            for db in data.get("database_selection", {}).get("selected", [])
        ]
        
        excluded_dbs = [
            DatabaseSelection(**db)
            for db in data.get("database_selection", {}).get("excluded", [])
        ]
        
        strategy_data = data.get("search_strategy", {})
        year_range_data = strategy_data.get("year_range", {})
        
        search_strategy = SearchStrategy(
            field_selection=strategy_data.get("field_selection", "title,abstract"),
            boolean_logic=strategy_data.get("boolean_logic", "AND for concepts"),
            year_range=(
                year_range_data.get("start", 2020),
                year_range_data.get("end", 2024)
            ),
            quality_threshold=strategy_data.get("quality_threshold", {}),
            expected_results=strategy_data.get("expected_results", num_papers)
        )
        
        return StrategyPlan(
            domain_analysis=domain_analysis,
            selected_databases=selected_dbs,
            excluded_databases=excluded_dbs,
            search_strategy=search_strategy,
            recommendations=data.get("recommendations", []),
            confidence=domain_analysis.get("confidence", 0.8)
        )
    
    async def adapt_strategy(self, 
                             current_plan: StrategyPlan,
                             search_results: List[Dict],
                             iteration: int = 1) -> StrategyPlan:
        """
        根据初步结果调整策略
        
        Args:
            current_plan: 当前策略计划
            search_results: 初步搜索结果
            iteration: 迭代次数
        
        Returns:
            调整后的策略计划
        """
        # 分析初步结果
        analysis = self._analyze_results(search_results)
        
        user_prompt = f"""Current Strategy Plan:
- Selected Databases: {[db.name for db in current_plan.selected_databases]}
- Expected Results: {current_plan.search_strategy.expected_results}
- Current Iteration: {iteration}

Search Results Analysis:
- Total Results: {analysis['total']}
- Quality Score: {analysis['quality_score']:.2f}
- Coverage Score: {analysis['coverage_score']:.2f}
- Language Distribution: {analysis['language_dist']}
- Year Distribution: {analysis['year_dist']}

Issues Identified:
{chr(10).join(analysis['issues'])}

Please adjust the search strategy based on these results. Return updated strategy in the same JSON format."""

        response = await self._call_llm(
            system_prompt=self.SYSTEM_PROMPT + "\n\n## Additional Context:\nYou are now ADJUSTING an existing strategy based on preliminary results. Focus on:\n1. Expanding search if results are insufficient\n2. Tightening filters if results are too many/low quality\n3. Adding/removing databases based on coverage gaps\n4. Adjusting year range based on publication trends",
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = self._extract_json_from_text(response)
        
        # 更新计划
        # ... (类似plan方法的处理)
        return current_plan  # 简化处理
    
    def _analyze_results(self, results: List[Dict]) -> Dict:
        """分析搜索结果"""
        total = len(results)
        
        # 质量评分（基于引用数、期刊等级等）
        quality_scores = []
        for r in results:
            score = 0
            if r.get("citation_count", 0) > 10:
                score += 0.3
            if r.get("is_oa"):
                score += 0.2
            if r.get("journal_tier") in ["Q1", "顶会"]:
                score += 0.5
            quality_scores.append(score)
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 语言分布
        lang_dist = {}
        for r in results:
            lang = r.get("language", "unknown")
            lang_dist[lang] = lang_dist.get(lang, 0) + 1
        
        # 年份分布
        year_dist = {}
        for r in results:
            year = r.get("year")
            if year:
                year_dist[year] = year_dist.get(year, 0) + 1
        
        # 识别问题
        issues = []
        if total < 20:
            issues.append("Too few results, need to expand search")
        elif total > 200:
            issues.append("Too many results, need to tighten filters")
        
        if avg_quality < 0.5:
            issues.append("Low quality results, need better filters")
        
        cn_ratio = lang_dist.get("zh", 0) / total if total > 0 else 0
        if cn_ratio < 0.2 and any(ord(c) > 127 for c in str(results)):
            issues.append("Insufficient Chinese literature, consider adding CNKI")
        
        return {
            "total": total,
            "quality_score": avg_quality,
            "coverage_score": min(total / 50, 1.0),  # 期望50篇
            "language_dist": lang_dist,
            "year_dist": year_dist,
            "issues": issues
        }
    
    async def _call_llm(self, system_prompt: str, user_prompt: str,
                        temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """调用LLM"""
        if self.llm is None:
            return self._mock_llm_response(user_prompt)
        
        raise NotImplementedError("LLM client not implemented")
    
    def _mock_llm_response(self, prompt: str) -> str:
        """模拟LLM响应"""
        # 根据提示内容返回模拟数据
        if "医学" in prompt or "medical" in prompt.lower():
            return json.dumps({
                "domain_analysis": {
                    "primary_domain": "medical",
                    "sub_domains": ["medical_imaging", "diagnosis", "computer_aided_diagnosis"],
                    "is_medical": True,
                    "is_computer_science": True,
                    "is_engineering": False,
                    "is_chinese_topic": "医学" in prompt,
                    "is_interdisciplinary": True,
                    "confidence": 0.92
                },
                "database_selection": {
                    "selected": [
                        {"name": "semantic_scholar", "priority": 1, "reason": "Broad coverage of medical AI literature", "enabled": True},
                        {"name": "pubmed", "priority": 1, "reason": "Essential for medical topics", "enabled": True},
                        {"name": "exa", "priority": 1, "reason": "High relevance neural search", "enabled": True},
                        {"name": "cnki", "priority": 2, "reason": "For Chinese medical literature", "enabled": "医学" in prompt},
                        {"name": "arxiv", "priority": 3, "reason": "Latest preprints in medical AI", "enabled": True}
                    ],
                    "excluded": [
                        {"name": "ieee", "reason": "Less relevant for clinical applications"},
                        {"name": "acm", "reason": "Less relevant for clinical applications"}
                    ]
                },
                "search_strategy": {
                    "field_selection": "title,abstract,keywords",
                    "boolean_logic": "AND for core concepts, OR for synonyms",
                    "year_range": {"start": 2020, "end": 2024, "reason": "Focus on recent 5 years for rapidly evolving field"},
                    "quality_threshold": {
                        "min_citations": 10,
                        "journal_tiers": ["Q1", "Q2", "顶会"],
                        "prefer_oa": True
                    },
                    "expected_results": 50
                },
                "recommendations": [
                    "Focus on peer-reviewed journal articles over conference papers for medical topics",
                    "Pay attention to FDA/CFDA approvals for clinical applications",
                    "Consider both technical AI methods and clinical validation studies"
                ]
            }, ensure_ascii=False)
        
        # 默认响应
        return json.dumps({
            "domain_analysis": {
                "primary_domain": "interdisciplinary",
                "sub_domains": [],
                "is_medical": False,
                "is_computer_science": False,
                "is_chinese_topic": any(ord(c) > 127 for c in prompt),
                "confidence": 0.6
            },
            "database_selection": {
                "selected": [
                    {"name": "semantic_scholar", "priority": 1, "reason": "Broad coverage", "enabled": True},
                    {"name": "exa", "priority": 1, "reason": "High relevance", "enabled": True}
                ],
                "excluded": []
            },
            "search_strategy": {
                "field_selection": "title,abstract",
                "year_range": {"start": 2020, "end": 2024},
                "quality_threshold": {"min_citations": 10},
                "expected_results": 50
            },
            "recommendations": []
        }, ensure_ascii=False)
    
    def _extract_json_from_text(self, text: str) -> Dict:
        """从文本中提取JSON"""
        import re
        json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', text)
        if json_match:
            return json.loads(json_match.group(1))
        
        json_match = re.search(r'({[\s\S]*})', text)
        if json_match:
            return json.loads(json_match.group(1))
        
        raise ValueError("Could not extract JSON from response")


# 便捷函数
async def create_strategy(query: str,
                          year_range: Optional[Tuple[int, int]] = None,
                          num_papers: int = 50,
                          llm_client=None) -> StrategyPlan:
    """
    创建检索策略
    
    Args:
        query: 研究主题
        year_range: 年份范围
        num_papers: 期望文献数量
        llm_client: LLM客户端
    
    Returns:
        StrategyPlan
    """
    planner = AIStrategyPlanner(llm_client)
    return await planner.plan(query, year_range, num_papers)


if __name__ == "__main__":
    async def main():
        # 测试
        plan = await create_strategy(
            query="基于深度学习的医学图像诊断研究",
            year_range=(2020, 2024),
            num_papers=50
        )
        
        print(f"学科领域: {plan.domain_analysis.get('primary_domain')}")
        print(f"置信度: {plan.confidence}")
        print(f"\n选择的数据库:")
        for db in plan.selected_databases:
            print(f"  {db.name} (优先级{db.priority}): {db.reason}")
        print(f"\n检索策略:")
        print(f"  字段: {plan.search_strategy.field_selection}")
        print(f"  年份: {plan.search_strategy.year_range[0]}-{plan.search_strategy.year_range[1]}")
        print(f"  期望结果: {plan.search_strategy.expected_results}")
        print(f"\n建议:")
        for rec in plan.recommendations:
            print(f"  - {rec}")
    
    asyncio.run(main())
