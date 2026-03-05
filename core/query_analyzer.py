#!/usr/bin/env python3
"""
LLM驱动的查询分析器

功能：
1. 自动识别研究领域
2. 智能分词和概念提取
3. 生成多语言同义词
4. 构建优化的检索表达式

使用LLM替代硬编码的TERM_MAPPINGS，实现自适应的关键词提取。
"""

import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ResearchDomain(Enum):
    """研究领域枚举"""
    COMPUTER_SCIENCE = "computer_science"
    MEDICINE = "medicine"
    ECONOMICS = "economics"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    SOCIAL_SCIENCE = "social_science"
    BIOLOGY = "biology"
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    UNKNOWN = "unknown"


@dataclass
class QueryAnalysisResult:
    """
    查询分析结果
    
    Attributes:
        original_query: 原始查询字符串
        domain: 识别的研究领域
        confidence: 领域识别置信度 (0-1)
        core_concepts: 核心概念列表
        keywords_zh: 中文关键词列表
        keywords_en: 英文关键词列表
        synonyms_zh: 中文同义词映射
        synonyms_en: 英文同义词映射
        search_queries: 各数据库检索表达式
        related_topics: 相关研究方向
        suggested_databases: 建议检索的数据库
    """
    original_query: str
    domain: ResearchDomain
    confidence: float
    core_concepts: List[Dict[str, Any]]
    keywords_zh: List[str]
    keywords_en: List[str]
    synonyms_zh: Dict[str, List[str]]
    synonyms_en: Dict[str, List[str]]
    search_queries: Dict[str, str]
    related_topics: List[str]
    suggested_databases: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        result['domain'] = self.domain.value
        return result


