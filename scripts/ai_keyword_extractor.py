#!/usr/bin/env python3
"""
AI驱动的双语关键词提取器

特点：
- 使用LLM智能提取中英文关键词
- 自动识别学科领域
- 生成多数据库检索表达式
- 支持同义词扩展
"""

import json
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DomainType(Enum):
    """学科领域类型"""
    MEDICAL = "medical"
    COMPUTER_SCIENCE = "computer_science"
    ENGINEERING = "engineering"
    SOCIAL_SCIENCE = "social_science"
    NATURAL_SCIENCE = "natural_science"
    ARTS_HUMANITIES = "arts_humanities"
    INTERDISCIPLINARY = "interdisciplinary"
    UNKNOWN = "unknown"


@dataclass
class KeywordSet:
    """关键词集合"""
    primary: List[str]
    synonyms: List[str]
    related: List[str]
    abbreviations: List[str]


@dataclass
class BilingualKeywords:
    """双语关键词"""
    zh: KeywordSet
    en: KeywordSet
    domain: str
    confidence: float


@dataclass
class SearchQuery:
    """检索表达式"""
    database: str
    query: str
    filters: Dict[str, Any]


@dataclass
class KeywordExtractionResult:
    """关键词提取结果"""
    original_query: str
    core_concepts: Dict[str, str]
    keywords: BilingualKeywords
    search_queries: List[SearchQuery]
    suggested_databases: List[str]
    year_range: Dict[str, int]
    recommendations: List[str]