class LLMQueryAnalyzer:
    """
    LLM驱动的查询分析器
    
    使用LLM进行智能分析，替代硬编码的词表和规则。
    
    Example:
        analyzer = LLMQueryAnalyzer(llm_client)
        result = await analyzer.analyze(
            "基于深度学习的医学图像诊断研究",
            abstract="本研究探讨深度学习在医学图像分析中的应用..."
        )
        
        print(f"领域: {result.domain.value}")
        print(f"中文关键词: {result.keywords_zh}")
        print(f"英文关键词: {result.keywords_en}")
        print(f"CNKI检索式: {result.search_queries['cnki']}")
    """
    
    def __init__(self, llm_client, config: Optional[Dict] = None):
        """
        初始化查询分析器
        
        Args:
            llm_client: LLM客户端，需要支持 complete 方法
            config: 可选配置字典
        """
        self.llm = llm_client
        self.config = config or {}
    
    async def analyze(
        self, 
        query: str, 
        context: Optional[str] = None
    ) -> QueryAnalysisResult:
        """
        分析用户查询
        
        Args:
            query: 用户输入的研究主题/论文标题
            context: 额外上下文（如摘要、描述）
        
        Returns:
            QueryAnalysisResult: 完整的分析结果
        """
        # 步骤1: 使用LLM进行领域识别
        domain_result = await self._identify_domain(query, context)
        
        # 步骤2: 使用LLM提取核心概念
        concepts = await self._extract_concepts(query, context)
        
        # 步骤3: 使用LLM生成同义词
        synonyms = await self._generate_synonyms(
            concepts, 
            domain_result["domain"]
        )
        
        # 步骤4: 生成检索表达式
        queries = await self._build_search_queries(
            concepts, 
            synonyms,
            domain_result["domain"]
        )
        
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
    
    async def _identify_domain(
        self, 
        query: str, 
        context: Optional[str]
    ) -> Dict:
        """
        使用LLM识别研究领域
        
        Args:
            query: 研究主题
            context: 上下文
        
        Returns:
            {
                "domain": "领域名称",
                "confidence": 0.0-1.0,
                "subfield": "子领域",
                "reasoning": "识别理由",
                "suggested_databases": [...],
                "related_topics": [...]
            }
        """
        prompt = f"""你是一个学术研究领域分析专家。请分析给定的研究主题，识别其学科领域。

研究主题：{query}
{f"上下文：{context}" if context else ""}

可选领域：
- computer_science: 计算机科学（AI、软件工程、网络安全、数据科学等）
- medicine: 医学（临床医学、生物医学、公共卫生、药学等）
- economics: 经济学（金融、产业经济、国际贸易、计量经济等）
- education: 教育学（教育技术、课程设计、教育心理、高等教育等）
- engineering: 工程技术（电子、机械、土木、材料、化工等）
- social_science: 社会科学（社会学、政治学、心理学、管理学等）
- biology: 生物学（分子生物、生态学、遗传学、生物信息等）
- chemistry: 化学（有机化学、材料化学、分析化学等）
- physics: 物理学（理论物理、应用物理、凝聚态物理等）
- unknown: 未知或跨学科

请输出JSON格式：
{{
    "domain": "领域代码",
    "confidence": 0.0-1.0,
    "subfield": "具体子领域",
    "reasoning": "识别理由（2-3句话）",
    "suggested_databases": ["建议检索的数据库列表，如semantic_scholar, pubmed, cnki等"],
    "related_topics": ["相关的研究方向或关键词"]
}}"""
        
        response = await self.llm.complete(prompt)
        return json.loads(response)
    
    async def _extract_concepts(
        self, 
        query: str, 
        context: Optional[str]
    ) -> List[Dict]:
        """
        提取核心概念
        
        Args:
            query: 研究主题
            context: 上下文
        
        Returns:
            [
                {
                    "concept": "概念名称（中文）",
                    "concept_en": "英文翻译",
                    "type": "topic|method|object|domain",
                    "importance": 0.0-1.0
                }
            ]
        """
        prompt = f"""从以下研究主题中提取核心概念，包括：
- 研究主题 (topic): 核心研究问题或主题
- 研究方法 (method): 使用的方法、技术、算法
- 研究对象 (object): 研究对象、数据来源、实验材料
- 应用领域 (domain): 应用领域、场景

研究主题：{query}
{f"上下文：{context}" if context else ""}

要求：
1. 识别所有相关概念（3-8个）
2. 评估每个概念的重要性(0-1)
3. 提供中英文对照
4. 概念应该具体而非过于宽泛

输出JSON数组：
[
    {{
        "concept": "概念名称（中文）",
        "concept_en": "英文翻译",
        "type": "topic|method|object|domain",
        "importance": 0.0-1.0
    }}
]"""
        
        response = await self.llm.complete(prompt)
        return json.loads(response)
    
    async def _generate_synonyms(
        self, 
        concepts: List[Dict], 
        domain: str
    ) -> Dict:
        """
        生成同义词扩展
        
        Args:
            concepts: 核心概念列表
            domain: 研究领域
        
        Returns:
            {
                "zh_main": [主关键词],
                "en_main": [英文主关键词],
                "zh_expanded": {概念: [同义词]},
                "en_expanded": {concept: [synonyms]}
            }
        """
        concepts_str = ", ".join([c["concept"] for c in concepts])
        
        prompt = f"""为以下研究概念生成中英文同义词扩展（考虑{domain}领域）：

核心概念：{concepts_str}

扩展策略：
1. 同义词：意义相近的术语
2. 缩写形式：领域内常用缩写（如CNN、NLP）
3. 相关术语：经常同时出现的概念
4. 上下位词：更广泛或更具体的概念

要求：
- 每个概念提供2-4个同义词/近义词
- 包括中英文对照
- 保持术语的学术规范性
- 避免过于宽泛的词汇

输出JSON格式：
{{
    "zh_main": ["中文主关键词（2-4个核心词）"],
    "en_main": ["english main keywords (2-4 core terms)"],
    "zh_expanded": {{
        "概念1": ["同义词1", "同义词2", "缩写"],
        "概念2": ["同义词1", "同义词2"]
    }},
    "en_expanded": {{
        "concept1": ["synonym1", "synonym2", "abbreviation"],
        "concept2": ["synonym1", "synonym2"]
    }}
}}"""
        
        response = await self.llm.complete(prompt)
        return json.loads(response)
    
    async def _build_search_queries(
        self, 
        concepts: List[Dict],
        synonyms: Dict,
        domain: str
    ) -> Dict[str, str]:
        """
        构建检索表达式
        
        为不同数据库生成优化的检索式
        
        Args:
            concepts: 核心概念
            synonyms: 同义词映射
            domain: 研究领域
        
        Returns:
            {
                "cnki": "CNKI检索式",
                "pubmed": "PubMed检索式",
                "semantic_scholar": "Semantic Scholar检索式",
                "arxiv": "arXiv检索式",
                "exa": "EXA自然语言查询"
            }
        """
        concepts_json = json.dumps(concepts, ensure_ascii=False, indent=2)
        synonyms_json = json.dumps(synonyms, ensure_ascii=False, indent=2)
        
        prompt = f"""基于以下核心概念和同义词，为不同学术数据库生成检索表达式：

研究领域：{domain}

核心概念：
{concepts_json}

同义词扩展：
{synonyms_json}

数据库特定语法：

1. CNKI (中国知网):
   - 字段代码: SU=主题, TI=篇名, KY=关键词, TKA=篇关摘
   - 布尔逻辑: * = AND, + = OR, - = NOT
   - 示例: SU=('深度学习'+'神经网络')*('医学图像'+'影像诊断')

2. PubMed:
   - 字段标签: [Title/Abstract], [MeSH Terms], [Publication Type]
   - 布尔逻辑: AND, OR, NOT
   - 示例: ("deep learning"[Title/Abstract] OR "neural network"[Title/Abstract]) AND ("medical imaging"[Title/Abstract])

3. Semantic Scholar:
   - 自然语言风格，支持布尔逻辑
   - 示例: ("deep learning" OR "neural network") AND ("medical imaging" OR "clinical imaging")

4. arXiv:
   - 字段前缀: ti=标题, au=作者, abs=摘要, cat=类别
   - 布尔逻辑: AND, OR, ANDNOT
   - 示例: (ti:deep OR abs:learning) AND (cat:cs.CV OR cat:cs.LG)

5. EXA:
   - 自然语言查询，无需布尔逻辑
   - 示例: Recent advances in deep learning for medical image analysis and diagnosis

输出JSON格式：
{{
    "cnki": "CNKI检索表达式",
    "pubmed": "PubMed检索表达式",
    "semantic_scholar": "Semantic Scholar检索表达式",
    "arxiv": "arXiv检索表达式",
    "exa": "EXA自然语言查询"
}}"""
        
        response = await self.llm.complete(prompt)
        return json.loads(response)


# 便捷函数
async def analyze_research_topic(
    llm_client,
    query: str,
    context: Optional[str] = None
) -> QueryAnalysisResult:
    """
    便捷函数：分析研究主题
    
    Args:
        llm_client: LLM客户端
        query: 研究主题
        context: 上下文
    
    Returns:
        QueryAnalysisResult
    """
    analyzer = LLMQueryAnalyzer(llm_client)
    return await analyzer.analyze(query, context)


if __name__ == "__main__":
    # 测试示例
    import asyncio
    
    # 模拟LLM客户端
    class MockLLMClient:
        async def complete(self, prompt: str, **kwargs) -> str:
            # 这里应该调用真实的LLM API
            # 为了测试，返回模拟响应
            if "identify" in prompt.lower() or "领域" in prompt:
                return json.dumps({
                    "domain": "computer_science",
                    "confidence": 0.95,
                    "subfield": "Medical Image Analysis",
                    "reasoning": "主题涉及深度学习和医学图像，属于计算机视觉在医学领域的应用",
                    "suggested_databases": ["semantic_scholar", "pubmed", "arxiv", "cnki"],
                    "related_topics": ["computer vision", "healthcare AI", "diagnostic imaging"]
                })
            elif "concept" in prompt.lower() or "概念" in prompt:
                return json.dumps([
                    {"concept": "深度学习", "concept_en": "deep learning", "type": "method", "importance": 0.95},
                    {"concept": "医学图像", "concept_en": "medical imaging", "type": "object", "importance": 0.9},
                    {"concept": "诊断", "concept_en": "diagnosis", "type": "domain", "importance": 0.85}
                ])
            elif "synonym" in prompt.lower() or "同义词" in prompt:
                return json.dumps({
                    "zh_main": ["深度学习", "医学图像", "诊断"],
                    "en_main": ["deep learning", "medical imaging", "diagnosis"],
                    "zh_expanded": {
                        "深度学习": ["深度神经网络", "DNN", "深层学习"],
                        "医学图像": ["医学影像", "医疗图像", "临床图像"],
                        "诊断": ["检测", "筛查", "识别"]
                    },
                    "en_expanded": {
                        "deep learning": ["deep neural network", "DNN", "representation learning"],
                        "medical imaging": ["clinical imaging", "medical image analysis", "radiology"],
                        "diagnosis": ["detection", "screening", "identification"]
                    }
                })
            else:
                return json.dumps({
                    "cnki": "SU=('深度学习'+'深度神经网络')*('医学图像'+'医学影像')*('诊断'+'检测')",
                    "pubmed": "(\"deep learning\"[Title/Abstract] OR \"deep neural network\"[Title/Abstract]) AND (\"medical imaging\"[Title/Abstract] OR \"radiology\"[Title/Abstract]) AND (\"diagnosis\"[Title/Abstract] OR \"detection\"[Title/Abstract])",
                    "semantic_scholar": "(\"deep learning\" OR \"deep neural network\") AND (\"medical imaging\" OR \"radiology\") AND (\"diagnosis\" OR \"detection\")",
                    "arxiv": "(ti:deep OR abs:learning) AND (ti:medical OR abs:imaging) AND (ti:diagnosis OR abs:detection)",
                    "exa": "Recent advances in deep learning for medical image analysis and computer-aided diagnosis"
                })
    
    async def test():
        client = MockLLMClient()
        analyzer = LLMQueryAnalyzer(client)
        
        result = await analyzer.analyze(
            "基于深度学习的医学图像诊断研究",
            "本研究探讨深度学习在医学图像分析中的应用..."
        )
        
        print("Query Analysis Result:")
        print(f"  Domain: {result.domain.value} (confidence: {result.confidence})")
        print(f"  Keywords (ZH): {result.keywords_zh}")
        print(f"  Keywords (EN): {result.keywords_en}")
        print(f"  Suggested DBs: {result.suggested_databases}")
        print("\nSearch Queries:")
        for db, query in result.search_queries.items():
            print(f"  {db}: {query[:80]}...")
    
    asyncio.run(test())