class AIKeywordExtractor:
    """
    AI驱动的关键词提取器
    
    使用LLM进行智能分析和关键词提取
    """
    
    # 系统提示词：关键词提取专家
    SYSTEM_PROMPT_KEYWORDS = """You are an expert academic research assistant specializing in keyword extraction and search strategy design.

Your task is to analyze a research topic and extract relevant keywords for literature search.

## Guidelines:
1. Identify the core concepts, methods, objects, and domains in the research topic
2. Generate BOTH English and Chinese keywords (if the topic contains Chinese)
3. Provide synonyms, related terms, and abbreviations for each keyword
4. Consider academic terminology and field-specific language
5. Order keywords by importance/relevance

## Output Format:
Return a JSON object with this structure:
{
    "domain_analysis": {
        "primary_domain": "main field (medical/cs/engineering/social_science/etc)",
        "sub_domains": ["subfield1", "subfield2"],
        "is_medical": boolean,
        "is_cs": boolean,
        "is_engineering": boolean,
        "is_chinese_topic": boolean
    },
    "core_concepts": {
        "topic": "research topic",
        "method": "research method",
        "object": "research object",
        "domain": "application domain"
    },
    "keywords": {
        "en": {
            "primary": ["keyword1", "keyword2", "keyword3"],
            "synonyms": ["synonym1", "synonym2"],
            "related": ["related_term1", "related_term2"],
            "abbreviations": ["abbr1", "abbr2"]
        },
        "zh": {
            "primary": ["关键词1", "关键词2"],
            "synonyms": ["同义词1", "同义词2"],
            "related": ["相关词1"],
            "abbreviations": ["缩写1"]
        }
    },
    "recommended_databases": ["semantic_scholar", "cnki", "pubmed", ...],
    "year_range": {"start": 2020, "end": 2024},
    "search_tips": ["tip1", "tip2"]
}

## Important:
- Primary keywords: 5-8 most important terms
- Synonyms: 2-3 per primary keyword
- Use academic terminology
- Consider both broad and specific terms
- Include methodological terms when relevant"""

    # 系统提示词：检索表达式生成
    SYSTEM_PROMPT_QUERIES = """You are an expert in academic database search syntax.

Generate search queries for different academic databases based on the provided keywords.

## Database-Specific Syntax:

### Semantic Scholar:
- Use natural language with quotes for phrases
- Combine with AND/OR
- Example: ("deep learning" OR "neural network") AND ("medical imaging")

### PubMed:
- Use [Title/Abstract] field tags
- Use MeSH terms when available
- Example: ("deep learning"[Title/Abstract]) AND ("diagnosis"[Title/Abstract])

### CNKI (中国知网):
- Use field codes: SU=主题, TI=篇名, KY=关键词
- Use + for OR, * for AND
- Example: SU=('深度学习'+'神经网络')*('医学影像')

### arXiv:
- Use field prefixes: ti=title, au=author, abs=abstract
- Use cat: for category
- Example: cat:cs.CV AND (ti:deep OR abs:neural)

### IEEE Xplore:
- Use parentheses for grouping
- Example: (("deep learning") AND "medical imaging")

## Output Format:
{
    "queries": [
        {
            "database": "semantic_scholar",
            "query": "search expression",
            "filters": {"year_range": [2020, 2024], "fields": ["computer_science", "medicine"]},
            "priority": 1
        }
    ],
    "explanation": "brief explanation of the search strategy"
}

## Rules:
- Generate queries for all relevant databases
- Use appropriate boolean operators
- Include year filters when specified
- Prioritize precision over recall"""

    def __init__(self, llm_client=None):
        """
        初始化提取器
        
        Args:
            llm_client: LLM客户端，如OpenAI或Anthropic的客户端
        """
        self.llm = llm_client
        self.domain_keywords = {
            DomainType.MEDICAL: [
                "clinical", "patient", "treatment", "diagnosis", "disease",
                "therapy", "medical", "health", "hospital", "drug"
            ],
            DomainType.COMPUTER_SCIENCE: [
                "algorithm", "neural", "network", "deep learning", "machine learning",
                "artificial intelligence", "model", "data", "prediction", "classification"
            ],
            DomainType.ENGINEERING: [
                "system", "design", "performance", "control", "optimization",
                "simulation", "experiment", "test", "measurement"
            ],
            DomainType.SOCIAL_SCIENCE: [
                "survey", "interview", "policy", "social", "behavior",
                "attitude", "perception", "culture", "economic"
            ]
        }
    
    async def extract(self, 
                      query: str, 
                      year_range: Optional[tuple] = None,
                      target_language: str = "both") -> KeywordExtractionResult:
        """
        提取关键词
        
        Args:
            query: 研究主题/标题
            year_range: (开始年份, 结束年份)，如 (2020, 2024)
            target_language: 目标语言 (zh/en/both)
        
        Returns:
            KeywordExtractionResult对象
        """
        # 构建提示
        user_prompt = f"""Research Topic: {query}

Target Language: {target_language}
{f"Year Range: {year_range[0]}-{year_range[1]}" if year_range else ""}

Please analyze this topic and extract keywords following the specified format."""

        # 调用LLM提取关键词
        response = await self._call_llm(
            system_prompt=self.SYSTEM_PROMPT_KEYWORDS,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        # 解析JSON响应
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # 如果LLM返回的不是纯JSON，尝试提取JSON部分
            data = self._extract_json_from_text(response)
        
        # 构建结果对象
        keywords = BilingualKeywords(
            zh=KeywordSet(**data["keywords"]["zh"]),
            en=KeywordSet(**data["keywords"]["en"]),
            domain=data["domain_analysis"]["primary_domain"],
            confidence=0.85  # 可由LLM评估
        )
        
        # 生成检索表达式
        search_queries = await self._generate_search_queries(
            keywords, year_range, data.get("recommended_databases", [])
        )
        
        return KeywordExtractionResult(
            original_query=query,
            core_concepts=data["core_concepts"],
            keywords=keywords,
            search_queries=search_queries,
            suggested_databases=data.get("recommended_databases", []),
            year_range={"start": year_range[0] if year_range else 2020, 
                       "end": year_range[1] if year_range else 2024},
            recommendations=data.get("search_tips", [])
        )
    
    async def _generate_search_queries(self, 
                                       keywords: BilingualKeywords,
                                       year_range: Optional[tuple],
                                       databases: List[str]) -> List[SearchQuery]:
        """生成各数据库的检索表达式"""
        
        user_prompt = f"""Keywords:
- English Primary: {', '.join(keywords.en.primary)}
- English Synonyms: {', '.join(keywords.en.synonyms)}
- Chinese Primary: {', '.join(keywords.zh.primary)}
- Chinese Synonyms: {', '.join(keywords.zh.synonyms)}

Target Databases: {', '.join(databases)}
{f"Year Range: {year_range[0]}-{year_range[1]}" if year_range else ""}

Generate search queries for each database."""

        response = await self._call_llm(
            system_prompt=self.SYSTEM_PROMPT_QUERIES,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=1500
        )
        
        try:
            data = json.loads(response)
            queries = []
            for q in data.get("queries", []):
                queries.append(SearchQuery(
                    database=q["database"],
                    query=q["query"],
                    filters=q.get("filters", {})
                ))
            return queries
        except (json.JSONDecodeError, KeyError):
            # 如果解析失败，使用备用方案生成基础查询
            return self._generate_fallback_queries(keywords, year_range, databases)
    
    def _generate_fallback_queries(self, keywords, year_range, databases) -> List[SearchQuery]:
        """备用查询生成方案"""
        queries = []
        
        # Semantic Scholar 查询
        if "semantic_scholar" in databases:
            en_terms = ' OR '.join([f'"{k}"' for k in keywords.en.primary[:3]])
            query = f"({en_terms})"
            if year_range:
                query += f" year:{year_range[0]}-{year_range[1]}"
            queries.append(SearchQuery("semantic_scholar", query, {}))
        
        # CNKI 查询
        if "cnki" in databases:
            zh_terms = '+'.join(keywords.zh.primary[:3])
            query = f"SU=({zh_terms})"
            queries.append(SearchQuery("cnki", query, {}))
        
        # PubMed 查询
        if "pubmed" in databases:
            terms = ' OR '.join([f'"{k}"[Title/Abstract]' for k in keywords.en.primary[:3]])
            query = f"({terms})"
            queries.append(SearchQuery("pubmed", query, {}))
        
        return queries
    
    async def _call_llm(self, system_prompt: str, user_prompt: str, 
                        temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """调用LLM"""
        if self.llm is None:
            # 如果没有提供LLM客户端，返回模拟数据（用于测试）
            return self._mock_llm_response(user_prompt)
        
        # 实际调用LLM
        # 这里需要根据具体的LLM客户端实现
        # 例如 OpenAI: await self.llm.chat.completions.create(...)
        # 或 Anthropic: await self.llm.messages.create(...)
        raise NotImplementedError("LLM client not implemented")
    
    def _mock_llm_response(self, prompt: str) -> str:
        """模拟LLM响应（用于测试）"""
        # 简单的关键词提取逻辑
        if "深度学习" in prompt or "deep learning" in prompt.lower():
            return json.dumps({
                "domain_analysis": {
                    "primary_domain": "computer_science",
                    "sub_domains": ["machine_learning", "medical_imaging"],
                    "is_medical": True,
                    "is_cs": True,
                    "is_engineering": False,
                    "is_chinese_topic": "深度学习" in prompt
                },
                "core_concepts": {
                    "topic": "深度学习在医学图像诊断中的应用",
                    "method": "卷积神经网络、深度学习算法",
                    "object": "医学图像、病灶检测",
                    "domain": "医疗诊断、计算机辅助诊断"
                },
                "keywords": {
                    "en": {
                        "primary": ["deep learning", "medical imaging", "diagnosis", "convolutional neural network", "image classification"],
                        "synonyms": ["deep neural network", "machine learning", "computer-aided diagnosis"],
                        "related": ["radiology", "pathology", "CT", "MRI", "X-ray"],
                        "abbreviations": ["DL", "CNN", "CAD"]
                    },
                    "zh": {
                        "primary": ["深度学习", "医学图像", "诊断", "卷积神经网络", "图像分类"],
                        "synonyms": ["深度神经网络", "机器学习", "计算机辅助诊断"],
                        "related": ["放射科", "病理学", "CT", "核磁共振"],
                        "abbreviations": ["深度学习", "CNN", "CAD"]
                    }
                },
                "recommended_databases": ["semantic_scholar", "pubmed", "cnki", "arxiv"],
                "year_range": {"start": 2020, "end": 2024},
                "search_tips": ["注意区分医学影像和病理图像", "关注最新的Transformer方法"]
            }, ensure_ascii=False)
        
        return json.dumps({
            "domain_analysis": {
                "primary_domain": "unknown",
                "is_chinese_topic": any('\u4e00' <= c <= '\u9fff' for c in prompt)
            },
            "core_concepts": {
                "topic": prompt[:50],
                "method": "",
                "object": "",
                "domain": ""
            },
            "keywords": {
                "en": {
                    "primary": ["research", "analysis"],
                    "synonyms": [],
                    "related": [],
                    "abbreviations": []
                },
                "zh": {
                    "primary": ["研究", "分析"],
                    "synonyms": [],
                    "related": [],
                    "abbreviations": []
                }
            },
            "recommended_databases": ["semantic_scholar"],
            "search_tips": []
        }, ensure_ascii=False)
    
    def _extract_json_from_text(self, text: str) -> Dict:
        """从文本中提取JSON"""
        import re
        # 尝试匹配 ```json ... ``` 或 ``` ... ```
        json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', text)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 尝试直接匹配 { ... }
        json_match = re.search(r'({[\s\S]*})', text)
        if json_match:
            return json.loads(json_match.group(1))
        
        raise ValueError("Could not extract JSON from LLM response")
    
    def detect_domain(self, query: str, keywords: List[str]) -> DomainType:
        """检测学科领域"""
        query_lower = query.lower()
        keyword_set = set(k.lower() for k in keywords)
        
        scores = {}
        for domain, indicators in self.domain_keywords.items():
            score = 0
            for indicator in indicators:
                if indicator in query_lower:
                    score += 2
                if indicator in keyword_set:
                    score += 1
            scores[domain] = score
        
        if scores:
            best_domain = max(scores, key=scores.get)
            if scores[best_domain] > 0:
                return best_domain
        
        return DomainType.UNKNOWN


# 便捷函数
async def extract_keywords(query: str, 
                           year_range: Optional[tuple] = None,
                           target_language: str = "both",
                           llm_client=None) -> KeywordExtractionResult:
    """
    便捷函数：提取关键词
    
    Args:
        query: 研究主题
        year_range: 年份范围元组 (start, end)
        target_language: 目标语言
        llm_client: LLM客户端实例
    
    Returns:
        KeywordExtractionResult
    """
    extractor = AIKeywordExtractor(llm_client)
    return await extractor.extract(query, year_range, target_language)


# 示例使用
if __name__ == "__main__":
    async def main():
        # 测试
        result = await extract_keywords(
            query="基于深度学习的医学图像诊断研究",
            year_range=(2020, 2024),
            target_language="both"
        )
        
        print(f"原始查询: {result.original_query}")
        print(f"\n学科领域: {result.keywords.domain}")
        print(f"\n英文关键词: {result.keywords.en.primary}")
        print(f"中文关键词: {result.keywords.zh.primary}")
        print(f"\n推荐数据库: {result.suggested_databases}")
        print(f"\n检索表达式:")
        for sq in result.search_queries:
            print(f"  {sq.database}: {sq.query}")
    
    asyncio.run(main())
